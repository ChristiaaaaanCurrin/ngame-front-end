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
        pass

    def execute_move(self, move, reverse_move, sub_moves=None):
        self.location = move
        for piece, move in sub_moves:
            piece.execute_move(move)

    def reverse_move(self, move, reverse_move, sub_moves=None):
        self.location = reverse_move
        if sub_moves:
            for piece, move in sub_moves:
                piece.execute_move(reverse_move)


class Token(Piece, ABC):
    def __init__(self, name, location, successor=None):
        super().__init__(name, location=location, player=location.player, successor=successor)

    def execute_move(self, move, reverse_move, sub_moves=None):
        super().execute_move(move, reverse_move, sub_moves)
        self.player = self.location.player

    def reverse_move(self, move, reverse_move, sub_moves=None):
        super().reverse_move(move, reverse_move, sub_moves)
        self.player = self.location.player


class Player(Piece, ABC):
    def __init__(self, name, location=play_on, successor=None):
        super().__init__(name=name, player=self, location=location, successor=successor)

    def __repr__(self):
        return 'p' + self.name

    @abstractmethod
    def utility(self, game_state):
        pass


class SubordinatePiece(Piece, ABC):
    @abstractmethod
    def attacks_piece(self, game_state, piece):
        pass

    def is_attacked(self, game_state):
        attacked = False
        for piece in game_state.pieces():
            if piece.attacks_piece(game_state, self):
                attacked = True
                break
        return attacked
