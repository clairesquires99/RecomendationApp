import os, json, requests, yaml
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from .models import *
from . import db, sp, utils

# This file handles everything excluding the authentication (handeled by auth.py).
#   Each page has at least one function, if not several. 
#   The media types are determined by the variable 'item_type'.


main = Blueprint('main', __name__)

@main.route('/home')
@login_required
def home():
    return render_template('home.html')


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'GET':
        # by default show following
        users = utils.following()
        return render_template('profile.html', user=current_user, follow=users, followers=False)
    else:
        if request.form['show'] == "followers":
            users = utils.followers()
            return render_template('profile.html', user=current_user, follow=users, followers=True)
        elif request.form['show'] == "following":
            users = utils.following()
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


@main.route('/show/<item_type>', methods=['GET', 'POST'])
@login_required
def show(item_type):
    items = []        
    if request.method == 'GET':
        recs_to_user = True
        if item_type == 'books':
            items = utils.books_rec_to_user()
        elif item_type == 'films':
            items = utils.films_rec_to_user()
    else:
        if request.form['recommended'] == "to user":
            if item_type == 'books':
                items = utils.books_rec_to_user()
            elif item_type == 'films':
                items = utils.films_rec_to_user()
            recs_to_user = True
        elif request.form['recommended'] == "by user":
            if item_type == 'books':
                items = utils.books_rec_by_user()
            elif item_type == 'films':
                print("showing films rec by user")
                items = utils.films_rec_by_user()
            recs_to_user = False
    return render_template('show.html', item_type=item_type, items=items, recs_to_user=recs_to_user)


@main.route('/search/<item_type>')
@login_required
def search(item_type):
    items = []
    data = None # default

    # fetch response to search query from API
    if 'books' in request.args:
        search_word = request.args.get('books')
        response = utils.fetch_books(search_word)
        if response.status_code == 200:
            data = json.loads(response.content)
        else:
            pass # invalid response from API
        if data and int(data['totalItems']) > 0:
            json_strings = data['items']
            for jstring in json_strings:
                item = utils.book_to_item(jstring)
                if item: items.append(item)

    elif 'films' in request.args:
        search_word = request.args.get('films')
        response = utils.fetch_films(search_word)
        if response.status_code == 200:
            data = json.loads(response.content)
        else:
            pass # invalid response from API
        if data:
            json_strings = data['results']
            for jstring in json_strings:
                # print(jstring)
                item = utils.film_to_item(jstring)
                if item:  items.append(item)

    # elif 'music' in request.args:
    #     search_word = request.args.get('music')
    #     data = sp.search(q=search_word, type='track')
    #     items = data['tracks']['items']
    
   
    #     for r in items:
    #         name = r['name']
    #         artist = r['artists'][0]['name']
    #         id = r['id']
    #         try:
    #             print(r['album']['images'])
    #         except:
    #             print('no image')
    #         print()

    if request.args and (len(items) == 0):
        flash(f"We coulnd't find any results for your search, sorry!", 'success')

    return render_template('search.html', item_type=item_type, items=items)
    

@main.route('/recommend/<item_type>', methods=['POST'])
@login_required
def recommend(item_type):
    if request.form.get('recommend'):
        item = request.form['recommend']
        item = yaml.safe_load(item)

        followers = db.session.query(Follower.user_A_id).filter(Follower.user_B_id == current_user.id).subquery()
        users = User.query.join(followers, User.id == followers.c.user_A_id)

        return render_template('recommend.html', item_type=item_type, item=item, followers=users)

    elif request.form.get('recommend_new'):
        string = request.form.get('recommend_new')
        l = string.strip('][').split(',', 1) # return string to list
        user_a = current_user.id
        user_b = int(l[0])
        item = yaml.safe_load(l[1])

        id = item['id']

        if item_type == 'books':
            exists = bool(BooksRecommended.query.filter_by(user_A_id=user_a, user_B_id=user_b, id=id).first())
            if exists:
                flash(f'You have already recommended this {item_type[:-1]} to this follower.', 'danger')
                return redirect(url_for('main.show', item_type=item_type))
            new = BooksRecommended(user_A_id=user_a, user_B_id=user_b, book_id=id)

        elif item_type == 'films':
            exists = bool(FilmsRecommended.query.filter_by(user_A_id=user_a, user_B_id=user_b, id=id).first())
            if exists:
                flash(f'You have already recommended this {item_type[:-1]} to this follower.', 'danger')
                return redirect(url_for('main.show', item_type=item_type))
            new = FilmsRecommended(user_A_id=user_a, user_B_id=user_b, film_id=id)

        db.session.add(new)
        db.session.commit()
        flash(f'You successfully recommended a new {item_type[:-1]}!', 'success')
        return redirect(url_for('main.show', item_type=item_type))

    else:
        flash('There was a problem with this request.', 'danger')
        return redirect(url_for('main.home'))
