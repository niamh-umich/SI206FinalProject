# Students numbers & emails: Niamh Duffy niamh@umich.edu 36240407
# Sophie Bascone  sbascone@umich.edu 00134142
# Justin Fiorillo haoranlu@umich.edu 77117441

import os

from database import create_tables
from api import (
    gather_spotify_data,
    gather_lastfm_data,
    gather_genius_data
)
#from analysis_and_viz import (
#    process_data,
#    create_visualizations
#)

def main():

    #SQL tables
    create_tables()

    print("getting Spotify data ")
    gather_spotify_data(limit=100)

    print("getting Last.fm data")
    gather_lastfm_data(limit=25)

    print("getting Genius metadata")
    gather_genius_data(limit=25)

   # process_data()

 #   print("Visualizations")
   # create_visualizations()

    print("Check output folder")

if __name__ == "__main__":
    main()
