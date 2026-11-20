
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_access_token():

    url = "https://accounts.spotify.com/api/token"

    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )

    response.raise_for_status()

    token_data = response.json()

    return token_data["access_token"]


if __name__ == "__main__":
    token = get_access_token()
    print("Spotify authentication successful!")
    print(f"Token received: {token[:10]}...")
