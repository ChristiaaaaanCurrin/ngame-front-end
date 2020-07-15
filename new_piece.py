from abc import ABC, abstractmethod
from new_game_state import GameState
from piece import play_on
from random import random


class Piece(ABC):
    def __init__(self, name, game_state=GameState(), player=None, location=None, successor=None):
        self.player = player
        self.location = location
        self.game_state = game_state
        self.game_state.add_piece(self)
        self.successor = successor
        self.name = name

    @abstractmethod
    def legal_moves(self):
        """
        :return: list of legal moves for self in game state
                 moves must contain enough information to be reversed
        """
        pass

    @abstractmethod
    def execute_move(self, move):
        """
        carries out instructions in move
        :param move: same type as an element of self.legal_moves() output
        """
        pass

    @abstractmethod
    def undo_move(self, move):
        """
        carries out inverse operation of self.execute_move(move)
        :param move: same type as an element of self.legal_moves() output
        """
        pass

    @abstractmethod
    def utility(self):
        pass

    def bottom(self):
        return self.location.bottom_piece()


# -- Top Piece --------------------------------------------

class TopPiece(Piece, ABC):
    def __init__(self, name, location, game_state=GameState(), history=None):
        #TODO should player for pieces above players be None? Think about it...
        super().__init__(name=name, player=None, location=location, successor=self, game_state=game_state)

        self.game_state.top_piece = self

        if history:
            self.history = history
        else:
            self.history = []

    def __repr__(self):
        return 'turn: ' + str(self.location)

    def execute_move(self, move):
        self.location = move[0]
        for piece, sub_move in move[2]:
            piece.execute_move(sub_move)
        self.player = self.location.player
        self.history.append(move)

    def undo_move(self, move):
        for piece, sub_move in move[2]:
            piece.undo_move(sub_move)
        self.location = move[1]
        self.player = self.location.player

    def revert(self):
        self.undo_move(self.history.pop(-1))


class SimpleTurn(TopPiece):
    def legal_moves(self):
        legal = []
        for move in self.location.legal_moves():
            legal.append((self.location.successor, self.location, [(self.location, move)]))
        return legal

    def utility(self):
        utility = {}
        for player in self.game_state.players():
            utility.update(player.utility())
        return utility


# -- Bottom Piece -----------------------------------------

class BottomPiece(Piece, ABC):
    def __init__(self, name, player=None, successor=None, game_state=None):
        super().__init__(name=name, player=player, location=None, successor=successor, game_state=game_state)

    def bottom_piece(self):
        return self


# -- Player -----------------------------------------------

class Player(BottomPiece, ABC):
    def __init__(self, name, status, game_state=GameState(), successor=None):
        self.status = status
        super().__init__(name=name, player=self, successor=successor, game_state=game_state)

    def __repr__(self):
        return 'p' + str(self.name)


# -- Subordinate Piece ------------------------------------

class SubordinatePiece(Piece, ABC):
    def __eq__(self, other):
        return other.bottom() == self.bottom()

    @abstractmethod
    def attacks_piece(self, piece):
        """
        :param piece: piece that self might be 'attacking'
        :return: true if self 'attacks' piece
        """
        pass

    def is_attacked(self):
        attacked = False
        for piece in self.game_state.sub_pieces():
            if piece.attacks_piece(self):
                attacked = True
                break
        return attacked


# Piece Factory Method

def instantiate_pieces_from_integer(piece_class, number_of_pieces, game_state=GameState()):
    pieces = [piece_class(name=number_of_pieces, game_state=game_state)]
    for n in range(number_of_pieces - 1):
        pieces.append(piece_class(successor=pieces[n], name=number_of_pieces - 1 - n, game_state=game_state))
    pieces[0].successor = pieces[-1]
    pieces.reverse()
    return pieces

