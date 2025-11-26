import os
import sqlite3
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from database import get_connection

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))


# ------------------------------
# SPOTIFY
# ------------------------------

def gather_spotify_data(limit=150):
    conn = get_connection()
    cur = conn.cursor()

    print("Pulling top tracks from Spotify...")

    # Get Spotify editorial chart playlist (Top Hits)
    playlist_id = "5ABHKGoOzxkaa28ttQV9sE"
    results = sp.playlist_items(playlist_id, additional_types=["track"], limit=100)

    tracks = results["items"]

    count = 0

    for item in tracks:
        track = item["track"]
        if not track or not track["id"]:
            continue

        track_id = track["id"]
        track_name = track["name"]
        popularity = track["popularity"]
        duration = track["duration_ms"]
        release_date = track["album"]["release_date"]

        artist = track["artists"][0]
        artist_spotify_id = artist["id"]
        artist_name = artist["name"]

        artist_info = sp.artist(artist_spotify_id)
        followers = artist_info["followers"]["total"]
        artist_popularity = artist_info["popularity"]

        # ---------------------------
        # ARTISTS TABLE
        # ---------------------------
        cur.execute("""
            INSERT OR IGNORE INTO Artists (spotify_artist_id, name, popularity, followers)
            VALUES (?, ?, ?, ?)
        """, (artist_spotify_id, artist_name, artist_popularity, followers))

        cur.execute("""
            SELECT id FROM Artists WHERE spotify_artist_id = ?
        """, (artist_spotify_id,))
        artist_db_id = cur.fetchone()[0]

        # ---------------------------
        # TRACKS TABLE
        # ---------------------------
        cur.execute("""
            INSERT OR IGNORE INTO Tracks
            (spotify_track_id, artist_id, name, release_date, duration_ms, popularity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            track_id,
            artist_db_id,
            track_name,
            release_date,
            duration,
            popularity
        ))

        cur.execute("""
            SELECT id FROM Tracks WHERE spotify_track_id = ?
        """, (track_id,))
        track_db_id = cur.fetchone()[0]

        count += 1
        print(f"Saved {count}: {track_name} - {artist_name}")

    conn.commit()
    conn.close()

    print("Spotify import complete!")


# ------------------------------
# STUBS (you already call these)
# ------------------------------

def gather_lastfm_data(limit=25):
    print("TODO: implement Last.fm")
    pass


def gather_genius_data(limit=25):
    print("TODO: implement Genius")
    pass
