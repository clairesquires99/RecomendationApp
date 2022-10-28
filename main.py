import os, json, requests
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import git, yaml

from .models import *
from . import db, utils

main = Blueprint('main', __name__)

@main.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('./RecommendationApp')
        origin = repo.remotes.origin
        origin.pull()
        return '', 200
    else:
        return '', 400

@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/profile')
@login_required
def profile():
    # by default show following
    users = utils.following()
    return render_template('profile.html', user=current_user, follow=users, followers=False)

@main.route('/profile', methods=['POST'])
@login_required
def profile_post():
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


# MEDIA
@main.route('/show/<item_type>')
@login_required
def show(item_type):
    # by default show items recommended to user
    items = []
    if item_type == 'books':
        results = utils.books_rec_to_user()
        items = utils.books_complete(results)
    elif item_type == 'films':
        results = utils.films_rec_to_user()
        for item in results:
            items.append(utils.name_to_title(item))
        
    return render_template('show.html', item_type=item_type, items=items, recs_to_user=True)

@main.route('/show/<item_type>', methods=['POST'])
@login_required
def show_post(item_type):
    items = []
    if request.form['recommended'] == "to user":
        if item_type == 'books':
            results = utils.books_rec_to_user()
            items = utils.books_complete(results)
        elif item_type == 'films':
            results = utils.films_rec_to_user()
            for item in results:
                items.append(utils.name_to_title(item))
        recs_to_user = True
    elif request.form['recommended'] == "by user":
        if item_type == 'books':
            results = utils.books_rec_by_user()
            items = utils.books_complete(results)
        elif item_type == 'films':
            results = utils.films_rec_by_user()
            for item in results:
                items.append(utils.name_to_title(item))
        recs_to_user = False
    return render_template('show.html', item_type=item_type, items=items, recs_to_user=recs_to_user)

@main.route('/search/<item_type>')
@login_required
def search(item_type):
    items = []
    if 'books' in request.args:
        search_word = request.args.get('books')
        link = f'https://www.googleapis.com/books/v1/volumes?q={search_word}&key='
        link += os.environ.get("GOOGLE_BOOKS_API")
        response = requests.get(link)
        if response.status_code == 200:
            data = json.loads(response.content)
            items = data['items']
            items = utils.books_complete(items)
    elif 'films' in request.args:
        search_word = request.args.get('films')
        link = 'https://api.themoviedb.org/3/search/multi?api_key='
        link += os.environ.get("FILM_API")
        link += f'&query={search_word}'
        response = requests.get(link)
        if response.status_code == 200:
            data = json.loads(response.content)
        for item in data['results']:
            item = utils.name_to_title(item)
            items.append(item)

    return render_template('search.html', item_type=item_type, items=items)

# PICKUP: fix this function and the one below. ensure functionaly of both books and films working from end-to-end

@main.route('/recommend/<item_type>', methods=['POST'])
@login_required
def recommend(item_type):
    if request.form.get('recommend'):
        item = request.form['recommend']
        item = item.replace('"', '\\"')
        item = item.replace("'", '"')
        item = yaml.safe_load(item)
        
        if item_type == 'books':
            item['title'] = item['volumeInfo']['title']
        elif item_type == 'films':
            item = utils.name_to_title(item)

        followers = db.session.query(Follower.user_A_id).filter(Follower.user_B_id == current_user.id).subquery()
        users = User.query.join(followers, User.id == followers.c.user_A_id)
        return render_template('recommend.html', item_type=item_type, item=item, followers=users)

    elif request.form.get('recommend_new'):
        string = request.form.get('recommend_new')
        l = string.strip('][').split(',', 1) # return string to list
        user_a = current_user.id
        user_b = int(l[0])
        item = yaml.safe_load(l[1])
        if item_type == 'books':
            id = item['id']
            new = BooksRecommended(user_A_id=user_a, user_B_id=user_b, book_id=id)
        elif item_type == 'films':
            id = f"{item['media_type']}/{item['id']}"
            new = FilmsRecommended(user_A_id=user_a, user_B_id=user_b, film_id=id)
        db.session.add(new)
        db.session.commit()
        flash(f'You successfully recommended a new {item_type}!', 'success')
        return redirect(url_for('main.show_post', item_type=item_type))

    else:
        flash('There was a problem with this request.', 'danger')
        return redirect(url_for('main.home'))
