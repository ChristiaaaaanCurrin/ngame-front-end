from abc import ABC, abstractmethod
from new_move import CombinationMove, TokenOwnerChange, RecordMove
from equality_modifiers import EqualityByType, EqualityByArgs
from player import PlayerStatus, play_on


class Piece(ABC):
    def __init__(self, player, successor=None):
        self.player = player
        self.successor = successor

    @abstractmethod
    def legal_moves(self, game_state):
        pass


class Player(Piece, ABC):
    def __init__(self, successor, tag, status=play_on):
        super().__init__(player=self, successor=successor)
        self.status = status
        self.tag = tag

    def __repr__(self):
        return 'p' + str(self.tag)

    @abstractmethod
    def utility(self, game_state):
        pass


class Token(Piece, ABC):
    def __init__(self, owner, successor=None):
        super().__init__(player=owner.player, successor=successor)
        self.owner = owner


class SimpleTurnToken(Token):
    def legal_moves(self, game_state):
        legal = []
        for move in self.owner.legal_moves(game_state):
            legal.append(CombinationMove(move, TokenOwnerChange(self, self.owner.successor)))
        return legal


class TopTurnToken(SimpleTurnToken):
    def __repr__(self):
        return 'turn'

    def legal_moves(self, game_state):
        legal = []
        for move in self.owner.legal_moves(game_state):
            legal.append(RecordMove(move, TokenOwnerChange(self, self.owner.successor)))
        return legal


def instantiate_pieces_from_integer(piece_class, number_of_players):
    players = [piece_class(None, number_of_players)]
    for n in range(number_of_players-1):
        players.append(piece_class(players[n], number_of_players-1-n))
    players[0].successor = players[-1]
    players.reverse()
    return players
