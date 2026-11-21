
import requests
from auth import get_access_token

ARTIST_IDS = {
    "Black Sabbath - Perfil 1": "5M52tdBnJaKSvOpJGz8mfZ",
    "Black Sabbath - Perfil 2": "7KwFSSDsXWVmiJjeuYCgx3"
}


def get_artist_albums(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "include_groups": "album,single,compilation",
        "limit": 10,
        "market": "BR"
    }

    albums = []

    while url:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        #response.raise_for_status()
        if response.status_code != 200:
            print("\nERRO NA API DO SPOTIFY")
            print("Status:", response.status_code)
            print("Resposta:", response.text)
            return []

        data = response.json()

        albums.extend(data.get("items", []))

        url = data.get("next")
        params = None

    return albums


def main():
    token = get_access_token()

    for profile_name, artist_id in ARTIST_IDS.items():

        albums = get_artist_albums(artist_id, token)

        print("\n" + "=" * 70)
        print(profile_name)
        print("Artist ID:", artist_id)
        print("Total de álbuns retornados:", len(albums))
        print("=" * 70)

        for album in albums:
            print(
                f"{album.get('release_date')} | "
                f"{album.get('album_type')} | "
                f"{album.get('total_tracks')} faixas | "
                f"{album.get('name')}"
            )

        print("\n" + "-" * 70)


if __name__ == "__main__":
    main()
