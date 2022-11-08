import spotipy, os
from flask_sqlalchemy import SQLAlchemy
from spotipy.oauth2 import SpotifyClientCredentials

db = SQLAlchemy()

# Spotify setup
cid = os.environ.get("SPOTIFY_API_ID")
csecret = os.environ.get("SPOTIFY_API_KEY")
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=csecret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)