
import math
import typing
import logging

import dog_cards
import dog_constants
import dog_patch_cards

logging.basicConfig(level=logging.DEBUG)

dog_patch_cards.CardsPatcher().convert_cards()

INITIAL_NAME = ('Asterix', 'Obelix', 'Trubadix', 'Idefix')

class PlayersCard:
    def __init__(self, gameState: 'GameState', id: int, angle: int, x_initial: int, y_initial: int, card: dog_cards.Card):
        self.__gameState = gameState
        self.id = id
        self.__order = self.__gameState.nextOrder()
        self.__angle = angle
        self.__x = x_initial
        self.__y = y_initial
        self.__x_initial = x_initial
        self.__y_initial = y_initial
        self.__card = card

    def move(self, x:int, y:int):
        self.__x = x
        self.__y = y
        self.__order = self.__gameState.nextOrder()

    def setCard(self, card: dog_cards.Card):
        self.__card = card

    @property
    def jsonMove(self):
        return (self.id, int(self.__angle), int(self.__x), int(self.__y))

    @property
    def jsonAll(self):
        return (self.id, int(self.__angle), int(self.__x), int(self.__y), self.__card.filebase, self.__card.descriptionI18N)

    def __lt__(self, other):
        return self.__order < other.__order
    
    def __eq__(self, other):
        return self.__order == other.__order

class Marble:
    def __init__(self, id:int):
        self.id = id
        self.reset()

    def move(self, x:int, y:int):
        self.__x = x
        self.__y = y

    def reset(self):
        self.__x = 2*self.id
        self.__y = 1*self.id

    @property
    def json(self):
        return (self.id, int(self.__x), int(self.__y))

class GameState:
    def __init__(self, game: 'Game', room: str):
        self.game = game
        self.room = room
        self.__order = 0
        self.__list_marbles = [Marble(id) for id in range(self.dgc.PLAYER_COUNT*dog_constants.MARBLE_COUNT)]
        self.reset()
        self.__game_dirty = False
        self.__board_dirty = False

    @property
    def dgc(self) -> dog_constants.DogGameConstants:
        return self.game.dgc

    @property
    def dbc(self) -> dog_constants.DogGameConstants:
        return self.game.dbc

    # @property
    # def card_filebases(self) -> list:
    #     return ';'.join([card.filebase for card in self.cards.all])

    def reset(self) -> None:
        self.__game_dirty = True
        self.__board_dirty = True
        self.list_player_names = list(self.dgc.PLAYER_NAMES_DEFAULTS)
        self.__list_cards = []
        for marble in self.__list_marbles:
            marble.reset()

        # self.__initializeCards()
        # self.__initializeMarbles()

    def nextOrder(self) -> int:
        self.__order += 1
        return self.__order

    def __initializeCards(self, cards=0):
        def generator():
            cardstack = dog_cards.Cards()
            cardstack.shuffle(dog_constants.dogRandom.shuffle)
            for playerIndex in range(self.dgc.PLAYER_COUNT):
                angleDeg = 360.0 * playerIndex / self.dgc.PLAYER_COUNT
                playerAngle = 2 * math.pi * playerIndex / self.dgc.PLAYER_COUNT
                for cardIndex in range(cards):
                    cardCenter = self.dbc.LIST_CARD_CENTER[cardIndex]
                    PLAYER_OFFSET = 10  # The first player start with 10, then 20, ...
                    id = PLAYER_OFFSET*(1+playerIndex) + cardIndex
                    cardCenterRotated = math.e**(complex(0, playerAngle)) * cardCenter
                    x_initial = cardCenterRotated.real
                    y_initial = cardCenterRotated.imag
                    card = cardstack.pop_card()
                    yield PlayersCard(gameState=self, id=id, angle=angleDeg, x_initial=x_initial, y_initial=y_initial, card=card)

        self.__list_cards = list(generator())

    def __initializeMarbles(self):
        for marble in self.__list_marbles:
            marble.middle()

    def boardDirty(self):
        self.__game_dirty = True
        self.__board_dirty = True

    def gameDirty(self):
        self.__game_dirty = True

    def event(self, json: str) -> typing.Optional[str]:
        if json['event'] == 'browserConnected':
            self.gameDirty()
            return

        if json['event'] == 'newName':
            idx = json['idx']
            name = json['name']
            self.list_player_names[idx] = name
            self.gameDirty()

        if json['event'] == 'buttonPressed':
            label = json['label']
            method = f'button_{label.upper()}'
            f = getattr(self, method)
            assert f is not None
            f()

    def appendState(self, json: dict) -> None:
        if self.__board_dirty:
            self.appendStateBoard(json)
            self.appendStateGame(json)
            return

        if self.__game_dirty:
            self.appendStateGame(json)
            return

    def appendStateGame(self, json: dict) -> None:
        self.__game_dirty = False
        json['playerNames'] = self.list_player_names

        self.__list_cards.sort()
        json['cards'] = [card.jsonAll for card in self.__list_cards]

        json['marbles'] = [marble.json for marble in self.__list_marbles]

    def moveCard(self, id:int, x:int, y:int) -> dict:
        def findCard():
            for card in self.__list_cards:
                if card.id == id:
                    return card
            raise Exception('Card not found')

        card = findCard()
        card.move(x=x, y=y)
        return { 'card': card.jsonMove }

    def moveMarble(self, id:int, x:int, y:int) -> dict:
        marble = self.__list_marbles[id]
        marble.move(x=x, y=y)
        return { 'marble': marble.json }

    def appendStateBoard(self, json: dict) -> None:
        self.__board_dirty = False

    def button_C(self):
        # Clean
        self.reset()
        self.gameDirty()

    def button_2(self):
        self.__initializeCards(2)
        self.gameDirty()

    def button_3(self):
        self.__initializeCards(3)
        self.gameDirty()

    def button_4(self):
        self.__initializeCards(4)
        self.gameDirty()

    def button_5(self):
        self.__initializeCards(5)
        self.gameDirty()

    def button_6(self):
        self.__initializeCards(6)
        self.gameDirty()

class Game:
    def __init__(self, players: int, room: str):
        def getDgc(playerCount):
            for dgc in dog_constants.LIST_DOG_GAME_CONSTANTS:
                if dgc.PLAYER_COUNT == playerCount:
                    return dgc
            return dog_constants.DOG_GAME_CONSTANTS_2
        self.dgc = getDgc(players)
        self.gameState = GameState(self, room)
        self.gameState.boardDirty()

    def event(self, json: str) -> typing.Optional[str]:
        return self.gameState.event(json)

    def appendState(self, json: dict) -> None:
        self.gameState.appendState(json)

    def moveCard(self, id:int, x:int, y:int) -> dict:
        return self.gameState.moveCard(id=id, x=x, y=y)

    def moveMarble(self, id:int, x:int, y:int) -> dict:
        return self.gameState.moveMarble(id=id, x=x, y=y)

    @property
    def dbc(self) -> dog_constants.DogBoardConstants:
        return self.dgc.dbc

    @property
    def room(self) -> str:
        return self.gameState.room

