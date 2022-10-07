from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import json
import requests

from .models import *
from . import db, creds, utils

main = Blueprint('main', __name__)

@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/books')
@login_required
def books():
    # by default show books recommended to user
    books = utils.books_rec_to_user()
    return render_template('books.html', books=books, recs_to_user=True)

@main.route('/books', methods=['POST'])
@login_required
def books_post():
    if request.form['recommended'] == "to user":
        books = utils.books_rec_to_user()
        recs_to_user = True
    elif request.form['recommended'] == "by user":
        books = utils.books_rec_by_user()
        recs_to_user = False
    return render_template('books.html', books=books, recs_to_user=recs_to_user)

@main.route('/books/catalogue')
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
        if response.status_code == 200:
            data = json.loads(response.content)
            books = data['items']
    return render_template('book_catalogue.html', books=books)

@main.route('/books/recommend', methods=['POST'])
@login_required
def books_recommend():
    if request.form.get('recommend_new'):
        string = request.form.get('recommend_new')
        l = string.strip('][').split(',') # return string to list
        a = current_user.id
        b = int(l[0])
        book = l[1].strip(' ')
        new = BooksRecommended(user_A_id = a, user_B_id = b, book_id = book)
        db.session.add(new)
        db.session.commit()
        flash('You successfully recommended a new book!', 'success')
        return redirect(url_for('main.books'))

    elif request.form.get('recommend'):
        link = 'https://www.googleapis.com/books/v1/volumes/'
        link += request.form['recommend']
        response = requests.get(link)
        if response.status_code == 200:
            book = json.loads(response.content)
        followers = db.session.query(Follower.user_A_id).filter(Follower.user_B_id == current_user.id).subquery()
        users = User.query.join(followers, User.id == followers.c.user_A_id)
        return render_template('recommend.html', book = book, followers = users)

    else:
        flash('There was a problem with this request.', 'danger')
        return redirect(url_for('main.books'))

@main.route('/profile')
@login_required
def profile():
    # by default show following
    followers = db.session.query(Follower.user_B_id).filter(Follower.user_A_id == current_user.id).subquery()
    users = User.query.join(followers, User.id == followers.c.user_B_id)
    return render_template('profile.html', user=current_user, follow=users, followers=False)

@main.route('/profile', methods=['POST'])
@login_required
def profile_post():
    if request.form['show'] == "followers":
        followers = db.session.query(Follower.user_A_id).filter(Follower.user_B_id == current_user.id).subquery()
        users = User.query.join(followers, User.id == followers.c.user_A_id)
        return render_template('profile.html', user=current_user, follow=users, followers=True)
    elif request.form['show'] == "following":
        followers = db.session.query(Follower.user_B_id).filter(Follower.user_A_id == current_user.id).subquery()
        users = User.query.join(followers, User.id == followers.c.user_B_id)
        return render_template('profile.html', user=current_user, follow=users, followers=False)
    else:
        return redirect(url_for('main.profile'))

@main.route('/follow_new', methods=['POST'])
@login_required
def follow_new():
    email = request.form.get('email')
    
    # Check email not self
    if current_user.email == email:
        flash('You cannot follow yourself.', 'danger')
        return redirect(url_for('main.profile'))

    # Check if email address is registered
    user_exists = User.query.filter_by(email = email).first()
    if not user_exists:
        flash('This email address is not registered.', 'danger')
        return redirect(url_for('main.profile'))

    # Check if already following
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

    return redirect(url_for('main.profile'))


