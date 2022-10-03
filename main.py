from flask import Blueprint, render_template, request, redirect, url_for, flash
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
    return render_template('profile.html', user=current_user)

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


