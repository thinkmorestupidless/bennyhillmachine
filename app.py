from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
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
import logging
import boto3
import botocore.session
from botocore.exceptions import ClientError
from botocore.client import Config


#################
# configuration #
#################

app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)
db  = SQLAlchemy(app)

q = Queue(connection=conn)

audio = AudioFileClip("audio.m4a")
accel = 2.5

from models import *

##########
# helper #
##########

def download_and_convert(url):
	print("converting url " + url)
	pafy.set_api_key(app.config.get('YOUTUBE_API_KEY'))

	source = pafy.new(url)

	best = source.getbest(preftype="mp4")
	ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
	input_filename = "/tmp/" + ts + "." + best.extension

	try:
	    best.download(filepath=input_filename)
	except:
	    return {"error": "Download failed."}

	output = VideoFileClip(input_filename)
	duration = output.duration

	output_filename=best.title + '-' + ts + '.' + best.extension
	output_filepath="/tmp/" + output_filename

	output = output.set_audio(audio).fl_time(lambda t: t * accel, apply_to='mask').set_duration(duration / accel)
	output.write_videofile(output_filepath)

	print("uploading to s3")

	output_url = upload_file(output_filepath, 'bennyhillmachine', output_filename)

	print("conversion complete")

	# save the results
	try:
		row = ConvertedVideo(
			youtube_url=output_url
		)
		db.session.add(row)
		db.session.commit()
		return row.id
	except:
		return {"error": "Database update failed."}

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3',config=Config(signature_version='s3v4'))
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        return s3_client.generate_presigned_url('get_object', Params={'Bucket': 'bennyhillmachine', 'Key': object_name})
    except ClientError as e:
        logging.error(e)
        return False

##########
# routes #
##########

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def get_counts():
    from app import download_and_convert
    # get url
    data = json.loads(request.data.decode())
    url = data["url"]
    # form URL, id necessary
    if 'https://' not in url[:8]:
        url = 'https://' + url
    # start job
    job = q.enqueue_call(
        func=download_and_convert, args=(url,), result_ttl=5000
    )
    # return created job id
    return job.get_id()

@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = ConvertedVideo.query.filter_by(id=job.result).first()
        return result.youtube_url#jsonify(result)
    else:
        return "Nay!", 202

@app.route('/<name>')
def hello_name(name):
	return "Hello {}!".format(name)

if __name__ == '__main__':
	app.run()	
