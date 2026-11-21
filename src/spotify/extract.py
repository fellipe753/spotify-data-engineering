
import csv
import json
import os
import re
import time
import unicodedata
from pathlib import Path

import requests

from auth import get_access_token


# Artists can be changed without modifying the extraction logic.
DEFAULT_ARTISTS = [
    "Black Sabbath",
    "The Strokes",
    "Paralamas do Sucesso",
]

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

API_URL = "https://api.spotify.com/v1"
MARKET = "BR"


def normalize_name(name):
    """Normalize names to compare Spotify search results."""
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = name.lower().strip()

    # Allow 'Paralamas do Sucesso' to match
    # 'Os Paralamas do Sucesso'.
    name = re.sub(r"^os\s+", "", name)

    return name


def request_json(url, headers, params=None):
    """Make an API request with basic rate-limit handling."""

    for attempt in range(4):

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code == 429 and attempt < 3:
            wait_time = int(response.headers.get("Retry-After", 5))
            print(f"Rate limit reached. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue

        response.raise_for_status()
        return response.json()

    raise RuntimeError("Spotify API rate limit exceeded after retries.")


def fetch_all_pages(url, headers, params, item_key):
    """Fetch all pages from a paginated Spotify endpoint."""

    items = []
    pages = []

    while url:

        data = request_json(url, headers, params)

        pages.append(data)
        items.extend(data.get(item_key, []))

        url = data.get("next")
        params = None

    return items, pages


def search_artist(artist_name, headers):
    """Find an artist using its name."""

    url = f"{API_URL}/search"

    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 10,
        "market": MARKET
    }

    data = request_json(url, headers, params)

    candidates = data.get("artists", {}).get("items", [])

    expected_name = normalize_name(artist_name)

    artist = next(
        (
            item for item in candidates
            if normalize_name(item["name"]) == expected_name
        ),
        None
    )

    if not artist:
        names = [item["name"] for item in candidates]

        raise ValueError(
            f"Artist '{artist_name}' not found as an exact match. "
            f"Spotify returned: {names}"
        )

    return artist, data


def extract_artist_albums(artist, headers):
    """Extract all albums, singles and compilations from an artist."""

    url = f"{API_URL}/artists/{artist['id']}/albums"

    params = {
        "include_groups": "album,single,compilation",
        "limit": 10,
        "market": MARKET
    }

    albums, pages = fetch_all_pages(
        url,
        headers,
        params,
        "items"
    )

    # Remove duplicated albums using Spotify ID.
    unique_albums = {
        album["id"]: album
        for album in albums
    }

    return list(unique_albums.values()), pages


def extract_album_tracks(album, headers):
    """Extract all tracks from an album."""

    url = f"{API_URL}/albums/{album['id']}/tracks"

    params = {
        "limit": 50,
        "market": MARKET
    }

    tracks, pages = fetch_all_pages(
        url,
        headers,
        params,
        "items"
    )

    return tracks, pages


def get_image_url(item):
    images = item.get("images") or []

    return images[0]["url"] if images else None


def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def save_csv(data, path, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(data)


def run_extraction(artist_names=None):

    if artist_names is None:
        configured_artists = os.getenv("SPOTIFY_ARTISTS")

        artist_names = (
            [name.strip() for name in configured_artists.split(",") if name.strip()]
            if configured_artists
            else DEFAULT_ARTISTS
        )

    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    artists_raw = []
    albums_raw = []
    tracks_raw = []

    artists_csv = []
    albums_csv = []
    tracks_csv = []

    for artist_name in artist_names:

        print(f"\nProcessing artist: {artist_name}")

        # 1. Search artist
        artist, search_response = search_artist(
            artist_name,
            headers
        )

        artist_id = artist["id"]
        actual_artist_name = artist["name"]

        artists_raw.append({
            "search_term": artist_name,
            "response": search_response
        })

        artists_csv.append({
            "id": artist_id,
            "name": actual_artist_name,
            "genres": ", ".join(artist.get("genres") or []),
            "spotify_url": artist.get("external_urls", {}).get("spotify"),
            "image_url": get_image_url(artist)
        })

        print(f"Artist found: {actual_artist_name}")

        # 2. Extract albums
        albums, album_pages = extract_artist_albums(
            artist,
            headers
        )

        albums_raw.append({
            "artist_id": artist_id,
            "artist_name": actual_artist_name,
            "pages": album_pages
        })

        print(f"Albums found: {len(albums)}")

        # 3. Extract tracks from each album
        for album in albums:

            album_id = album["id"]
            album_name = album["name"]

            images = album.get("images") or []

            albums_csv.append({
                "id": album_id,
                "artist_id": artist_id,
                "artist_name": actual_artist_name,
                "name": album_name,
                "release_date": album.get("release_date"),
                "release_date_precision": album.get("release_date_precision"),
                "total_tracks": album.get("total_tracks"),
                "album_type": album.get("album_type"),
                "spotify_url": album.get("external_urls", {}).get("spotify"),
                "image_url": get_image_url(album)
            })

            tracks, track_pages = extract_album_tracks(
                album,
                headers
            )

            tracks_raw.append({
                "artist_id": artist_id,
                "artist_name": actual_artist_name,
                "album_id": album_id,
                "album_name": album_name,
                "pages": track_pages
            })

            for track in tracks:

                track_artists = track.get("artists") or []

                tracks_csv.append({
                    "id": track.get("id"),
                    "album_id": album_id,
                    "album_name": album_name,
                    "artist_id": artist_id,
                    "artist_name": actual_artist_name,
                    "name": track.get("name"),
                    "track_artists": ", ".join(
                        item["name"] for item in track_artists
                    ),
                    "track_number": track.get("track_number"),
                    "disc_number": track.get("disc_number"),
                    "duration_ms": track.get("duration_ms"),
                    "explicit": track.get("explicit"),
                    "spotify_url": track.get("external_urls", {}).get("spotify")
                })

            print(
                f"  Album: {album_name} | Tracks: {len(tracks)}"
            )

    # 4. Save Bronze JSON files
    save_json(
        artists_raw,
        DATA_DIR / "bronze/artists/artists.json"
    )

    save_json(
        albums_raw,
        DATA_DIR / "bronze/albums/albums.json"
    )

    save_json(
        tracks_raw,
        DATA_DIR / "bronze/tracks/tracks.json"
    )

    # 5. Save Silver CSV files
    save_csv(
        artists_csv,
        DATA_DIR / "processed/artists.csv",
        [
            "id",
            "name",
            "genres",
            "spotify_url",
            "image_url"
        ]
    )

    save_csv(
        albums_csv,
        DATA_DIR / "processed/albums.csv",
        [
            "id",
            "artist_id",
            "artist_name",
            "name",
            "release_date",
            "release_date_precision",
            "total_tracks",
            "album_type",
            "spotify_url",
            "image_url"
        ]
    )

    save_csv(
        tracks_csv,
        DATA_DIR / "processed/tracks.csv",
        [
            "id",
            "album_id",
            "album_name",
            "artist_id",
            "artist_name",
            "name",
            "track_artists",
            "track_number",
            "disc_number",
            "duration_ms",
            "explicit",
            "spotify_url"
        ]
    )

    print("\n========== EXTRACTION SUMMARY ==========")
    print(f"Artists: {len(artists_csv)}")
    print(f"Albums: {len(albums_csv)}")
    print(f"Tracks: {len(tracks_csv)}")
    print("JSON and CSV files generated successfully.")


if __name__ == "__main__":
    run_extraction()
