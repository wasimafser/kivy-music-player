import requests
import base64
import re

SPOTIFY_CLIENT_ID = "<client_id>"
SPOTIFY_CLIENT_SECRET = "<client_secret>"

# API_TOKEN = ""
# TOKEN_TYPE = ""

def get_encoded_auth_header():
    return base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode("ascii")).decode("ascii")

response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        headers={"Authorization": f"Basic {get_encoded_auth_header()}"},
        verify=True,
        timeout=2,
    ).json()

API_TOKEN = response['access_token']
TOKEN_TYPE = response['token_type']

def extract_image_data(image_url):
    response = requests.get(image_url)
    return response.content

def get_artist_info(artist, search=False):
    artist_info = {
        'spotify_id': None,
        'image': None
    }
    if search:
        response = requests.get(
            url="https://api.spotify.com/v1/search",
            headers={"Authorization": f"{TOKEN_TYPE} {API_TOKEN}"},
            params={
                'q': artist,
                'type': 'artist',
                'limit': 1
            }
        ).json()

        try:
            artist_info['spotify_id'] = response['artists']['items'][0]['id']
            artist_info['image'] = extract_image_data(response['artists']['items'][0]['images'][0]['url'])
        except Exception as e:
            print(e)

        return artist_info

def get_album_info(album, search=False):
    album_info = {
        'spotify_id': None,
        'image': None
    }
    if search:
        album = re.sub(r'\([^()]*\)', '', album)
        response = requests.get(
            url="https://api.spotify.com/v1/search",
            headers={"Authorization": f"{TOKEN_TYPE} {API_TOKEN}"},
            params={
                'q': album,
                'type': 'album',
                'limit': 1
            }
        ).json()

        try:
            album_info['spotify_id'] = response['albums']['items'][0]['id']
            album_info['image'] = extract_image_data(response['albums']['items'][0]['images'][0]['url'])
        except Exception as e:
            print(e)

        return album_info
