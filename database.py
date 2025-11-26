import sqlite3
import os

DB_NAME = "project.db"


def get_connection():
    path = os.path.dirname(os.path.abspath(__file__))

    full_path = os.path.join(path, DB_NAME)

    # creates file if it doesn't exist)
    return sqlite3.connect(full_path)


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # TABLE 1: Artists (From Spotify API)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spotify_artist_id TEXT UNIQUE,
            name TEXT,
            popularity INTEGER,
            followers INTEGER
        )
    """)

    # TABLE 2: Tracks (From Spotify API)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spotify_track_id TEXT UNIQUE,
            artist_id INTEGER,
            name TEXT,
            release_date TEXT,
            duration_ms INTEGER,
            popularity INTEGER,
            FOREIGN KEY (artist_id) REFERENCES Artists(id)
        )
    """)

    # TABLE 3: AudioFeatures (From Spotify API)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS AudioFeatures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            danceability REAL,
            energy REAL,
            loudness REAL,
            valence REAL,
            tempo REAL,
            FOREIGN KEY (track_id) REFERENCES Tracks(id)
        )
    """)

    # TABLE 4: TrackTags (From Last.fm API)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS TrackTags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            tag TEXT,
            tag_count INTEGER,
            FOREIGN KEY (track_id) REFERENCES Tracks(id)
        )
    """)

    # TABLE 5: GeniusMetadata (From Genius API)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS GeniusMetadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            genius_song_id TEXT,
            annotation_count INTEGER,
            pageviews INTEGER,
            hot BOOLEAN,
            lyrics_state TEXT,
            FOREIGN KEY (track_id) REFERENCES Tracks(id)
        )
    """)

    conn.commit()
    conn.close()
