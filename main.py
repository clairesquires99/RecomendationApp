import os, json, requests, yaml, spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from .models import *
from . import db, utils

# Spotify setup
cid = os.environ.get("SPOTIFY_API_ID")
csecret = os.environ.get("SPOTIFY_API_KEY")
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=csecret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

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


# MEDIA
@main.route('/show/<item_type>', methods=['GET', 'POST'])
@login_required
def show(item_type):
    items = []        
    if request.method == 'GET':
        recs_to_user = True
        if item_type == 'books':
            results = utils.books_rec_to_user()
            items = utils.books_complete(results)
        elif item_type == 'films':
            results = utils.films_rec_to_user()
            for item in results:
                items.append(utils.name_to_title(item))
    else:
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
    data = None # default
    if 'books' in request.args:
        search_word = request.args.get('books')
        link = f'https://www.googleapis.com/books/v1/volumes?q={search_word}&key='
        link += os.environ.get("GOOGLE_BOOKS_API")
        response = requests.get(link)
        if response.status_code == 200:
            data = json.loads(response.content)
            if data and int(data['totalItems']) > 0:
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
        if data:
            for item in data['results']:
                item = utils.name_to_title(item)
                items.append(item)
    # elif 'music' in request.args:
    #     search_word = request.args.get('music')
        # data = sp.search(q=search_word, type='track')
        
    # data = sp.search(q='hello', type='track')
    # results = data['tracks']['items']
    # for r in results['tracks']['items']:
    #     name = r['name']
    #     artist = r['artists'][0]['name']
    #     id = r['id']
    #     print(r)


    if request.args and (len(items) == 0):
        flash(f"We coulnd't find any results for your search, sorry!", 'success')

    return render_template('search.html', item_type=item_type, items=items)

@main.route('/recommend/<item_type>', methods=['POST'])
@login_required
def recommend(item_type):
    if request.form.get('recommend'):
        item = request.form['recommend']
        # item = item.replace('"', '\\"')
        # item = item.replace("'", '"')
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
            exists = bool(BooksRecommended.query.filter_by(user_A_id=user_a, user_B_id=user_b, id=id).first())
            if exists:
                flash(f'You have already recommended this {item_type[:-1]} to this follower.', 'danger')
                return redirect(url_for('main.show', item_type=item_type))
            new = BooksRecommended(user_A_id=user_a, user_B_id=user_b, book_id=id)

        elif item_type == 'films':
            id = f"{item['media_type']}/{item['id']}"
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
