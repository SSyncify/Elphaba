from flask import request
from flask import jsonify
from flask import Response
from base64 import b64encode
import requests as api_request
import pymysql

db = pymysql.connect("localhost", "root", "496545Aa", "Accounts")
db_cursor = db.cursor()


CLIENT_ID = "cb00645fb09c42b7b68431b639091bcf"
CLIENT_SECRET = "4b1b65c712af4a9ebfd26485bec2a078"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_AUTHORIZATION_URL = "https://accounts.spotify.com/authorize"
REDIRECT_URI = 'http://127.0.0.1:3000/callback/redirect'
SPOTIFY_USER_INFO = 'https://api.spotify.com/v1/me'
DEFAULT_IMAGE_URL = "https://pngimage.net/wp-content/uploads/2018/05/default-user-png-1.png"


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
    if len(response["images"]) > 0:
        img = response["images"][0]['url']
    else:
        img = DEFAULT_IMAGE_URL
    return jsonify(images=img, email=response['email'], display_name=response['display_name'], country=response['country'],
                   id=response['id'])


def store_tokens():
    access_token = request.args['access_token']
    refresh_token = request.args['refresh_token']
    expires_in = request.args['expiry_time']
    images = request.args['images']
    display_name = request.args['display_name']

    prepared_stmt = "INSERT INTO users (uid, display_name, expiry, access_token, profile_image) VALUES (%s, %s, %s, %s, %s)"
    db_cursor.execute(prepared_stmt, (refresh_token, display_name, expires_in, access_token, images))
    return Response(status=201)


def get_stored_tokens():
    uid = request.args['uid']
    prepared_stmt = "SELECT * FROM users WHERE uid=%s"
    db_cursor.execute(prepared_stmt, uid)
    data = db_cursor.fetchall()
    Response(200)
    return jsonify(display_name=data[1], images=data[4], refresh_token=data[0], access_token=data[3], expires=data[2])


def refresh_user_token():
    refresh_token = request.args['refresh_token']

    code_payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    base64encoded = b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    response = api_request.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers).json()
    new_access_token = response['access_token']
    expires_in = response['expires_in']

    prepared_stmt = "UPDATE users SET access_token=%s, expiry=%s WHERE uid=%s"
    db_cursor.execute(prepared_stmt, (new_access_token, expires_in, refresh_token))
    return Response(status=201)
