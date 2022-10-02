from re import template
from flask import Blueprint, render_template
from flask_login import login_required
from . import db

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/profile')
@login_required
def profile():
    return 'Profile'

@main.route('/books/')
@login_required
def books():
    return render_template('books.html')

