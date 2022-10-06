from flask_login import UserMixin
from .extentions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

class Follower(db.Model):
    # A follows B
    id = db.Column(db.Integer, primary_key=True)
    user_A_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user_B_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

class BooksRecommended(db.Model):
    # A recommended book to B
    # B must follow A
    id = db.Column(db.Integer, primary_key=True)
    user_A_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user_B_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    book_id = db.Column(db.String(12), nullable = False)