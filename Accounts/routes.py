from flask import Flask
from flask_socketio import SocketIO
from controllers import authentication_controllers

app = Flask(__name__, static_folder='.')
socketio = SocketIO(app)


# ACCOUNTS ROUTES
@app.route('/username')
def get_username():
    '''
    GET REQUEST
    requires access token parameter, returns username of user with given access token
    '''
    return authentication_controllers.get_user_info_from_spotify()


@app.route('/generate_tokens')
def get_user_tokens():
    '''
    GET REQUEST
    requires "code" parameter to be sent, sends request to spotify api and returns access and refresh tokens
    '''
    return authentication_controllers.get_tokens_from_spotify()


@app.route('/store_token', methods=['POST'])
def store_user_tokens():
    '''
    POST REQUEST
    no required params, requires headers: username, access_token, refresh_token and expiry time. Stores tokens for given user.
    '''
    return authentication_controllers.store_tokens()


@app.route('/get_stored_info')
def get_stored_user_info():
    '''
    GET REQUEST
    requires username parameter, retrieves stored user tokens and returns to caller
    '''
    return authentication_controllers.get_stored_tokens()


@app.route('/refresh_stored_token', methods=['PUT'])
def refresh_stored_token():
    '''
    refershed stored access token, refresh_token parameter required. username Header required.
    '''
    return authentication_controllers.refresh_user_token()


if __name__ == '__main__':
    socketio.run(app, port=5002)
