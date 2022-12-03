from flask_login import current_user
from sqlalchemy import desc
import requests
import json
import os

from .models import *
from . import db, sp


def fetch_books(search_word):
    link = f'https://www.googleapis.com/books/v1/volumes?q={search_word}&key='
    link += os.environ.get("GOOGLE_BOOKS_API")
    response = requests.get(link)
    return response


def fetch_films(search_word):
    link = 'https://api.themoviedb.org/3/search/multi?api_key='
    link += os.environ.get("FILM_API")
    link += f'&query={search_word}'
    response = requests.get(link)
    return response


# input: JSON string of book from Google Books API
# output: informally defined item object
def book_to_item(json_string):
    item = {}

    # json_strings without ids should return None since they cannot be processed
    try:
        item['id'] = json_string['id']
    except:
        return None

    try:
        item['title'] = json_string['volumeInfo']['title']
    except:
        item['title'] = None

    try:
        item['authors'] = json_string['volumeInfo']['authors']
    except:
        item['authors'] = None

    try:
        item['image_link'] = json_string['volumeInfo']['imageLinks']['smallThumbnail'].replace(
            "&edge=curl", "")
    except:
        item['image_link'] = None

    item['type'] = 'book'

    return item


# input: JSON string of film from The Movie Database API
# output: informally defined item object
def film_to_item(json_string):
    item = {}

    # remove people from results
    try:
        if json_string['media_type'] == "person":
            return None
    except:
        pass

    # json_strings without ids should return None since they cannot be processed
    try:
        id = str(json_string['id'])
    except:
        return None

    # testing media_type == "movie"
    try:
        # if json_string has title field then media type is movie
        item['title'] = json_string['title']
    except:
        item['title'] = None  # try tv
    else:
        id = "movie/" + id

    # testing media_type == "tv"
    if not item['title']:
        try:
            # if json_string has name field then media type is tv
            item['title'] = json_string['name']
        except:
            pass
        else:
            id = "tv/" + id

    item['id'] = id
    item['authors'] = None

    try:
        item['image_link'] = 'https://image.tmdb.org/t/p/w200' + \
            json_string['poster_path']
    except:
        item['image_link'] = None

    item['type'] = 'film'

    return item


# input: JSON string of film from Spotify API
# output: informally defined item object
def music_to_item(json_string):
    item = {}

    try:
        item['id'] = json_string['id']
    except:
        return None

    try:
        item['title'] = json_string['name']
    except:
        item['title'] = None

    try:
        artists = []
        for artist in json_string['artists']:
            artists.append(artist['name'])
        item['authors'] = artists
    except:
        item['authors'] = None

    try:
        item['image_link'] = json_string['album']['images'][1]['url']
    except:
        item['image_link'] = None

    item['type'] = 'music'

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
                user = User.query.filter_by(id=r.user_A_id).first()
                data = json.loads(response.content)
                item = book_to_item(data)
                item['fname'] = user.firstname
                item['lname'] = user.lastname
                item['date'] = r.date
                books.append(item)
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
                user = User.query.filter_by(id=r.user_B_id).first()
                data = json.loads(response.content)
                item = book_to_item(data)
                item['fname'] = user.firstname
                item['lname'] = user.lastname
                item['date'] = r.date
                books.append(item)
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
            response = requests.get(
                f'{link}{r.film_id}?api_key={os.environ.get("FILM_API")}')
            if response.status_code == 200:
                user = User.query.filter_by(id=r.user_A_id).first()
                data = json.loads(response.content)
                item = film_to_item(data)
                item['fname'] = user.firstname
                item['lname'] = user.lastname
                item['date'] = r.date
                films.append(item)
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
            response = requests.get(
                f'{link}{r.film_id}?api_key={os.environ.get("FILM_API")}')
            if response.status_code == 200:
                user = User.query.filter_by(id=r.user_B_id).first()
                data = json.loads(response.content)
                item = film_to_item(data)
                item['fname'] = user.firstname
                item['lname'] = user.lastname
                item['date'] = r.date
                films.append(item)
    return films


# return music recommended to user
def music_rec_to_user():
    results = db.session.query(MusicRecommended)\
        .with_entities(MusicRecommended.music_id, MusicRecommended.user_A_id, MusicRecommended.date)\
        .filter(MusicRecommended.user_B_id == current_user.id)\
        .order_by(desc(MusicRecommended.date)).all()
    music = []
    if results:
        link = 'http://open.spotify.com/track/'
        for r in results:
            response = requests.get(f'{link}{r.music_id}')
            if response.status_code == 200:
                user = User.query.filter_by(id=r.user_A_id).first()
                data = json.loads(response.content)
                item = music_to_item(data)
                item['fname'] = user.firstname
                item['lname'] = user.lastname
                item['date'] = r.date
                music.append(item)
    return music


# return music recommended by user
def music_rec_by_user():
    results = db.session.query(MusicRecommended)\
        .with_entities(MusicRecommended.music_id, MusicRecommended.user_B_id, MusicRecommended.date)\
        .filter(MusicRecommended.user_A_id == current_user.id)\
        .order_by(desc(MusicRecommended.date)).all()
    music = []

    if results:
        for r in results:
            data = sp.track(r.music_id)
            if data:
                user = User.query.filter_by(id=r.user_B_id).first()
                item = music_to_item(data)
                item['fname'] = user.firstname
                item['lname'] = user.lastname
                item['date'] = r.date
                print(item)
                music.append(item)
            # response = requests.get(f'{link}{r.music_id}')
            # print(f'{link}{r.music_id}')
            # print(response.content)
            # if response.status_code == 200:
            #     user = User.query.filter_by(id=r.user_B_id).first()
            #     data = json.loads(response.content)
            #     item = music_to_item(data)
            #     item['fname'] = user.firstname
            #     item['lname'] = user.lastname
            #     item['date'] = r.date
            #     music.append(item)
    return music


# return user's followers
def followers():
    followers = db.session.query(Follower.user_A_id).filter(
        Follower.user_B_id == current_user.id).subquery()
    users = User.query.join(followers, User.id ==
                            followers.c.user_A_id).order_by(User.firstname)
    return users


# return user's following
def following():
    followers = db.session.query(Follower.user_B_id).filter(
        Follower.user_A_id == current_user.id).subquery()
    users = User.query.join(followers, User.id ==
                            followers.c.user_B_id).order_by(User.firstname)
    return users
