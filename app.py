
import logging
import pathlib

import eventlet
import jinja2
import flask
import flask_session
import flask_socketio

import dog_constants
import dog_game

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent.absolute()

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SESSION_TYPE'] = 'filesystem'
app.jinja_env.undefined = jinja2.StrictUndefined

'''
https://medium.com/hackervalleystudio/weekend-project-part-1-creating-a-real-time-web-based-application-using-flask-vue-and-socket-b71c73f37df7
https://medium.com/hackervalleystudio/weekend-project-part-2-turning-flask-into-a-real-time-websocket-server-using-flask-socketio-ab6b45f1d896
https://medium.com/hackervalleystudio/weekend-project-part-3-centralizing-state-management-with-vuex-5f4387ebc144
'''
flask_session.Session(app)
params = dict(
    # ping_timeout=1000,
    # ping_interval=5000,
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False,
    async_mode='eventlet',
    # See: 5:22 in https://www.youtube.com/watch?v=OZ1yQTbtf5E
    # See: https://blog.miguelgrinberg.com/post/flask-socketio-and-the-user-session
    manage_session=False 
    # async_mode='threading'
)
# socketio = flask_socketio.SocketIO(app, ping_timeout=20, ping_interval=10)
socketio = flask_socketio.SocketIO(app, **params)

class Rooms:
    def __init__(self):
        self.d = {}

    def get(self, json: dict):
        room = json['room']
        game = self.d.get(room, None)
        if game is not None:
            return game
        players, group = room.split('-', 2)
        return self.initialize(players=int(players), group=group)

    def initialize(self, players: int, group: str):
        room = f'{players}-{group}'
        game = self.d.get(room, None)
        if game is not None:
            return game
        # TODO: The game already exists. Broadcast a reset.
        game = dog_game.Game(players=players, room=room)
        self.d[room] = game
        return game

rooms = Rooms()

@socketio.on('message')
def handleMessage(msg):
    if DEBUG:
        print(f'Message: {msg}\n')
    socketio.send(f'MESSAGE:{msg}', broadcast=True)

@socketio.on('event')
def handleEvent(json):
    if DEBUG:
        print(f'Json: {json}\n')
    try:
        if json['event'] == 'browserConnected':
            room = json['room']
            flask_socketio.join_room(room)

        game = rooms.get(json)
        game.event(json)
        json_command = {}
        game.appendState(json_command)
        socketio.send(json_command, json=True, room=game.room)
        # socketio.send(json_command, json=True, broadcast=True)
    except Exception as e:
        logging.error(f'******************* Error during game.event(): {e}')
        raise

@socketio.on('marble')
def handleMoveMarble(json: dict):
    if DEBUG:
        print(f'handleMoveMarble Json: {json}\n')
    game = rooms.get(json)
    id, x, y = json['marble']
    json_msg = game.moveMarble(id=id, x=x, y=y)
    socketio.send(json_msg, json=True, broadcast=True, room=game.room)

@socketio.on('moveCard')
def handleMoveCard(json: dict):
    if DEBUG:
        print(f'handleMoveCard Json: {json}\n')
    game = rooms.get(json)
    id, x, y = json['card']
    json_msg = game.moveCard(id=id, x=x, y=y)
    socketio.send(json_msg, json=True, broadcast=True, room=game.room)

@app.route('/')
def index():
    location = f'{flask.request.url_root}2/sandbox'
    return flask.redirect(location=location)

# dogspiel.ch/<players>/<room>
@app.route('/<int:players>/<string:group>')
def index_room(players: int, group: str):
    game = rooms.initialize(players=players, group=group)
    return flask.render_template('index.html', game=game)

@app.route('/favicon.ico')
def favicon():
    return flask.send_file(DIRECTORY_OF_THIS_FILE / 'static' / 'favicon.ico')

# https://riptutorial.com/flask/example/5832/receiving-json-from-an-http-request
@app.route('/debugjson', methods=['POST', 'GET']) 
def debugjson():
    content_type = flask.request.headers['Content-Type']
    if content_type == 'application/x-www-form-urlencoded':
        data_json = flask.json.loads(flask.request.get_data().decode("utf-8"))
        if DEBUG:
            print(f'debugjson: {data_json}\n')
        socketio.send(data_json, json=True, broadcast=True)
        return 'Yes'
    return 'No'

    # curl -X POST http://localhost:5000/debugjson -d @set_all_1.json 

# This is how to run a timer
#
# def timer_run():
#     while True:
#         str_time = time.strftime('%H:%M:%S')
#         data_json = {
#             "call_html": {
#                 "id": "#time",
#                 "calls": {
#                     "html": str_time
#                 }
#             }
#         }
#         socketio.send(data_json, json=True, broadcast=True)
#         eventlet.sleep(1.0)

if __name__ == '__main__':
    # eventlet.spawn(timer_run)

    socketio.run(app, host="0.0.0.0")
