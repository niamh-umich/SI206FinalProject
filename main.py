# Students numbers & emails: Niamh Duffy niamh@umich.edu 36240407
# Sophie Bascone  sbascone@umich.edu 00134142
# Justin Fiorillo haoranlu@umich.edu 77117441

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope
))

results = sp.current_user_saved_tracks(limit=20)

for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], "-", track['name'])