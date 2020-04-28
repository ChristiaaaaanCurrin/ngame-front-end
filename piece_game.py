from abc import ABC, abstractmethod
from game_prep import GameState


class Piece(ABC):
    def __init__(self, game_state, player, location):
        self.player = player
        self.location = location
        self.game_state = game_state

    @abstractmethod
    def legal_moves(self, game_state):
        """
        :param game_state: game that the piece is in
        :return: what actions ("moves") the piece can legally make
        """
        pass


class PatternMovePiece(Piece, ABC):
    def __init__(self, player, location, capture_with_move=True, blocked=True, friendly_fire=False):
        super().__init__(player, location)
        self.capture_with_move = capture_with_move
        self.blocked = blocked
        self.friendly_fire = friendly_fire

    @abstractmethod
    def legal_move_steps(self):
        """
        :return: list of functions giving closest legal moves (one step in the pattern for pattern move)
        """
        pass

    def legal_moves(self):
        legal = []
        for legal_move_step in self.legal_move_steps():
            edge = legal_move_step(self)
            while edge:
                new_edge = []
                for move in edge:
                    if move not in legal:
                        legal.append(move)
                        for piece in move.pieces_to_add:
                            for next_move in legal_move_step(piece):
                                new_edge.append(next_move)
                edge = new_edge
        return legal


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
