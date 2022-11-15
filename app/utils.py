from flask_login import current_user
from sqlalchemy import desc
import requests, json, os

from .models import *
from . import db

# fix books without authors or thumbnails
def books_complete(og_items):
    items = []
    for item in og_items:
        try: 
            item['volumeInfo']['imageLinks']['smallThumbnail']
        except: 
            item['volumeInfo']['imageLinks'] = {'smallThumbnail': 'none'}
        else: 
            # remove the page curl on image
            item['volumeInfo']['imageLinks']['smallThumbnail'] = \
                item['volumeInfo']['imageLinks']['smallThumbnail'].replace("&edge=curl", "")
        try: item['volumeInfo']['authors']
        except: item['volumeInfo'] = {'authors': None}
        items.append(item)
    return items

# def name_to_title(item):
#     if item['media_type'] == 'tv':
#         # correct for inconsitent naming movie vs tv
#         item['title'] = item['name']
#     return item

# correct for inconsitent naming movie vs tv
def name_to_title(item):
    try:
        # media_type = movie
        title = item['title']
    except:
        # media_type = tv
        title = item['name']
    item['title'] = title
    return item

# return books recommended to user
def books_rec_to_user():
    results = db.session.query(BooksRecommended)\
        .with_entities(BooksRecommended.book_id, BooksRecommended.user_A_id, BooksRecommended.date)\
        .filter(BooksRecommended.user_B_id == current_user.id)\
        .order_by(desc(BooksRecommended.date)).all()
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
        .filter(BooksRecommended.user_A_id == current_user.id)\
        .order_by(desc(BooksRecommended.date)).all()
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

# return films recommended to user
def films_rec_to_user():
    results = db.session.query(FilmsRecommended)\
        .with_entities(FilmsRecommended.film_id, FilmsRecommended.user_A_id, FilmsRecommended.date)\
        .filter(FilmsRecommended.user_B_id == current_user.id)\
        .order_by(desc(FilmsRecommended.date)).all()
    films = []
    if results:
        link = 'https://api.themoviedb.org/3/'
        for r in results:
            # by default try media_type = movie 
            response = requests.get(f'{link}{r.film_id}?api_key={os.environ.get("FILM_API")}')
            if response.status_code == 200:
                data = json.loads(response.content)
                user = User.query.filter_by(id=r.user_A_id).first()
                data['fname'] = user.firstname
                data['lname'] = user.lastname
                data['date'] = r.date
                films.append(data)
    return films

# return films recommended by user
def films_rec_by_user():
    results = db.session.query(FilmsRecommended)\
        .with_entities(FilmsRecommended.film_id, FilmsRecommended.user_B_id, FilmsRecommended.date)\
        .filter(FilmsRecommended.user_A_id == current_user.id)\
        .order_by(desc(FilmsRecommended.date)).all()
    films = []
    if results:
        link = 'https://api.themoviedb.org/3/'
        for r in results:
            # by default try media_type = movie 
            response = requests.get(f'{link}{r.film_id}?api_key={os.environ.get("FILM_API")}')
            if response.status_code == 200:
                data = json.loads(response.content)
                user = User.query.filter_by(id=r.user_B_id).first()
                data['fname'] = user.firstname
                data['lname'] = user.lastname
                data['date'] = r.date
                films.append(data)
    return films

# return user's followers
def followers():
    followers = db.session.query(Follower.user_A_id).filter(Follower.user_B_id == current_user.id).subquery()
    users = User.query.join(followers, User.id == followers.c.user_A_id).order_by(User.firstname)
    return users

# return user's following
def following():
    followers = db.session.query(Follower.user_B_id).filter(Follower.user_A_id == current_user.id).subquery()
    users = User.query.join(followers, User.id == followers.c.user_B_id).order_by(User.firstname)
    return users