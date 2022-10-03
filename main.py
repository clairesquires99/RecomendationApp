from flask import Blueprint, render_template
from flask_login import login_required, current_user

from .models import *
from . import db

main = Blueprint('main', __name__)

@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/books')
@login_required
def books():
    return render_template('books.html')

@main.route('/followers')
@login_required
def show_followers():
    followers = db.session.query(Follower.user_A_id).filter(Follower.user_B_id == current_user.id).subquery()
    users = User.query.join(followers, User.id == followers.c.user_A_id)
    return render_template('followers.html', followers=users)

@main.route('/following')
@login_required
def show_following():
    following = Follower.query.all()
    return render_template('followers.html', following=following)


