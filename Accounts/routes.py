from flask import Flask
from flask import request
from flask_socketio import SocketIO
from controllers import authentication_controllers
import json

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


@socketio.on("user_connected")
def handle_user_connect(display_name, sid):
    print("USER CONNECTED")
    print(sid)
    with open("./user_data/connected_users.json", "r") as connected_file:
        try:
            connected_users = json.load(connected_file)
            if len(connected_users) > 5:
                connected_users['users'][0] = {'display_name': display_name["display_name"], 'sid': sid['sid']}
                socketio.emit('list_users', connected_users)
            else:
                socketio.emit('list_users', connected_users)
                connected_users['users'].append({'display_name': display_name["display_name"], 'sid': sid['sid']})
        except ValueError:
            connected_users = {'users': [{'display_name': display_name["display_name"], 'sid': sid['sid']}]}
    with open("./user_data/connected_users.json", "w") as connected_file:
        json.dump(connected_users, connected_file)
        socketio.emit('user_connected', connected_users, broadcast=True, include_self=False)


@socketio.on("disconnect")
def handle_user_disconnect():
    print('DISCONNECT DETECTED')
    user_sid = request.sid
    with open("./user_data/connected_users.json") as connected_file:
        connected_users = json.load(connected_file)
    for i in range(len(connected_users['users'])):
        if connected_users['users'][i]['sid'] == user_sid:
            connected_users['users'].pop(i)
    with open("./user_data/connected_users.json", "w") as connected_file:
        json.dump(connected_users, connected_file)
        socketio.emit('user_disconnected', connected_users, broadcast=True, include_self=False)


if __name__ == '__main__':
    print("listening on 5002")
    socketio.run(app, port=5002)
