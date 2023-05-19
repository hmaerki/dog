import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import dog_game

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


# @app.route("/favicon.ico")
# def favicon():
# return flask.send_file(DIRECTORY_OF_THIS_FILE / "static" / "favicon.ico")
if __name__ == "__main__":
    # uvicorn.run(
    #     app,
    #     host="0.0.0.0",
    #     port=8000,
    #     log_level="debug",
    #     debug=True,
    # )
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
        workers=1,
    )
