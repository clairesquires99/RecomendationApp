import spotipy
from os import environ, path
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from spotipy.oauth2 import SpotifyClientCredentials

db = SQLAlchemy()

# Spotify setup
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '..', '.env'))
cid = environ.get("SPOTIPY_CLIENT_ID")
csecret = environ.get("SPOTIPY_CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(
    client_id=cid, client_secret=csecret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
