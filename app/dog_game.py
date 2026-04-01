from __future__ import annotations

import dataclasses
import logging
import math

from app import dog_card_def, dog_constants, dog_patch_cards

logging.basicConfig(level=logging.DEBUG)

dog_patch_cards.CardsPatcher().convert_cards()

INITIAL_NAME = ("Asterix", "Obelix", "Trubadix", "Idefix")


@dataclasses.dataclass
class PlayersCard:
    game_state: GameState
    id: int
    angle: int
    card_def_color: dog_card_def.CardDefColor
    x: int
    y: int
    order: int = 0

    def __post_init__(self) -> None:
        self.order = self.game_state.next_order()
        assert isinstance(self.id, int)
        assert isinstance(self.angle, int)
        assert isinstance(self.x, int)
        assert isinstance(self.y, int)
        assert isinstance(self.card_def_color, dog_card_def.CardDefColor)

    def move(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.order = self.game_state.next_order()

    def set_card(self, card_def_color: dog_card_def.CardDefColor) -> None:
        self.card_def_color = card_def_color

    @property
    def json_move(self) -> tuple[int, int, int, int]:
        return (self.id, int(self.angle), int(self.x), int(self.y))

    @property
    def json_all(self) -> tuple[int, int, int, int, str, str]:
        return (
            self.id,
            int(self.angle),
            int(self.x),
            int(self.y),
            self.card_def_color.filebase,
            self.card_def_color.description_i18n,
        )

    def __lt__(self, other: PlayersCard) -> bool:
        assert isinstance(other, PlayersCard)
        return self.order < other.order

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, PlayersCard)
        return self.order == other.order


@dataclasses.dataclass
class Marble:
    id: int
    x: int = 0
    y: int = 0

    def __post_init__(self) -> None:
        assert isinstance(self.id, int)
        assert isinstance(self.x, int)
        assert isinstance(self.y, int)

    def move(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def reset(self) -> None:
        self.x = 2 * self.id
        self.y = 1 * self.id

    @property
    def json(self) -> tuple[int, int, int]:
        return (self.id, int(self.x), int(self.y))


@dataclasses.dataclass
class GameState:
    game: Game
    room: str
    _order: int = 0
    _list_marbles: list[Marble] = []
    _game_dirty: bool = False
    _board_dirty: bool = False
    _list_cards: list[PlayersCard] = []

    def __post_init__(self) -> None:
        self._list_marbles = [Marble(id) for id in range(self.dgc.player_count * dog_constants.MARBLE_COUNT)]
        assert isinstance(self.room, str)
        assert isinstance(self._order, int)
        assert isinstance(self._list_marbles, list)
        assert isinstance(self._game_dirty, bool)
        assert isinstance(self._board_dirty, bool)
        assert isinstance(self._list_cards, list)
        self.reset()

    @property
    def dgc(self) -> dog_constants.DogGameConstants:
        return self.game.dgc

    @property
    def dbc(self) -> dog_constants.DogBoardConstants:
        return self.game.dbc

    def reset(self) -> None:
        self._game_dirty = True
        self._board_dirty = True
        self.list_player_names: list[str] = list(self.dgc.player_names_defaults)
        self._list_cards = []
        for marble in self._list_marbles:
            marble.reset()

        # self.__initializeCards()
        # self.__initializeMarbles()

    def next_order(self) -> int:
        self._order += 1
        return self._order

    def __initialize_cards(self, cards: int = 0) -> None:
        def generator():
            cardstack = dog_card_def.Cards()
            cardstack.shuffle(dog_constants.DOG_RANDOM.shuffle)
            for player_index in range(self.dgc.player_count):
                angle_deg = 360.0 * player_index / self.dgc.player_count
                player_angle = 2 * math.pi * player_index / self.dgc.player_count
                for card_index in range(cards):
                    card_center = self.dbc.list_card_center[card_index]
                    player_offset = 10  # The first player start with 10, then 20, ...
                    jid = player_offset * (1 + player_index) + card_index
                    card_center_rotated = math.e ** (complex(0, player_angle)) * card_center
                    x_initial = card_center_rotated.real
                    y_initial = card_center_rotated.imag
                    card_def_color = cardstack.pop_card()
                    yield PlayersCard(
                        game_state=self,
                        id=jid,
                        angle=angle_deg,
                        x=x_initial,
                        y=y_initial,
                        card_def_color=card_def_color,
                    )

        self._list_cards = list(generator())

    def board_dirty(self) -> None:
        self._game_dirty = True
        self._board_dirty = True

    def game_dirty(self) -> None:
        self._game_dirty = True

    def event_browser_connected(self, json: dict) -> None:
        self.game_dirty()

    def event_new_name(self, json: dict) -> None:
        idx = json["idx"]
        name = json["name"]
        self.list_player_names[idx] = name
        self.game_dirty()

    def event_button_pressed(self, json: dict) -> None:
        label = json["label"]
        method = f"button_{label.upper()}"
        f = getattr(self, method)
        assert f is not None
        f()

    def append_state(self, json: dict) -> None:
        if self._board_dirty:
            self.append_state_board(json)
            self.append_state_game(json)
            return

        if self._game_dirty:
            self.append_state_game(json)
            return

    def append_state_game(self, json: dict) -> None:
        self._game_dirty = False
        json["playerNames"] = self.list_player_names

        self._list_cards.sort()
        json["cards"] = [card.json_all for card in self._list_cards]

        json["marbles"] = [marble.json for marble in self._list_marbles]

    def move_card(self, jid: int, x: int, y: int) -> dict:
        def find_card():
            for card in self._list_cards:
                if card.id == jid:
                    return card
            raise ValueError("Card not found")

        card = find_card()
        card.move(x=x, y=y)
        return {"card": card.json_move}

    def move_marble(self, jid: int, x: int, y: int) -> dict:
        marble = self._list_marbles[jid]
        marble.move(x=x, y=y)
        return {"marble": marble.json}

    def append_state_board(self, json: dict) -> None:
        self._board_dirty = False

    def button_c(self) -> None:
        # Clean
        self.reset()
        self.game_dirty()

    def button_2(self) -> None:
        self.__initialize_cards(2)
        self.game_dirty()

    def button_3(self) -> None:
        self.__initialize_cards(3)
        self.game_dirty()

    def button_4(self) -> None:
        self.__initialize_cards(4)
        self.game_dirty()

    def button_5(self) -> None:
        self.__initialize_cards(5)
        self.game_dirty()

    def button_6(self) -> None:
        self.__initialize_cards(6)
        self.game_dirty()


class Game:
    def __init__(self, players: int, room: str):
        def get_dgc(player_count: int) -> dog_constants.DogGameConstants:
            for dgc in dog_constants.LIST_DOG_GAME_CONSTANTS:
                if dgc.player_count == player_count:
                    return dgc
            return dog_constants.DOG_GAME_CONSTANTS_2

        self.dgc = get_dgc(players)
        self.game_state = GameState(self, room)
        self.game_state.board_dirty()

    def append_state(self, json: dict) -> None:
        self.game_state.append_state(json)

    def move_card(self, jid: int, x: int, y: int) -> dict:
        return self.game_state.move_card(jid=jid, x=x, y=y)

    def move_marble(self, jid: int, x: int, y: int) -> dict:
        return self.game_state.move_marble(jid=jid, x=x, y=y)

    @property
    def dbc(self) -> dog_constants.DogBoardConstants:
        return self.dgc.dbc

    @property
    def room(self) -> str:
        return self.game_state.room
