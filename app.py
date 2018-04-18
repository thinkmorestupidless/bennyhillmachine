from boto.s3.key import Key
from flask import Flask, render_template, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from moviepy.video.io.VideoFileClip import VideoFileClip, AudioFileClip
from rq import Queue
from rq.job import Job
from worker import conn
import operator
import os
import json
import pafy
import time
import datetime
import boto

#################
# configuration #
#################

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db  = SQLAlchemy(app)

q = Queue(connection=conn)

audio = AudioFileClip("audio.m4a")
accel = 2.5

from models import *

##########
# helper #
##########

def download_and_convert(url):
	print('1', url, 'converting')
	source = pafy.new(url)
	best = source.getbest(preftype="mp4")
	ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
	input_filename = "/tmp/" + ts + "." + best.extension
	print('1b')
	best.download(filepath=input_filename)
	output = VideoFileClip(input_filename)
	duration = output.duration
	print('1c')
	output_filename="/tmp/" + best.title + "." + best.extension
	print('1d')
	output = output.set_audio(audio).fl_time(lambda t: t * accel, apply_to='mask').set_duration(duration / accel)
	print('1e')
	output.write_videofile(output_filename)

	print('2', url, 'uploading')

	s3 = boto.connect_s3()
	bucket = s3.get_bucket(os.environ['BUCKET_NAME'])
	key = Key(bucket)
	key.key = best.title + "-" + ts
	key.set_contents_from_filename(output_filename)

	output_url = key.generate_url(expires_in=3600)

	print('3', url, 'complete')

	# save the results
	try:
		result = Result(
			url=url,
			youtube_url=output_url
		)
		db.session.add(result)
		db.session.commit()
		return result.id
	except:
		errors.append("Unable to add item to database.")
		return {"error": errors}

##########
# routes #
##########

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def get_counts():
    # get url
    data = json.loads(request.data.decode())
    url = data["url"]
    # form URL, id necessary
    if 'https://' not in url[:8]:
        url = 'https://' + url
    # start job
    job = q.enqueue_call(
        func="app.download_and_convert", args=(url,), result_ttl=5000
    )
    # return created job id
    return job.get_id()

@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        return result.youtube_url#jsonify(result)
    else:
        return "Nay!", 202

@app.route('/<name>')
def hello_name(name):
	return "Hello {}!".format(name)

if __name__ == '__main__':
	app.run()	