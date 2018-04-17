from app import db
from sqlalchemy.dialects.postgresql import JSON


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    youtube_url = db.Column(db.String())
    url = db.Column(db.String())

    def __init__(self, url, youtube_url):
        self.url = url
        self.youtube_url = youtube_url

    def __repr__(self):
        return '<id {}>'.format(self.id)