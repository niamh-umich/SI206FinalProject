import sqlite3
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import matplotlib.pyplot as plt
import os
import urllib.parse

from database import get_connection

SPOTIPY_CLIENT_ID = "e1f4ef3c783047f38f52bcbf7d0b8df5"
SPOTIPY_CLIENT_SECRET = "8f38ea7b4f3c4ab99e53f7f60315a61f"
LASTFM_API_KEY = "50983eca61b9dde155f61695a6b1919f"
GENIUS_TOKEN = "1UGL0TI68nJNcqEhnG17VZln745U281Cjw9TL6UuZLfzJNoAEwR_ZsrbpQSxh12-"

def gather_spotify_data(limit=25):
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET
        )
    )

    conn = get_connection()
    cur = conn.cursor()

    playlist_id = "5ABHKGoOzxkaa28ttQV9sE"  # Spotify Top Hits
    results = sp.playlist_items(playlist_id, limit=limit)

    for item in results["items"]:
        track = item["track"]
        if not track:
            continue

        artist = track["artists"][0]
        artist_info = sp.artist(artist["id"])

        # Insert Artist
        cur.execute("""
            INSERT OR IGNORE INTO Artists
            (spotify_artist_id, name, popularity, followers)
            VALUES (?, ?, ?, ?)
        """, (
            artist["id"],
            artist["name"],
            artist_info["popularity"],
            artist_info["followers"]["total"]
        ))

        cur.execute("SELECT id FROM Artists WHERE spotify_artist_id=?", (artist["id"],))
        artist_id = cur.fetchone()[0]

        # Insert Track
        cur.execute("""
            INSERT OR IGNORE INTO Tracks
            (spotify_track_id, artist_id, name, release_date, duration_ms, popularity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            track["id"],
            artist_id,
            track["name"],
            track["album"]["release_date"],
            track["duration_ms"],
            track["popularity"]
        ))

    conn.commit()
    conn.close()

# LAST.FM

def gather_lastfm_data(limit=25):
    conn = get_connection()
    cur = conn.cursor()

    # Get tracks with artist names
    cur.execute("""
        SELECT Tracks.id, Tracks.name, Artists.name
        FROM Tracks
        JOIN Artists ON Tracks.artist_id = Artists.id
        LIMIT ?
    """, (limit,))

    tracks = cur.fetchall()
    inserted = 0

    for track_id, track_name, artist_name in tracks:
        # URL-encode names to handle spaces/special chars
        track_q = urllib.parse.quote(track_name)
        artist_q = urllib.parse.quote(artist_name)

        url = (
            "http://ws.audioscrobbler.com/2.0/"
            f"?method=track.gettoptags"
            f"&track={track_q}"
            f"&artist={artist_q}"
            f"&api_key={LASTFM_API_KEY}"
            f"&format=json"
        )

        response = requests.get(url)
        data = response.json()

        tags = data.get("toptags", {}).get("tag", [])

        for tag in tags[:3]:  # limit tags per track
            if "name" in tag:
                cur.execute("""
                    INSERT INTO TrackTags (track_id, tag, tag_count)
                    VALUES (?, ?, ?)
                """, (
                    track_id,
                    tag["name"],
                    int(tag.get("count", 0))
                ))
                inserted += 1

    conn.commit()
    conn.close()

    print(f"Inserted {inserted} Last.fm tags")



# GENIUS

def gather_genius_data(limit=25):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM Tracks LIMIT 1")
    track_id, name = cur.fetchone()

    headers = {"Authorization": f"Bearer {GENIUS_TOKEN}"}
    url = f"https://api.genius.com/search?q={name}"

    hits = requests.get(url, headers=headers).json()["response"]["hits"]

    for hit in hits[:limit]:
        song = hit["result"]
        cur.execute("""
            INSERT INTO GeniusMetadata
            (track_id, genius_song_id, annotation_count, pageviews, hot, lyrics_state)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            track_id,
            song["id"],
            song.get("annotation_count", 0),
            song.get("pageviews", 0),
            int(song["stats"]["hot"]),
            song["lyrics_state"]
        ))

    conn.commit()
    conn.close()


# ANALYSIS


def process_data():
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT TrackTags.tag, AVG(Tracks.popularity) AS avg_popularity
        FROM Tracks
        JOIN TrackTags ON Tracks.id = TrackTags.track_id
        GROUP BY TrackTags.tag
        HAVING COUNT(*) > 1
        ORDER BY avg_popularity DESC
    """).fetchall()

    os.makedirs("output", exist_ok=True)

    with open("output/calculations.txt", "w") as f:
        for tag, avg_pop in rows:
            f.write(f"{tag}: {round(avg_pop, 2)}\n")

    conn.close()



# VISUALIZATION

def create_visualizations():
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT TrackTags.tag, AVG(Tracks.popularity) AS avg_popularity
        FROM Tracks
        JOIN TrackTags ON Tracks.id = TrackTags.track_id
        GROUP BY TrackTags.tag
        HAVING COUNT(*) > 1
        ORDER BY avg_popularity DESC
    """).fetchall()

    tags = [r[0] for r in rows]
    values = [r[1] for r in rows]

    plt.figure(figsize=(12, 6))
    plt.bar(tags, values)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Average Spotify Popularity")
    plt.title("Average Track Popularity by Last.fm Tag")
    plt.tight_layout()
    plt.savefig("output/avg_popularity_by_tag.png")
    plt.close()

    conn.close()