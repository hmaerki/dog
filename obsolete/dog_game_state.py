from __future__ import annotations
import typing
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # https://www.stefaanlippens.net/circular-imports-type-hints-python.html
    import dog_game

import dog_constants
import dog_game_statemachine

import dog_cards


class JsonWrapper:
    def __init__(self, gameState: GameState, json:dict):
        self.__gameState = gameState
        self.__json = json

    def isEvent(self, eventName: str):
        return self.__json.get('event', None) == eventName

    def getStr(self, tag, mandatory=True):
        text = self.__json.get(tag, None)
        if text is None:
            if mandatory:
                raise Exception(f'"{tag}" mssing in: {self.__json}')
        return text

    def getInt(self, tag, mandatory=True):
        text = self.getStr(tag=tag, mandatory=mandatory)
        try:
            return int(text)
        except ValueError:
            raise Exception(f'Expected a integer but got "{tag}" in: {self.__json}')

    def addMessagePlayer(self, msg:str, msgI18L:str) -> None:
        playerIndex = self.getInt('player')
        self.__gameState.addMessagePlayer(playerIndex, msg, msgI18L)

    def addMessage(self, msg:str, msgI18L:str) -> None:
        self.__gameState.addMessage(msg, msgI18L)

    def __repr__(self):
        return repr(self.__json)

class PlayerState:
    def __init__(self, game_state:GameState, player: dog_game.Player):
        self.__game_state = game_state
        self.__player = player
        self.__name = player.initialName
        self.__cards = ()
        self.__cardToBeChangedIndex = None

    def __repr__(self) -> str:
        return f'{type(self).__name__} {self.__player.colorID}({self.__name})'

    @property
    def game(self) -> dog_game.Game:
        return self.__player.game

    @property
    def colorI18N(self) -> str:
        return self.__player.colorI18N

    @property
    def name(self) -> str:
        return self.__name

    @property
    def player(self) -> dog_game.Player:
        return self.__player

    @property
    def cardsText(self) -> str:
        def name(card):
            if card is None:
                return '-'
            return card.id
        cards_text = [name(card) for card in self.__cards]
        return f'{self.__player.colorID} changeIndex={self.__cardToBeChangedIndex} cards={",".join(cards_text)}'

    @property
    def requireToChange(self) -> bool:
        return self.__cardToBeChangedIndex is None

    def setName(self, name:str):
        self.__name = name

    def serveCards(self, cards: list) -> None:
        self.__cards = cards

    def cardToBeChanged(self, card_index:int) -> typing.Optional[str]:
        err = f'{self}: Expected __cardToBeChangedIndex to be "None" but got "{self.__cardToBeChangedIndex}"'
        if self.__cardToBeChangedIndex is not None:
            logging.warning(err)
            return err
        self.__cardToBeChangedIndex = card_index
    
    def changeCard(self, playerStateOther: PlayerState):
        cardSelf = self.__cards[self.__cardToBeChangedIndex]
        cardOther = playerStateOther.__cards[playerStateOther.__cardToBeChangedIndex]

        self.__cards[self.__cardToBeChangedIndex] = cardOther
        playerStateOther.__cards[playerStateOther.__cardToBeChangedIndex] = cardSelf

    def playCard(self, json: JsonWrapper, card_index: int, f_addMessage:typing.Callable):
        card = self.__getCardAtIndex(card_index)
        if card is None:
            json.addMessagePlayer(msg=': This card is not available', msgI18L=': Diese Karte kannst Du nicht spielen.')
            return 'Card already played'
        f_addMessage(msg=f'plays {card.id}', msgI18L=f'spielt {card.nameI18N}')
        self.__game_state.throwCardInCenter(card)
        self.__cards[card_index] = None
        self.__game_state.cardPlayedSuccessfully(json, lastCard=self.__lastCard())

    def __lastCard(self):
        for card in self.__cards:
            if card is not None:
                return False
        return True

    def __getCardAtIndex(self, card_index:int):
        '''Returns card or "None"'''
        if card_index >= len(self.__cards):
            return None
        return self.__cards[card_index]

    def __enableCardAtIndex(self, card_index:int, enabled:bool):
        '''Returns "False" if no card, else "enabled"'''
        card = self.__getCardAtIndex(card_index)
        if card is None:
            return False
        return enabled

    def appendState(self, json: list, statemachineState: dog_game_statemachine.GameStatemachineBase):
        # changeCard-buttons: Enable or disable all
        enabled = statemachineState.buttonChangeEnabled(self)
        json.append({
            'html_id': f'button#player{self.__player.index}_changeCard',
            'attr_set': { 'disabled': not enabled }
        })

        # Update the play cards buttons
        for card_index in range(dog_constants.COUNT_PLAYER_CARDS_OBSOLETE):
            enabled = self.__enableCardAtIndex(card_index, statemachineState.buttonPlayEnabled(self))
            json.append({
                'html_id': f'button#player{self.__player.index}_playCard[name="{card_index}"]',
                'attr_set': { 'disabled': not enabled }
            })

        # Update the cards
        for card_index in range(dog_constants.COUNT_PLAYER_CARDS_OBSOLETE):
            card = self.__getCardAtIndex(card_index)
            card_name = '-' if card is None else card.nameI18N
            json.append({
                'html_id': f'p#player{self.__player.index}_card[name="{card_index}"]',
                'html': card_name
            })

        json.append({
            'html_id': f'#player{self.__player.index}_textfield_name',
            'attr_set': { 'value': self.name }
        })


class GameState:
    def __init__(self, game: dog_game.Game):
        self.__game = game
        self.__statemachine = dog_game_statemachine.GameStateInit(self)
        self.__list_player_state = [PlayerState(self, player) for player in self.__game.players]
        self.__cardStack = dog_cards.Cards()
        self.__cardInCenter = None
        self.__messagesI18L = []
        self.__last_message = '-'
        self.__dictMarbles = {}

    def shuffleCards(self, json: JsonWrapper):
        # It is not possible to play one game (6,5,4,3,2) with one card set. 120 cards are available but 120 required.
        #   Total cards: 13*4*2 + 3*2 = 110
        #   Cards used in one round: 6 Players, cards 6, 5, 4, 3, 2
        #   6 * (6+5+4+3+2) = 120
        MAX_PLAYERS = 6
        MAX_CARDS_PER_PLAYER = 6
        if self.__cardStack.count > MAX_PLAYERS*MAX_CARDS_PER_PLAYER:
            # Shuffling still not required
            return
        self.__cardStack.shuffle(dog_constants.dogRandom.shuffle)
        json.addMessage(msg='shuffle card', msgI18L='Die Karten wurden gemischt')

    @property
    def game(self) -> dog_game.Game:
        return self.__game

    @property
    def playersRequireToChange(self):
        return [player for player in self.__list_player_state if player.requireToChange]

    @property
    def lastMessage(self):
        return self.__last_message

    def addMessagePlayer(self, playerIndex: int, msg:str, msgI18L:str) -> None:
        player = self.__list_player_state[playerIndex].name
        _msg = f'{player} {msg}'
        _msgI18L = f'{player} {msgI18L}'
        self.addMessage(_msg, _msgI18L)

    def addMessage(self, msg:str, msgI18L:str) -> None:
        self.__last_message = msg
        self.__messagesI18L.insert(0, msgI18L)
        while len(self.__messagesI18L) > 5:
            self.__messagesI18L.pop(-1)

    def getPlayer(self, index: int) -> 'PlayerState':
        return self.__list_player_state[index]

    def serveCards(self, count_cards: int) -> None:
        for playerState in self.__list_player_state:
            playerState.serveCards(self.__cardStack.pop_cards(count_cards))

    def event(self, json: str) -> typing.Optional[str]:
        try:
            return self.__statemachine.event(JsonWrapper(self, json))
        except dog_game_statemachine.NewGameStateException as ex:
            self.__statemachine = ex.state
            return f'New State "{type(self.__statemachine).__name__}"'

    def appendState(self, json: dict) -> None:
        for playerState in self.__list_player_state:
            playerState.appendState(json, self.__statemachine)

        json.append({
            'html_id': '#assistance',
            'html': self.game.getAssistance()
        })

        json.append({
            'html_id': '#messages',
            'html': ' / '.join(self.__messagesI18L)
        })

        cardInCentre = ''
        if self.__cardInCenter is not None:
            cardInCentre = self.__cardInCenter.nameI18N
        json.append({
            'html_id': '#card_in_center',
            'html': cardInCentre
        })

        for dictPosition in self.__dictMarbles.values():
            json.append(dictPosition)

    def getAssistance(self):
        return self.__statemachine.getAssistance()

    def setName(self, player:int, name:str):
        return self.__list_player_state[player].setName(name)

    def setMarble(self, dictPosition: dict) -> None:
        # ['circle1_0', 0, 0, 0]
        svg_id = dictPosition['svg_id']
        self.__dictMarbles[svg_id] = dictPosition

    def cardToBeChanged(self, player:int, index:int):
        return self.__list_player_state[player].cardToBeChanged(index)

    def playCard(self, json: JsonWrapper, player:int, index:int, f_addMessage:typing.Callable):
        return self.__list_player_state[player].playCard(json, index, f_addMessage)

    def changeCards(self):
        if len(self.playersRequireToChange) > 0:
            return False
        player_count_half = self.__game.player_count//2
        for index_A in range(player_count_half):
            index_B = index_A + player_count_half
            self.__list_player_state[index_A].changeCard(self.__list_player_state[index_B])
        return True

    def cardPlayedSuccessfully(self, json: JsonWrapper, lastCard: bool) -> None:
        self.__statemachine.cardPlayedSuccessfully(json, lastCard)

    # def throwCardInCenter(self, card:dog_cards.Card) -> None:
    def throwCardInCenter(self, card):
        self.__cardInCenter = card