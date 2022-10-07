from flask_login import current_user
import requests
import json

from .models import *
from . import db, creds

# return books recommended to user
def books_rec_to_user():
    results = db.session.query(BooksRecommended)\
        .with_entities(BooksRecommended.book_id, BooksRecommended.user_A_id, BooksRecommended.date)\
        .filter(BooksRecommended.user_B_id == current_user.id).all()
    books = []
    if results:
        link = 'https://www.googleapis.com/books/v1/volumes/'
        for r in results:
            response = requests.get(link + r.book_id)
            if response.status_code == 200:
                data = json.loads(response.content)
                user = User.query.filter_by(id=r.user_A_id).first()
                data['fname'] = user.firstname
                data['lname'] = user.lastname
                data['date'] = r.date
                books.append(data)
    return books

# return books recommended by user
def books_rec_by_user():
    results = db.session.query(BooksRecommended)\
        .with_entities(BooksRecommended.book_id, BooksRecommended.user_B_id, BooksRecommended.date)\
        .filter(BooksRecommended.user_A_id == current_user.id).all()
    books = []
    if results:
        link = 'https://www.googleapis.com/books/v1/volumes/'
        for r in results:
            response = requests.get(link + r.book_id)
            if response.status_code == 200:
                data = json.loads(response.content)
                user = User.query.filter_by(id=r.user_B_id).first()
                data['fname'] = user.firstname
                data['lname'] = user.lastname
                data['date'] = r.date
                books.append(data)
    return books

# return user's followers
def followers():
    followers = db.session.query(Follower.user_A_id).filter(Follower.user_B_id == current_user.id).subquery()
    users = User.query.join(followers, User.id == followers.c.user_A_id)
    return users

# return user's following
def following():
    followers = db.session.query(Follower.user_B_id).filter(Follower.user_A_id == current_user.id).subquery()
    users = User.query.join(followers, User.id == followers.c.user_B_id)
    return users