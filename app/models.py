from flask_login import UserMixin
from .extentions import db
import datetime

"""
COMMANDS TO UPDATE DB WITH NEW TABLE
1. cd RecommendationApp
2. open python terminal (>>>python)
3. >>>from app import models, db, create_app
4. >>>create_all(app=create_app())
"""


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)


class Follower(db.Model):
    # A follows B
    id = db.Column(db.Integer, primary_key=True)
    user_A_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_B_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class BooksRecommended(db.Model):
    # A recommended book to B
    # B must follow A
    id = db.Column(db.Integer, primary_key=True)
    user_A_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_B_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.String(12), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class FilmsRecommended(db.Model):
    # A recommended film to B
    # B must follow A
    id = db.Column(db.Integer, primary_key=True)
    user_A_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_B_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    film_id = db.Column(db.String(12), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class MusicRecommended(db.Model):
    # A recommended music track to B
    # B must follow A
    id = db.Column(db.Integer, primary_key=True)
    user_A_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_B_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    music_id = db.Column(db.String(12), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class PodcastsRecommended(db.Model):
    # A recommended podcast to B
    # B must follow A
    id = db.Column(db.Integer, primary_key=True)
    user_A_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_B_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    podcast_id = db.Column(db.String(12), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
