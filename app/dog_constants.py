from __future__ import annotations

import pathlib
import random as r
from collections.abc import Sequence
import dataclasses

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent.absolute()

MAX_PLAYERS = 6
MAX_CARDS_PER_PLAYER = 6
MARBLE_COUNT = 4

LIST_PLAYER_COUNT = (2, 4, 6)
LIST_BOARD_ID = (4, 6)
BOARD_CENTER = 0, 0
BOARD_DIAMETER = 2000


@dataclasses.dataclass
class DogBoardConstants:
    board_id: int
    scale: float
    marble_diameter: float
    card_size: complex
    list_card_center: tuple[complex, ...]
    opacity_param_d: float
    opacity_param_b: float
    opacity_param_j: float

    @property
    def board_directory_relative(self) -> pathlib.Path:
        return DIRECTORY_OF_THIS_FILE / "static" / f"board{self.board_id}"


class DogGameConstants:
    def __init__(
        self,
        player_count: int,
        dbc: DogBoardConstants,
        player_names_default: Sequence[str],
    ):
        assert player_count in LIST_PLAYER_COUNT

        self.player_count: int = player_count
        self.player_names_defaults: Sequence[str] = player_names_default
        self.dbc: DogBoardConstants = dbc

        # Copy from globals
        self.board_center: tuple[int, int] = BOARD_CENTER
        self.board_diameter: int = BOARD_DIAMETER


DOG_BOARD_CONSTANTS_4 = DogBoardConstants(
    board_id=4,
    scale=0.563380281690141,
    marble_diameter=9.01408450704225,
    card_size=complex(31.5492957746479, 50.1408450704225),
    list_card_center=(
        complex(-22.5352112676056, 132.957746478873),
        complex(22.5352112676056, 132.957746478873),
        complex(-47.3239436619718, 126.760563380282),
        complex(47.3239436619718, 126.760563380282),
        complex(-69.2957746478873, 119.43661971831),
        complex(69.2957746478873, 119.43661971831),
    ),
    opacity_param_d=28.169014084507,
    opacity_param_b=107.042253521127,
    opacity_param_j=90.1408450704225,
)


DOG_BOARD_CONSTANTS_6 = DogBoardConstants(
    board_id=6,
    scale=0.43956043956044,
    marble_diameter=7.03296703296703,
    card_size=complex(24.6153846153846, 39.1208791208791),
    list_card_center=(
        complex(-13.1868131868132, 132.747252747253),
        complex(13.1868131868132, 132.747252747253),
        complex(-29.8901098901099, 126.153846153846),
        complex(29.8901098901099, 126.153846153846),
        complex(-44.3956043956044, 120.879120879121),
        complex(44.3956043956044, 120.879120879121),
    ),
    opacity_param_d=45.0704225352113,
    opacity_param_b=84.5070422535211,
    opacity_param_j=126.760563380282,
)

DOG_GAME_CONSTANTS_2 = DogGameConstants(
    2,
    DOG_BOARD_CONSTANTS_4,
    ("Blau", "Grün"),
)
DOG_GAME_CONSTANTS_4 = DogGameConstants(
    4,
    DOG_BOARD_CONSTANTS_6,
    ("Blau", "Gelb", "Grün", "Rot"),
)
DOG_GAME_CONSTANTS_6 = DogGameConstants(
    6,
    DOG_BOARD_CONSTANTS_6,
    ("Grün", "Rot", "Weiss", "Blau", "Gelb", "Schwarz"),
)
LIST_DOG_GAME_CONSTANTS = (
    DOG_GAME_CONSTANTS_2,
    DOG_GAME_CONSTANTS_4,
    DOG_GAME_CONSTANTS_6,
)


class DogRandom:
    def __init__(self):
        self.__mock_mode = False
        self.__mock_seed = 0

    def seed(self, a: int, mock_mode: bool) -> None:
        self.__mock_mode = mock_mode
        self.__mock_seed = a

    def shuffle(self, elements: list) -> None:
        if self.__mock_mode:
            return
        r.shuffle(elements)

    def randint(self, a: int, b: int) -> int:
        if self.__mock_mode:
            return a
        return r.randint(a, b)


dogRandom: DogRandom = DogRandom()
