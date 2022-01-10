from app import db
from sqlalchemy.dialects.postgresql import JSON


class ConvertedVideo(db.Model):
    __tablename__ = 'converted_videos'

    id = db.Column(db.Integer, primary_key=True)
    youtube_url = db.Column(db.String())
    converted_url = db.Column(db.String())
    status = db.Column(db.String())

    def __init__(self, youtube_url, status='Downloading'):
        self.youtube_url = youtube_url
        self.status = status

    def __repr__(self):
        return '<id {}, youtube_url {}, converted_url {}, status {}>'.format(self.id, self.youtube_url, self.converted_url, self.status)
