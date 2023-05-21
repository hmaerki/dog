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


@app.get("/")
async def redirect_typer():
    return RedirectResponse("2/sandbox")


@app.get("/{players}/{group}", response_class=HTMLResponse)
async def index_room(request: Request, players: int, group: str):
    game = rooms.initialize(players=players, group=group)
    context = dict(
        request=request,
        game=game,
    )
    return templates.TemplateResponse("index.html", context=context)


async def handler(websocket) -> None:
    json_msg = await websocket.receive_json()
    event = json_msg["event"]
    assert isinstance(event, str)

    if event == "browserConnected":
        game = rooms.get(json_msg)
        game.gameState.event_browserConnected(json_msg)
        json_command = {}
        game.appendState(json_command)
        await websocket.send_json(json_command)
        return

    if event == "newName":
        game = rooms.get(json_msg)
        game.gameState.event_newName(json_msg)
        json_command = {}
        game.appendState(json_command)
        await websocket.send_json(json_command)
        return

    if event == "buttonPressed":
        game = rooms.get(json_msg)
        game.gameState.event_buttonPressed(json_msg)
        json_command = {}
        game.appendState(json_command)
        await websocket.send_json(json_command)
        return

    if event == "marble":
        if DEBUG:
            print(f"handleMoveMarble Json: {json_msg}\n")
        game = rooms.get(json_msg)
        id, x, y = json_msg["marble"]
        json_msg = game.moveMarble(id=id, x=x, y=y)
        # socketio.send(json_msg, json=True, broadcast=True, room=game.room)
        # Broadcast
        await websocket.send_json(json_msg)
        return

    if event == "moveCard":
        if DEBUG:
            print(f"handleMoveCard Json: {json_msg}\n")
        game = rooms.get(json_msg)
        id, x, y = json_msg["card"]
        json_msg = game.moveCard(id=id, x=x, y=y)
        # socketio.send(json_msg, json=True, broadcast=True, room=game.room)
        # Broadcast
        await websocket.send_json(json_msg)
        return

    if event == "message":
        if DEBUG:
            print(f"Message: {json_msg}\n")
        # socketio.send(f"MESSAGE:{msg}", broadcast=True)
        # Broadcast
        await websocket.send_json(f"MESSAGE:{json_msg}", broadcast=True)
        return


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
