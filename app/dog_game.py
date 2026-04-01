from __future__ import annotations

import logging
import math

from app import dog_cards, dog_constants, dog_patch_cards

logging.basicConfig(level=logging.DEBUG)

dog_patch_cards.CardsPatcher().convert_cards()

INITIAL_NAME = ("Asterix", "Obelix", "Trubadix", "Idefix")


class PlayersCard:
    def __init__(
        self,
        game_state: GameState,
        jid: int,
        angle: int,
        x_initial: int,
        y_initial: int,
        card: dog_cards.Card,
    ):
        self.__game_state = game_state
        self.id = jid
        self.__order = self.__game_state.next_order()
        self.__angle = angle
        self.__x = x_initial
        self.__y = y_initial
        self.__card = card

    def move(self, x: int, y: int) -> None:
        self.__x = x
        self.__y = y
        self.__order = self.__game_state.next_order()

    def set_card(self, card: dog_cards.Card) -> None:
        self.__card = card

    @property
    def json_move(self) -> tuple[int, int, int, int]:
        return (self.id, int(self.__angle), int(self.__x), int(self.__y))

    @property
    def json_all(self) -> tuple[int, int, int, int, str, str]:
        return (
            self.id,
            int(self.__angle),
            int(self.__x),
            int(self.__y),
            self.__card.filebase,
            self.__card.description_i18n,
        )

    def __lt__(self, other: PlayersCard) -> bool:
        return self.__order < other.__order

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlayersCard):
            return NotImplemented  # type: ignore[return-value]
        return self._PlayersCard__order == other._PlayersCard__order  # type: ignore[attr-defined]


class Marble:
    def __init__(self, jid: int):
        self.id = jid
        self.reset()
        self.__x = 0
        self.__y = 0

    def move(self, x: int, y: int) -> None:
        self.__x = x
        self.__y = y

    def reset(self) -> None:
        self.__x = 2 * self.id
        self.__y = 1 * self.id

    @property
    def json(self) -> tuple[int, int, int]:
        return (self.id, int(self.__x), int(self.__y))


class GameState:
    def __init__(self, game: Game, room: str):
        self.game: Game = game
        self.room: str = room
        self.__order: int = 0
        self.__list_marbles: list[Marble] = [
            Marble(id) for id in range(self.dgc.player_count * dog_constants.MARBLE_COUNT)
        ]
        self.reset()
        self.__game_dirty: bool = False
        self.__board_dirty: bool = False
        self.__list_cards: list[PlayersCard] = []

    @property
    def dgc(self) -> dog_constants.DogGameConstants:
        return self.game.dgc

    @property
    def dbc(self) -> dog_constants.DogBoardConstants:
        return self.game.dbc

    # @property
    # def card_filebases(self) -> list:
    #     return ';'.join([card.filebase for card in self.cards.all])

    def reset(self) -> None:
        self.__game_dirty = True
        self.__board_dirty = True
        self.list_player_names: list[str] = list(self.dgc.player_names_defaults)
        self.__list_cards = []
        for marble in self.__list_marbles:
            marble.reset()

        # self.__initializeCards()
        # self.__initializeMarbles()

    def next_order(self) -> int:
        self.__order += 1
        return self.__order

    def __initialize_cards(self, cards: int = 0) -> None:
        def generator():
            cardstack = dog_cards.Cards()
            cardstack.shuffle(dog_constants.dogRandom.shuffle)
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
                    card = cardstack.pop_card()
                    yield PlayersCard(
                        game_state=self,
                        jid=jid,
                        angle=angle_deg,
                        x_initial=x_initial,
                        y_initial=y_initial,
                        card=card,
                    )

        self.__list_cards = list(generator())

    # def __initialize_marbles(self) -> None:
    #     for marble in self.__list_marbles:
    #         marble.reset()

    def board_dirty(self) -> None:
        self.__game_dirty = True
        self.__board_dirty = True

    def game_dirty(self) -> None:
        self.__game_dirty = True

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
        if self.__board_dirty:
            self.append_state_board(json)
            self.append_state_game(json)
            return

        if self.__game_dirty:
            self.append_state_game(json)
            return

    def append_state_game(self, json: dict) -> None:
        self.__game_dirty = False
        json["playerNames"] = self.list_player_names

        self.__list_cards.sort()
        json["cards"] = [card.json_all for card in self.__list_cards]

        json["marbles"] = [marble.json for marble in self.__list_marbles]

    def move_card(self, jid: int, x: int, y: int) -> dict:
        def find_card():
            for card in self.__list_cards:
                if card.id == jid:
                    return card
            raise ValueError("Card not found")

        card = find_card()
        card.move(x=x, y=y)
        return {"card": card.json_move}

    def move_marble(self, jid: int, x: int, y: int) -> dict:
        marble = self.__list_marbles[jid]
        marble.move(x=x, y=y)
        return {"marble": marble.json}

    def append_state_board(self, json: dict) -> None:
        self.__board_dirty = False

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
