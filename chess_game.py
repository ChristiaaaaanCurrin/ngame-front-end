from abc import ABC, abstractmethod
from piece_game import PieceGameState, Piece


class ChessPiece(Piece, ABC):
    def __init__(self, game_state, player, location):
        super().__init__(game_state, player, location)

    @abstractmethod
    def attackers_of_same_type(self, location):
        """
        this method must give the pieces (of same type as self)in game_state where location is in self.legal_moves
        :param location: the location that is attacked by pieces
        :return: list of pieces in game_state where type(piece) == type(self) and piece attacks location
        """
        pass

    def attacked(self):
        attacked = False
        for piece_type in self.game_state.piece_types:
            if piece_type.attackers_of_same_type(self.location):
                attacked = True
                break
        return attacked


class ChessGameState(PieceGameState, ABC):
    def __init__(self, players, player_to_move, pieces, kings, history=None):
        super().__init__(players, player_to_move, pieces, history)

        self.kings = kings

        self.piece_types = []
        for piece in self.pieces:
            if type(piece) not in self.piece_types:
                self.piece_types.append(piece)

    def in_check(self, player):
        in_check = False
        if self.kings:
            for king in self.kings:
                if king.player == player and king.attackers:
                    in_check = True
        return in_check

    def legal_moves(self):
        legal = []
        for piece in self.pieces:
            for move in piece.legal_moves(self):
                if self.in_check(piece.player):
                    legal.append(move)
        return legal
