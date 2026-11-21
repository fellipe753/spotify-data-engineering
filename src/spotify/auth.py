
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_access_token():

    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError(
            "Spotify credentials not configured. "
            "Check SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET."
        )

    url = "https://accounts.spotify.com/api/token"

    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=30
    )

    response.raise_for_status()

    token_data = response.json()

    return token_data["access_token"]


if __name__ == "__main__":
    get_access_token()
    print("Spotify authentication successful!")
