from flask import request, redirect
from flask import jsonify
from flask import Response
from base64 import b64encode
from datetime import datetime, timedelta
import requests as api_request
import json


CLIENT_ID = "d68e3b6c4ff5431ab1d5bc7808d1ec0b"
CLIENT_SECRET = "c7d41cb2f1424ac88f0bccdde873e7b2"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_AUTHORIZATION_URL = "https://accounts.spotify.com/authorize"
REDIRECT_URI = 'http://127.0.0.1:5002/callback/user_page'
SPOTIFY_USER_INFO = 'https://api.spotify.com/v1/me'


scopes = ["user-read-playback-state%20", "user-read-currently-playing%20", "user-modify-playback-state%20",
          "app-remote-control%20", "streaming%20", "playlist-read-collaborative%20", "playlist-modify-private%20",
          "playlist-modify-public%20","playlist-read-private%20", "user-read-birthdate%20", "user-read-email%20",
          "user-read-private%20", "user-library-read%20", "user-library-modify"]


#probably don't need this endpoint in this API should make front end do this
def login_to_spotify():
    return redirect(SPOTIFY_AUTHORIZATION_URL + "/?client_id=" + CLIENT_ID +
                    "&response_type=code&redirect_uri=" + REDIRECT_URI + "&scope=" + "".join(scopes))


def get_tokens_from_spotify():
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    response = api_request.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    return jsonify(access_token=response.json()['access_token'], refresh_token=response.json()['refresh_token'], expiry_time=response.json()['expires_in'])


def get_user_info_from_spotify():
    access_token = request.args['access_token']
    headers = {"Authorization": "Bearer {}".format(access_token)}
    response = api_request.get(SPOTIFY_USER_INFO, headers=headers).json()
    return jsonify(images=response['images'], email=response['email'], display_name=response['display_name'], country=response['country'],
                   id=response['id'])


def store_tokens():
    username = request.headers['username']
    access_token = request.headers['access_token']
    refresh_token = request.headers['refresh_token']
    expires_in = request.headers['expiry_time']
    with open('./user_data/user_data.json', 'r') as data_file:
        try:
            user_data = json.load(data_file)
        except ValueError:
            user_data = {}

    if len(user_data) > 5:
        user_data.pop(user_data.keys[0])

    user_data[username] = {"access_token": access_token, "refresh_token": refresh_token, "expires": (datetime.now() + timedelta(seconds=int(expires_in)-600)).__str__()}
    with open('./user_data/user_data.json', 'w') as data_file:
        json.dump(user_data, data_file)
    return Response(status=201)


def get_stored_tokens():
    username = request.args['username']
    with open('./user_data/user_data.json', 'r') as data_file:
        user_data = json.load(data_file)
    return jsonify(access_token=user_data[username]['access_token'], refresh_token=user_data[username]['refresh_token'], expires=user_data[username]['expires'])


def refresh_user_token():
    username = request.headers['username']
    refresh_token = request.args['refresh_token']

    with open('./user_data/user_data.json', 'r') as data_file:
        try:
            user_data = json.load(data_file)
        except ValueError:
            return Response('no user data stored', status=400)

    code_payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    base64encoded = b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    response = api_request.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers).json()
    new_access_token = response['access_token']
    expires_in = response['expires_in']

    user_data[username]['access_token'] = new_access_token
    user_data[username]['expires'] = (datetime.now() + timedelta(seconds=int(expires_in)-600)).__str__()

    with open('./user_data/user_data.json', 'w') as data_file:
        json.dump(user_data, data_file)
    return Response(status=201)
