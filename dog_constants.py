import pathlib
import random as r

import dog_constants_4
import dog_constants_6

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent.absolute()

# COUNT_PLAYER_CARDS_OBSOLETE = 6

MAX_PLAYERS = 6
MAX_CARDS_PER_PLAYER = 6
MARBLE_COUNT = 4

LIST_PLAYER_COUNT = (2, 4, 6)
LIST_BOARD_ID = (4, 6)
BOARD_CENTER = 0,0
BOARD_DIAMETER = 2000

class DogBoardConstants:
    def __init__(self, dbc_module: 'module'):
        self.BOARD_ID = dbc_module.BOARD_ID
        assert self.BOARD_ID in LIST_BOARD_ID
        self.SCALE = dbc_module.SCALE
        self.MARBLE_DIAMETER = dbc_module.MARBLE_DIAMETER
        self.CARD_SIZE = dbc_module.CARD_SIZE
        self.LIST_CARD_CENTER = dbc_module.LIST_CARD_CENTER

    @property
    def BOARD_DIRECTORY_RELATIVE(self):
        return DIRECTORY_OF_THIS_FILE / 'static' / f'board{self.BOARD_ID}'

class DogGameConstants:
    def __init__(self, player_count: int, dbc_module: 'module', player_names_default: list):
        assert player_count in LIST_PLAYER_COUNT
        
        self.PLAYER_COUNT = player_count
        self.PLAYER_NAMES_DEFAULTS = player_names_default
        self.dbc = DogBoardConstants(dbc_module)

        # Copy from globals
        self.BOARD_CENTER = BOARD_CENTER
        self.BOARD_DIAMETER = BOARD_DIAMETER

DOG_BOARD_CONSTANTS_4 = DogBoardConstants(dog_constants_4)
DOG_BOARD_CONSTANTS_6 = DogBoardConstants(dog_constants_6)
LIST_DOG_BOARD_CONSTANTS = (DOG_BOARD_CONSTANTS_4, DOG_BOARD_CONSTANTS_6)

DOG_GAME_CONSTANTS_2 = DogGameConstants(2, DOG_BOARD_CONSTANTS_4, ('Blau', 'Grün'))
DOG_GAME_CONSTANTS_4 = DogGameConstants(4, DOG_BOARD_CONSTANTS_4, ('Blau', 'Gelb', 'Grün', 'Rot'))
DOG_GAME_CONSTANTS_6 = DogGameConstants(6, DOG_BOARD_CONSTANTS_6, ('Grün', 'Rot', 'Weiss', 'Blau', 'Gelb', 'Schwarz'))
LIST_DOG_GAME_CONSTANTS = (DOG_GAME_CONSTANTS_2, DOG_GAME_CONSTANTS_4, DOG_GAME_CONSTANTS_6)


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
