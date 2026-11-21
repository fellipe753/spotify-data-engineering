
import requests
from auth import get_access_token

ARTIST_IDS = [
    "5M52tdBnJaKSvOpJGz8mfZ",
    "7KwFSSDsXWVmiJjeuYCgx3"
]

def get_artist_details(artist_id, token):
    url = f"https://api.spotify.com/v1/artists/{artist_id}"

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    response.raise_for_status()
    return response.json()


def main():
    token = get_access_token()

    for artist_id in ARTIST_IDS:
        artist = get_artist_details(artist_id, token)

        print("\n" + "=" * 60)
        print("ARTIST PROFILE")
        print("=" * 60)

        print("ID:", artist["id"])
        print("Name:", artist["name"])
        print("Spotify URL:", artist["external_urls"].get("spotify"))
        print("Followers:", artist.get("followers", {}).get("total", "Not available"))
        print("Popularity:", artist.get("popularity", "Not available"))
        print("Genres:", artist.get("genres", "Not available"))

        print("Images:")

        for image in artist.get("images", []):
            print(image.get("url"))

    print("\nComparison completed!")


if __name__ == "__main__":
    main()
