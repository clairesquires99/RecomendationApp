from flask import Blueprint, render_template
from . import db

main = Blueprint('main', __name__)

@main.route('/home')
def home():
    return render_template('home.html')

@main.route('/profile')
def profile():
    return 'Profile'

