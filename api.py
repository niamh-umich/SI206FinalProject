import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib.parse

from database import get_connection

SPOTIPY_CLIENT_ID = "e1f4ef3c783047f38f52bcbf7d0b8df5"
SPOTIPY_CLIENT_SECRET = "8f38ea7b4f3c4ab99e53f7f60315a61f"
LASTFM_API_KEY = "50983eca61b9dde155f61695a6b1919f"
GENIUS_TOKEN = "1UGL0TI68nJNcqEhnG17VZln745U281Cjw9TL6UuZLfzJNoAEwR_ZsrbpQSxh12-"


def gather_spotify_data(limit=100):
    print("Gathering Spotify data...")
    
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri="http://127.0.0.1:8888/callback",
            scope=""
        )
    )


    conn = get_connection()
    cur = conn.cursor()

    playlist_id = "5ABHKGoOzxkaa28ttQV9sE"  # Spotify Top Hits
    offset = 0
    inserted = 0

    # Store mapping: spotify_track_id -> local track_id
    track_id_map = {}

    while inserted < limit:
        results = sp.playlist_items(
            playlist_id,
            limit=25,
            offset=offset
        )

        if not results["items"]:
            break

        for item in results["items"]:
            if inserted >= limit:
                break

            track = item.get("track")
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

            cur.execute(
                "SELECT id FROM Artists WHERE spotify_artist_id=?",
                (artist["id"],)
            )
            artist_pk = cur.fetchone()[0]

            # Insert Track
            cur.execute("""
                INSERT OR IGNORE INTO Tracks
                (spotify_track_id, artist_id, name, release_date, duration_ms, popularity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                track["id"],
                artist_pk,
                track["name"],
                track["album"]["release_date"],
                track["duration_ms"],
                track["popularity"]
            ))

            cur.execute(
                "SELECT id FROM Tracks WHERE spotify_track_id=?",
                (track["id"],)
            )
            track_pk = cur.fetchone()[0]

            # Save mapping for audio features later
            track_id_map[track["id"]] = track_pk

            inserted += 1

        offset += 25


    conn.commit()
    conn.close()

    print(f"Inserted {inserted} Spotify tracks")


# LAST.FM

def gather_lastfm_data(limit=100):
    """
    Collects Last.fm tags for multiple tracks
    so TrackTags reaches 100+ rows.
    """

    print("Gathering Last.fm data...")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT Tracks.id, Tracks.name, Artists.name
        FROM Tracks
        JOIN Artists ON Tracks.artist_id = Artists.id
        LIMIT ?
    """, (limit,))

    tracks = cur.fetchall()
    inserted = 0

    for track_id, track_name, artist_name in tracks:
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

        data = requests.get(url).json()
        tags = data.get("toptags", {}).get("tag", [])

        for tag in tags[:5]:  # 5 tags per track
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

def gather_genius_data(limit=100):
    """
    Collects Genius metadata for many tracks
    so GeniusMetadata reaches 100+ rows.
    """

    print("Gathering Genius data...")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM Tracks LIMIT ?", (limit,))
    tracks = cur.fetchall()

    headers = {"Authorization": f"Bearer {GENIUS_TOKEN}"}
    inserted = 0

    for track_id, name in tracks:
        url = f"https://api.genius.com/search?q={name}"
        response = requests.get(url, headers=headers).json()
        hits = response.get("response", {}).get("hits", [])

        if not hits:
            continue

        song = hits[0]["result"]

        cur.execute("""
            INSERT INTO GeniusMetadata
            (track_id, genius_song_id, annotation_count, pageviews, hot, lyrics_state)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            track_id,
            song["id"],
            song.get("annotation_count", 0),
            song.get("pageviews", 0),
            int(song["stats"].get("hot", False)),
            song["lyrics_state"]
        ))

        inserted += 1

    conn.commit()
    conn.close()

    print(f"Inserted {inserted} Genius records")
