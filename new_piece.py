from abc import ABC, abstractmethod
from piece import play_on


class Piece(ABC):
    def __init__(self, name, player=None, location=None, successor=None):
        self.player = player
        self.location = location
        self.successor = successor
        self.name = name

    @abstractmethod
    def legal_moves(self, game_state):
        """
        :param game_state: game state to investigate for legality
        :return: list of legal moves for self in game state
                 moves must have the form (new_location, old_location, [sub_moves])
        """
        pass

    @abstractmethod
    def execute_move(self, move, move_inverse, sub_moves=None):
        for piece, sub_move in sub_moves:
            piece.execute_move(sub_move)
        self.location = move

    @abstractmethod
    def reverse_move(self, move, move_inverse, sub_moves=None):
        self.location = move_inverse
        for piece, sub_move in sub_moves:
            piece.execute_move(sub_move)


# -- Token ------------------------------------------

class Token(Piece, ABC):
    def __init__(self, name, location, successor=None):
        super().__init__(name, location=location, player=location.player, successor=successor)

    def execute_move(self, move, reverse_move, sub_moves=None):
        super().execute_move(move, reverse_move, sub_moves)
        self.player = self.location.player

    def reverse_move(self, move, reverse_move, sub_moves=None):
        super().reverse_move(move, reverse_move, sub_moves)
        self.player = self.location.player

    def legal_moves(self, game_state):
        legal = []
        for move in self.location.legal_moves(game_state):
            legal.append((self.location.successor, self.location, [(self.location, move)]))
        return legal


class TopTurnToken(Token):
    def __init__(self, name, location, history=None):
        super().__init__(name=name, location=location, successor=None)
        if history:
            self.history = history
        else:
            self.history = []

    def __repr__(self):
        return 'turn: ' + str(self.location)

    def legal_moves(self, game_state):
        legal = []
        for move in self.location.legal_moves(game_state):
            legal.append((self.location.successor, self.location, [move]))
        return legal


# -- Player -----------------------------------------

class Player(Piece, ABC):
    def __init__(self, name, location=play_on, successor=None):
        super().__init__(name=name, player=self, location=location, successor=successor)

    def __repr__(self):
        return 'p' + self.name

    @abstractmethod
    def utility(self, game_state):
        pass


# -- Subordinate Piece ------------------------------

class SubordinatePiece(Piece, ABC):
    @abstractmethod
    def attacks_piece(self, game_state, piece):
        """
        :param game_state: game state of self and piece #TODO necessary?
        :param piece: piece that self might be 'attacking'
        :return: true if self 'attacks' piece
        """
        pass

    def is_attacked(self, game_state):
        attacked = False
        for piece in game_state.pieces():
            if piece.attacks_piece(game_state, self):
                attacked = True
                break
        return attacked


