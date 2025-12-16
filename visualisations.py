import os
import matplotlib.pyplot as plt
from database import get_connection


def process_data():
    """
    Writes calculation results to output/calculations.txt
    Required by the project spec.
    """

    conn = get_connection()
    cur = conn.cursor()

    os.makedirs("output", exist_ok=True)

    rows = cur.execute("""
        SELECT TrackTags.tag, AVG(Tracks.popularity) AS avg_popularity
        FROM Tracks
        JOIN TrackTags ON Tracks.id = TrackTags.track_id
        GROUP BY TrackTags.tag
        HAVING COUNT(*) > 1
        ORDER BY avg_popularity DESC
    """).fetchall()

    with open("output/calculations.txt", "w") as f:
        for tag, avg_pop in rows:
            f.write(f"{tag}: {round(avg_pop, 2)}\n")

    conn.close()

# 1 : Average Spotify popularity by Last.fm tag

def viz_avg_popularity_by_tag():
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
    plt.savefig("output/viz1_avg_popularity_by_tag.png")
    plt.close()

    conn.close()


# 2 : Spotify popularity vs Genius pageviews (scatterplot)

def viz_popularity_vs_pageviews():
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT Tracks.popularity, GeniusMetadata.pageviews
        FROM Tracks
        JOIN GeniusMetadata ON Tracks.id = GeniusMetadata.track_id
        WHERE GeniusMetadata.pageviews IS NOT NULL
    """).fetchall()

    popularity = [r[0] for r in rows]
    pageviews = [r[1] for r in rows]

    plt.figure(figsize=(8, 6))
    plt.scatter(popularity, pageviews)
    plt.xlabel("Spotify Popularity")
    plt.ylabel("Genius Pageviews")
    plt.title("Spotify Popularity vs Genius Pageviews")
    plt.tight_layout()
    plt.savefig("output/viz2_popularity_vs_pageviews.png")
    plt.close()

    conn.close()


# 3 : Average annotation count by Last.fm tag

def viz_annotations_by_tag():
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT TrackTags.tag, AVG(GeniusMetadata.annotation_count) AS avg_annotations
        FROM Tracks
        JOIN TrackTags ON Tracks.id = TrackTags.track_id
        JOIN GeniusMetadata ON Tracks.id = GeniusMetadata.track_id
        GROUP BY TrackTags.tag
        HAVING COUNT(*) > 1
        ORDER BY avg_annotations DESC
    """).fetchall()

    tags = [r[0] for r in rows]
    values = [r[1] for r in rows]

    plt.figure(figsize=(12, 6))
    plt.bar(tags, values)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Average Annotation Count")
    plt.title("Average Genius Annotations by Last.fm Tag")
    plt.tight_layout()
    plt.savefig("output/viz3_annotations_by_tag.png")
    plt.close()

    conn.close()


def create_visualizations():
    """
    Runs all three visualizations.
    main.py should call ONLY this function.
    """

    os.makedirs("output", exist_ok=True)

    viz_avg_popularity_by_tag()
    viz_popularity_vs_pageviews()
    viz_annotations_by_tag()
