
from __future__ import annotations

import typing
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # https://www.stefaanlippens.net/circular-imports-type-hints-python.html
    import dog_game
    import dog_game_state

import dog_constants

class NewGameStateException(BaseException):
    def __init__(self, state):
        self.state = state

class GameStatemachineBase:
    def __init__(self, gameState: dog_game_state.GameState):
        self._gameState = gameState

    @property
    def game(self):
        return self._gameState.game

    def event(self, json: dog_game_state.JsonWrapper) -> typing.Optional[str]:
        raise NotImplementedError()

    def cardPlayedSuccessfully(self, lastCard: bool) -> None:
        None

    def handleGenericEvent(self, json: dog_game_state.JsonWrapper) -> typing.Optional[str]:
        '''
        Events which always are valid.
        return True if event was handled
        '''
        if json.isEvent('newGame'):
            json.addMessagePlayer( msg='starts a new game', msgI18L='beginnt ein neues Spiel')
            raise NewGameStateException(GameStateExchangeCards(self._gameState, json))

        if json.isEvent('setName'):
            playerIndex = json.getInt('player')
            playerName = json.getStr('name')
            json.addMessagePlayer(msg=f'is now {playerName}', msgI18L=f'heisst neu {playerName}')
            self._gameState.setName(playerIndex, playerName)
            return True

        if json.isEvent('rotateBoard'):
            playerIndex = json.getInt('player')
            logging.warning(f'Player {playerIndex} rotated.')
            json.addMessagePlayer(msg=f'turns the board', msgI18L='dreht das Spielbrett')
            return True

        if json.isEvent('browserConnected'):
            playerIndex = json.getInt('player')
            logging.warning(f'****************************************** {playerIndex} verbunden.')
            # json.addMessagePlayer('ist neu verbunden')
            return True

        return False

    def unexpectedEvent(self, json: dict) -> None:
        err = f'{type(self).__name__}: Unexpected event:{repr(json)}'
        logging.warning(err)
        return err

    def getAssistance(self) -> str:
        raise NotImplementedError()

    def buttonPlayEnabled(self, playerState: dog_game_state.PlayerState):
        return False

    def buttonChangeEnabled(self, playerState: dog_game_state.PlayerState):
        return False

class GameStateInit(GameStatemachineBase):
    def event(self, json: dog_game_state.JsonWrapper) -> typing.Optional[str]:
        if self.handleGenericEvent(json):
            return
        return self.unexpectedEvent(json)

    def getAssistance(self):
        return f'Spiel starten!'

class GameStateExchangeCards(GameStatemachineBase):
    def __init__(self, gameState: dog_game_state.GameState, json: dog_game_state.JsonWrapper):
        super().__init__(gameState)
        self._gameState.shuffleCards(json)
        self._gameState.serveCards(self.game.numcards_begin1)

    @property
    def playersRequireToChangeText(self):
        return ', '.join(sorted([player.name for player in self._gameState.playersRequireToChange]))

    def event(self, json: dog_game_state.JsonWrapper) -> typing.Optional[str]:
        # dict(player=0, event='changeCard', card=1))
        if self.handleGenericEvent(json):
            return
        if json.isEvent('changeCard'):
            playerIndex = json.getInt('player')
            cardIndex = json.getInt('card')
            json.addMessagePlayer(msg='changes a card', msgI18L='tauscht')
            err = self._gameState.cardToBeChanged(playerIndex, cardIndex)
            if self._gameState.changeCards():
                raise NewGameStateException(GameStatePlay(self._gameState))
            return err
        return self.unexpectedEvent(json)

    def buttonChangeEnabled(self, playerState: dog_game_state.PlayerState):
        return playerState.requireToChange

    def getAssistance(self):
        return f'{self.playersRequireToChangeText}: Bitte eine Karte tauschen!'

class GameStatePlay(GameStatemachineBase):
    def __init__(self, gameState: dog_game_state.GameState):
        super().__init__(gameState)
        self._count_cards_served = self.game.numcards_begin1
        self._playerToPlayIndex = dog_constants.dogRandom.randint(0, self._gameState.game.player_count-1)

    def event(self, json: dog_game_state.JsonWrapper) -> typing.Optional[str]:
        if self.handleGenericEvent(json):
            return

        if json.isEvent('playCard'):
            playerIndex = json.getInt('player')
            cardIndex = json.getInt('card')
            if playerIndex != self._playerToPlayIndex:
                json.addMessagePlayer(msg='may play know', msgI18L='darf jetzt nicht spielen!')
                return 'Not your turn!'
            return self._gameState.playCard(json, playerIndex, cardIndex, json.addMessagePlayer)

        return self.unexpectedEvent(json)

    def cardPlayedSuccessfully(self, json: dog_game_state.JsonWrapper, lastCard: bool) -> None:
        self._playerToPlayIndex = (self._playerToPlayIndex + 1) % self.game.player_count
        if lastCard and (self._playerToPlayIndex == 0):
            # If there are no more cards, shuffle and distribute
            self._count_cards_served -= 1
            if self._count_cards_served < self.game.numcards_end:
                self._count_cards_served = self.game.numcards_begin2
                json.addMessage(msg=f'Cards have been shuffled', msgI18L=f'Karten wurden gemischelt.')
                self._gameState.shuffleCards(json)
            json.addMessage(msg=f'Distribute {self._count_cards_served} cards', msgI18L=f'Verteile {self._count_cards_served} Karten')
            self._gameState.serveCards(self._count_cards_served)

    def buttonPlayEnabled(self, playerState: dog_game_state.PlayerState):
        return self._playerToPlayIndex == playerState.player.index

    def getAssistance(self):
        return f'{self._gameState.getPlayer(self._playerToPlayIndex).name}: Bitte Karte ausspielen!'

