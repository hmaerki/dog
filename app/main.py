import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import dog_game

DEBUG = False

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


class Rooms:
    def __init__(self):
        self.d = {}

    def get(self, json: dict):
        room = json["room"]
        game = self.d.get(room, None)
        if game is not None:
            return game
        players, group = room.split("-", 2)
        return self.initialize(players=int(players), group=group)

    def initialize(self, players: int, group: str):
        room = f"{players}-{group}"
        game = self.d.get(room, None)
        if game is not None:
            return game
        # TODO: The game already exists. Broadcast a reset.
        game = dog_game.Game(players=players, room=room)
        self.d[room] = game
        return game


rooms = Rooms()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


# @app.route("/")
# def index():
#     location = f"{flask.request.url_root}2/sandbox"
#     return flask.redirect(location=location)
@app.get("/")
async def redirect_typer():
    return RedirectResponse("2/sandbox")


# dogspiel.ch/<players>/<room>
# @app.route("/<int:players>/<string:group>")
# def index_room(players: int, group: str):
#     game = rooms.initialize(players=players, group=group)
#     return flask.render_template("index.html", game=game)
@app.get("/{players}/{group}", response_class=HTMLResponse)
async def index_room(request: Request, players: int, group: str):
    game = rooms.initialize(players=players, group=group)
    context = dict(
        request=request,
        game=game,
    )
    return templates.TemplateResponse("index.html", context=context)


async def handler(websocket) -> None:
    json_websocket = await websocket.receive_json()
    json_event = json_websocket["event"]
    assert isinstance(json_event, str)
    json = json_websocket["msg"]
    assert isinstance(json, dict)

    if json_event == "event":
        if json["event"] == "browserConnected":
            room = json["room"]
            flask_socketio.join_room(room)

        game = rooms.get(json)
        game.event(json)
        json_command = {}
        game.appendState(json_command)
        await websocket.send_json(json_command)
        return

    if json_event == "marble":
        if DEBUG:
            print(f"handleMoveMarble Json: {json}\n")
        game = rooms.get(json)
        id, x, y = json["marble"]
        json_msg = game.moveMarble(id=id, x=x, y=y)
        # socketio.send(json_msg, json=True, broadcast=True, room=game.room)
        # Broadcast
        await websocket.send_json(json_msg)
        return

    if json_event == "moveCard":
        if DEBUG:
            print(f"handleMoveCard Json: {json}\n")
        game = rooms.get(json)
        id, x, y = json["card"]
        json_msg = game.moveCard(id=id, x=x, y=y)
        # socketio.send(json_msg, json=True, broadcast=True, room=game.room)
        # Broadcast
        await websocket.send_json(json_msg)
        return

    if json_event == "message":
        if DEBUG:
            print(f"Message: {json}\n")
        # socketio.send(f"MESSAGE:{msg}", broadcast=True)
        # Broadcast
        await websocket.send_json(f"MESSAGE:{json}", broadcast=True)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            await handler(websocket=websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


@app.websocket("/wsx/{client_id}")
async def websocket_endpointx(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
