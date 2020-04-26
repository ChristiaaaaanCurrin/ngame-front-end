from abc import ABC, abstractmethod
from game_prep import GameState


class Piece(ABC):
    def __init__(self, player, location):
        self.player = player
        self.location = location

    @abstractmethod
    def legal_moves(self, game_state):
        pass


class PieceMove:
    def __init__(self, added_pieces, removed_pieces):
        self.added_pieces = added_pieces
        self.removed_pieces = removed_pieces


class PieceGameState(GameState, ABC):
    def __init__(self, players, player_to_move, pieces, history=None):
        super().__init__(players, player_to_move)
        self.pieces = pieces
        if history:
            self.history = history
        else:
            self.history = []

    def legal_moves(self):
        legal = []
        for piece in self.pieces:
            for move in piece.legal_moves(self):
                legal.append(move)
        return legal

    def make_move(self, move):
        for piece in move.added_pieces:
            self.pieces.append(piece)
        self.pieces = filter((lambda x: x not in move.removed_pieces), self.pieces)
        self.history.append(self.player_to_move, move)
        self.player_to_move = self.player_to_move.turn()

    def revert(self):
        (previous_player, move) = self.history.pop(-1)
        for piece in move.removed_pieces:
            self.pieces.append(piece)
        self.pieces = filter((lambda x: x not in move.added_pieces), self.pieces)
        self.player_to_move = previous_player
