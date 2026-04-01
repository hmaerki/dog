from __future__ import annotations

import pathlib
import random as r
from collections.abc import Sequence
import dataclasses

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent.absolute()

# COUNT_PLAYER_CARDS_OBSOLETE = 6

MAX_PLAYERS = 6
MAX_CARDS_PER_PLAYER = 6
MARBLE_COUNT = 4

LIST_PLAYER_COUNT = (2, 4, 6)
LIST_BOARD_ID = (4, 6)
BOARD_CENTER = 0, 0
BOARD_DIAMETER = 2000


@dataclasses.dataclass
class DogBoardConstants:
    BOARD_ID: int
    SCALE: float
    MARBLE_DIAMETER: float
    CARD_SIZE: complex
    LIST_CARD_CENTER: tuple[complex, ...]
    OPACITY_PARAM_D: float
    OPACITY_PARAM_B: float
    OPACITY_PARAM_J: float

    @property
    def BOARD_DIRECTORY_RELATIVE(self):
        return DIRECTORY_OF_THIS_FILE / "static" / f"board{self.BOARD_ID}"


# Imported after DogBoardConstants to avoid circular imports


class DogGameConstants:
    def __init__(
        self,
        player_count: int,
        dbc: DogBoardConstants,
        player_names_default: Sequence[str],
    ):
        assert player_count in LIST_PLAYER_COUNT

        self.PLAYER_COUNT = player_count
        self.PLAYER_NAMES_DEFAULTS = player_names_default
        self.dbc = dbc

        # Copy from globals
        self.BOARD_CENTER = BOARD_CENTER
        self.BOARD_DIAMETER = BOARD_DIAMETER


DOG_BOARD_CONSTANTS_4 = DogBoardConstants(
    BOARD_ID=4,
    SCALE=0.563380281690141,
    MARBLE_DIAMETER=9.01408450704225,
    CARD_SIZE=complex(31.5492957746479, 50.1408450704225),
    LIST_CARD_CENTER=(
        complex(-22.5352112676056, 132.957746478873),
        complex(22.5352112676056, 132.957746478873),
        complex(-47.3239436619718, 126.760563380282),
        complex(47.3239436619718, 126.760563380282),
        complex(-69.2957746478873, 119.43661971831),
        complex(69.2957746478873, 119.43661971831),
    ),
    OPACITY_PARAM_D=28.169014084507,
    OPACITY_PARAM_B=107.042253521127,
    OPACITY_PARAM_J=90.1408450704225,
)


DOG_BOARD_CONSTANTS_6 = DogBoardConstants(
    BOARD_ID=6,
    SCALE=0.43956043956044,
    MARBLE_DIAMETER=7.03296703296703,
    CARD_SIZE=complex(24.6153846153846, 39.1208791208791),
    LIST_CARD_CENTER=(
        complex(-13.1868131868132, 132.747252747253),
        complex(13.1868131868132, 132.747252747253),
        complex(-29.8901098901099, 126.153846153846),
        complex(29.8901098901099, 126.153846153846),
        complex(-44.3956043956044, 120.879120879121),
        complex(44.3956043956044, 120.879120879121),
    ),
    OPACITY_PARAM_D=45.0704225352113,
    OPACITY_PARAM_B=84.5070422535211,
    OPACITY_PARAM_J=126.760563380282,
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
        self.__mockMode = False
        self.__mockSeed = 0

    def seed(self, a, mockMode: bool) -> None:
        self.__mockMode = mockMode
        self.__mockSeed = a

    def shuffle(self, elements: list) -> None:
        if self.__mockMode:
            return
        r.shuffle(elements)

    def randint(self, a: int, b: int) -> int:
        if self.__mockMode:
            return a
        return r.randint(a, b)


dogRandom = DogRandom()
