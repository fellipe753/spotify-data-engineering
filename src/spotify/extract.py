
import csv
import json
from pathlib import Path

import requests

from auth import get_access_token


def extract_artists(search_term):

    token = get_access_token()

    url = "https://api.spotify.com/v1/search"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "q": search_term,
        "type": "artist",
        "limit": 10
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    # Save raw JSON
    bronze_path = Path("data/bronze/artists")
    bronze_path.mkdir(parents=True, exist_ok=True)

    with open(bronze_path / "artists.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    # Prepare CSV
    artists = data["artists"]["items"]

    processed_path = Path("data/processed")
    processed_path.mkdir(parents=True, exist_ok=True)

    csv_path = processed_path / "artists.csv"

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as file:

        fieldnames = [
            "id",
            "name",
            "genres",
            "popularity",
            "followers",
            "spotify_url",
            "image_url"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for artist in artists:
            images = artist.get("images") or []
            followers = artist.get("followers") or {}

            writer.writerow({
                "id": artist.get("id"),
                "name": artist.get("name"),
                "genres": ", ".join(artist.get("genres") or []),
                "popularity": artist.get("popularity"),
                "followers": followers.get("total"),
                "spotify_url": artist.get("external_urls", {}).get("spotify"),
                "image_url": images[0]["url"] if images else None
            })

    print(f"Artists extracted: {len(artists)}")
    print(f"CSV saved: {csv_path}")
    print(f"JSON saved: {bronze_path / 'artists.json'}")


# if __name__ == "__main__":
#     extract_artists("Radiohead")


def test_artist_details(artist_id):

    token = get_access_token()

    url = f"https://api.spotify.com/v1/artists/{artist_id}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print("HTTP Status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    print("\nAvailable fields:")
    print(list(data.keys()))

    print("\nGenres:", data.get("genres"))
    print("Followers:", data.get("followers"))
    print("Popularity:", data.get("popularity"))



def extract_albums(artist_id, artist_name):

    token = get_access_token()

    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"

    headers = {
        "Authorization": f"Bearer {token}"
    }


    params = {
        "include_groups": "album,single,compilation",
        "limit": 10,
        "market": "BR"
    }    

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    #response.raise_for_status()
    if response.status_code != 200:
        print("API Error:", response.status_code)
        print("Details:", response.text)

    response.raise_for_status()

    data = response.json()

    # Save raw JSON
    bronze_path = Path("data/bronze/albums")
    bronze_path.mkdir(parents=True, exist_ok=True)

    with open(bronze_path / "albums.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    # Prepare CSV
    albums = data["items"]

    processed_path = Path("data/processed")
    processed_path.mkdir(parents=True, exist_ok=True)

    csv_path = processed_path / "albums.csv"

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as file:

        fieldnames = [
            "id",
            "name",
            "artist_name",
            "release_date",
            "release_date_precision",
            "total_tracks",
            "album_type",
            "spotify_url",
            "image_url"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for album in albums:

            images = album.get("images") or []

            writer.writerow({
                "id": album.get("id"),
                "name": album.get("name"),
                "artist_name": artist_name,
                "release_date": album.get("release_date"),
                "release_date_precision": album.get("release_date_precision"),
                "total_tracks": album.get("total_tracks"),
                "album_type": album.get("album_type"),
                "spotify_url": album.get("external_urls", {}).get("spotify"),
                "image_url": images[0]["url"] if images else None
            })

    print(f"Albums extracted: {len(albums)}")
    print(f"CSV saved: {csv_path}")
    print(f"JSON saved: {bronze_path / 'albums.json'}")


# if __name__ == "__main__":
#     extract_albums(
#         "4Z8W4fKeB5YxbusRsdQVPb",
#         "Radiohead"
#     )



def extract_tracks(album_id, album_name):

    token = get_access_token()

    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "limit": 50,
        "market": "BR"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    if response.status_code != 200:
        print("API Error:", response.status_code)
        print("Details:", response.text)

    response.raise_for_status()

    data = response.json()

    # Save raw JSON
    bronze_path = Path("data/bronze/tracks")
    bronze_path.mkdir(parents=True, exist_ok=True)

    with open(bronze_path / "tracks.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    # Prepare CSV
    tracks = data["items"]

    processed_path = Path("data/processed")
    processed_path.mkdir(parents=True, exist_ok=True)

    csv_path = processed_path / "tracks.csv"

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as file:

        fieldnames = [
            "id",
            "name",
            "album_name",
            "artist_name",
            "track_number",
            "disc_number",
            "duration_ms",
            "explicit",
            "spotify_url"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for track in tracks:

            artists = [
                artist["name"]
                for artist in track.get("artists", [])
            ]

            writer.writerow({
                "id": track.get("id"),
                "name": track.get("name"),
                "album_name": album_name,
                "artist_name": ", ".join(artists),
                "track_number": track.get("track_number"),
                "disc_number": track.get("disc_number"),
                "duration_ms": track.get("duration_ms"),
                "explicit": track.get("explicit"),
                "spotify_url": track.get("external_urls", {}).get("spotify")
            })

    print(f"Tracks extracted: {len(tracks)}")
    print(f"CSV saved: {csv_path}")
    print(f"JSON saved: {bronze_path / 'tracks.json'}")


# if __name__ == "__main__":
#     extract_tracks(
#         "5vkqYmiPBYLaalcmjujWxK",
#         "In Rainbows"
#     )


def extract_playlist(playlist_id):

    token = get_access_token()

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "market": "BR"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    if response.status_code != 200:
        print("API Error:", response.status_code)
        print("Details:", response.text)

    response.raise_for_status()

    data = response.json()

    # Save raw JSON
    bronze_path = Path("data/bronze/playlists")
    bronze_path.mkdir(parents=True, exist_ok=True)

    with open(bronze_path / "playlists.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    # Prepare CSV
    images = data.get("images") or []

    playlist = {
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description"),
        "owner_id": data.get("owner", {}).get("id"),
        "owner_name": data.get("owner", {}).get("display_name"),
        "public": data.get("public"),
        "collaborative": data.get("collaborative"),
        "followers": data.get("followers", {}).get("total"),
        "spotify_url": data.get("external_urls", {}).get("spotify"),
        "image_url": images[0]["url"] if images else None,
        "snapshot_id": data.get("snapshot_id")
    }

    processed_path = Path("data/processed")
    processed_path.mkdir(parents=True, exist_ok=True)

    with open(
        processed_path / "playlists.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=playlist.keys()
        )

        writer.writeheader()
        writer.writerow(playlist)

    print("Playlist metadata extracted successfully!")
    print("CSV saved: data/processed/playlists.csv")
    print("JSON saved: data/bronze/playlists/playlists.json")


    print("Playlist:", data.get("name"))
    print("Owner:", data.get("owner", {}).get("display_name"))
    print("Available fields:", list(data.keys()))


if __name__ == "__main__":
    extract_playlist("3aBCsCrpXA1Vaww6DK1OO3")