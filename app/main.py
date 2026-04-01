from __future__ import annotations

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
    def __init__(self) -> None:
        self.d: dict[str, dog_game.Game] = {}

    def get(self, json: dict[str, object]) -> dog_game.Game:
        room = json["room"]
        assert isinstance(room, str)
        game = self.d.get(room, None)
        if game is not None:
            return game
        players, group = room.split("-", 2)
        return self.initialize(players=int(players), group=group)

    def initialize(self, players: int, group: str) -> dog_game.Game:
        room = f"{players}-{group}"
        game = self.d.get(room, None)
        if game is not None:
            return game
        # The game already exists. Broadcast a reset.
        game = dog_game.Game(players=players, room=room)
        self.d[room] = game
        return game


rooms = Rooms()


class ConnectionManager:
    def __init__(self) -> None:
        self.room_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str) -> None:
        await websocket.accept()
        self.room_connections.setdefault(room, []).append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        for connections in self.room_connections.values():
            if websocket in connections:
                connections.remove(websocket)
                return

    def move_to_game_room(self, websocket: WebSocket, game_room: str) -> None:
        """Re-register a websocket under the authoritative game room."""
        # Remove from any existing room
        for connections in self.room_connections.values():
            if websocket in connections:
                connections.remove(websocket)
                break
        # Add to game room
        self.room_connections.setdefault(game_room, []).append(websocket)

    async def broadcast_room(self, json_data: dict[str, object], room: str) -> None:
        for connection in list(self.room_connections.get(room, [])):
            await connection.send_json(json_data)


manager = ConnectionManager()


@app.get("/")
async def redirect_typer() -> RedirectResponse:
    return RedirectResponse("2/sandbox")


@app.get("/{players}/{group}", response_class=HTMLResponse)
async def index_room(request: Request, players: int, group: str):
    game = rooms.initialize(players=players, group=group)
    context = {
        "request": request,
        "game": game,
    }
    return templates.TemplateResponse(request, "index.html", context=context)


async def handler(websocket: WebSocket) -> None:
    json_msg = await websocket.receive_json()
    event = json_msg["event"]
    assert isinstance(event, str)

    if event == "browserConnected":
        room = rooms.get(json_msg)
        manager.move_to_game_room(websocket, room.room)
        room.game_state.event_browser_connected(json_msg)
        browser_connected_command: dict[str, object] = {}
        room.append_state(browser_connected_command)
        await websocket.send_json(browser_connected_command)
        return

    if event == "newName":
        room = rooms.get(json_msg)
        room.game_state.event_new_name(json_msg)
        new_name_command: dict[str, object] = {}
        room.append_state(new_name_command)
        await manager.broadcast_room(new_name_command, room.room)
        return

    if event == "buttonPressed":
        room = rooms.get(json_msg)
        room.game_state.event_button_pressed(json_msg)
        button_pressed_command: dict[str, object] = {}
        room.append_state(button_pressed_command)
        await manager.broadcast_room(button_pressed_command, room.room)
        return

    if event == "marble":
        if DEBUG:
            print(f"handleMoveMarble Json: {json_msg}")
        room = rooms.get(json_msg)
        jid, x, y = json_msg["marble"]
        json_response = room.move_marble(jid=jid, x=x, y=y)
        if DEBUG:
            print(f"broadcast_room target={room.room!r} connections={list(manager.room_connections.keys())}\n")
        await manager.broadcast_room(json_response, room.room)
        return

    if event == "moveCard":
        if DEBUG:
            print(f"handleMoveCard Json: {json_msg}")
        room = rooms.get(json_msg)
        jid, x, y = json_msg["card"]
        json_response = room.move_card(jid=jid, x=x, y=y)
        await manager.broadcast_room(json_response, room.room)
        return

    if event == "message":
        if DEBUG:
            print(f"Message: {json_msg}")
        room = rooms.get(json_msg)
        await manager.broadcast_room({"message": {json_msg}}, room.room)
        return


@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            await handler(websocket=websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
