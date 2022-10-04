from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import json
import requests

from .models import *
from . import db
from . import creds

main = Blueprint('main', __name__)

@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/books')
@login_required
def books():
    # by default show books recomended to user
    book_ids = db.session.query(BooksRecomended.book_id).filter(BooksRecomended.user_B_id == current_user.id).all()
    books = []
    if book_ids:
        link = 'https://www.googleapis.com/books/v1/volumes/'
        for b in book_ids:
            response = requests.get(link + b.book_id)
            if response.status_code == 200:
                data = json.loads(response.content)
                books.append(data)

    return render_template('books.html', books=books)

@main.route('/books', methods=['POST'])
@login_required
def books_post():
    if request.form['recomended'] == "to user":
        book_ids = db.session.query(BooksRecomended.book_id).filter(BooksRecomended.user_B_id == current_user.id).all()
    elif request.form['recomended'] == "by user":
        book_ids = db.session.query(BooksRecomended.book_id).filter(BooksRecomended.user_A_id == current_user.id).all()
    books = [] 
    if book_ids:
        link = 'https://www.googleapis.com/books/v1/volumes/'
        for b in book_ids:
            response = requests.get(link + b.book_id)
            if response.status_code == 200:
                data = json.loads(response.content)
                books.append(data)
    return render_template('books.html', books=books)








@main.route('/books/search')
@login_required
def books_search():
    books = []
    if 'book' in request.args:
        search_word = request.args.get('book')
        link = 'https://www.googleapis.com/books/v1/volumes?q='
        link += search_word
        link += '&key='
        link += creds.google_books_api
        response = requests.get(link)
        data = json.loads(response.content)
        books = data['items']
    return render_template('dev_book_search.html', books=books)

@main.route('/books/recomend')
@login_required
def books_recomend():
    pass

@main.route('/followers')
@login_required
def show_followers():
    followers = db.session.query(Follower.user_A_id).filter(Follower.user_B_id == current_user.id).subquery()
    users = User.query.join(followers, User.id == followers.c.user_A_id)
    return render_template('followers.html', followers=users)

@main.route('/following')
@login_required
def show_following():
    followers = db.session.query(Follower.user_B_id).filter(Follower.user_A_id == current_user.id).subquery()
    users = User.query.join(followers, User.id == followers.c.user_B_id)
    return render_template('following.html', following=users)

@main.route('/follow_new', methods=['POST'])
@login_required
def follow_new():
    email = request.form.get('email')
    # Check if email address is registered
    user_exists = User.query.filter_by(email = email).first()
    if not user_exists:
        flash('This email address is not registered.', 'danger')
        return redirect(url_for('main.show_following'))

    # Check if already following exists
    followers = db.session.query(Follower.user_B_id).filter(Follower.user_A_id == current_user.id).subquery()
    user_followers = User.query.join(followers, User.id == followers.c.user_B_id).subquery()
    user = User.query.filter(user_followers.c.email == email).first()
        
    if user:
        flash('You are already following this person.', 'danger')
    else:
        new_following = Follower(user_A_id = current_user.id, user_B_id = user_exists.id)
        db.session.add(new_following)
        db.session.commit()
        flash('New follower successfully added!', 'success')

    return redirect(url_for('main.show_following'))


