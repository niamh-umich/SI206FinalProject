# Students numbers & emails:
# Niamh Duffy – niamh@umich.edu – 36240407
# Sophie Bascone – sbascone@umich.edu – 00134142
# Justin Fiorillo – haoranlu@umich.edu – 77117441

from database import create_tables
from api import (
    gather_spotify_data,
    gather_lastfm_data,
    gather_genius_data,
    process_data,
    create_visualizations
)

def main():
    create_tables()

    print("Getting Spotify data...")
    gather_spotify_data(limit=25)

    print("Getting Last.fm data...")
    gather_lastfm_data(limit=25)

    print("Getting Genius metadata...")
    gather_genius_data(limit=25)

    process_data()
    create_visualizations()

    print("Done! Check project.db and output/")

if __name__ == "__main__":
    main()
