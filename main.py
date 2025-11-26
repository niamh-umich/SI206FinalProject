# Students numbers & emails: Niamh Duffy niamh@umich.edu 36240407
# Sophie Bascone  sbascone@umich.edu 00134142
# Justin Fiorillo haoranlu@umich.edu 77117441

import os
<<<<<<< HEAD
from dotenv import load_dotenv
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyOAuth

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
=======

from database import create_tables
from apis import (
    gather_spotify_data,
    gather_lastfm_data,
    gather_genius_data
)
from analysis_and_viz import (
    process_data,
    create_visualizations
)
>>>>>>> 2141ae9 (main)

def main():

    #SQL tables
    create_tables()

    print("getting Spotify data ")
    gather_spotify_data(limit=25)

<<<<<<< HEAD
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], "-", track['name'])
=======
    print("getting Last.fm data")
    gather_lastfm_data(limit=25)

    print("getting Genius metadata")
    gather_genius_data(limit=25)

    process_data()

    print("Visualizations")
    create_visualizations()

    print("Check output folder")

if __name__ == "__main__":
    main()
>>>>>>> 2141ae9 (main)
