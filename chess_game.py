from abc import ABC, abstractmethod
from piece_game import PieceGameState, Piece


class ChessGameState(PieceGameState, ABC):
    def __init__(self, players, player_to_move, history):
        super().__init__(players, player_to_move, history)

        self.kings = []

        self.piece_types = []

    def set_board(self, pieces):
        for piece in pieces:
            self.all_pieces.append(piece)
            if piece not in self.piece_types:
                self.piece_types.append(piece)

    def crown_kings(self, kings):
        for king in kings:
            self.kings.append(king)

    def in_check(self, player):
        in_check = False
        if self.kings:
            for king in self.kings:
                if king.player == player and king.attackers:
                    in_check = True
        return in_check

    def legal_moves(self):
        legal = []
        for piece in self.pieces():
            for move in piece.legal_moves():
                if not self.in_check(piece.player):
                    legal.append(move)
        return legal


class ChessPiece(Piece, ABC):
    def __init__(self, game_state, player, location):
        super().__init__(game_state, player, location)

    @abstractmethod
    def attackers_of_same_type(self, piece):
        """
        this method must give the pieces (of same type as self)in game_state where location is in piece.legal_moves
        :param piece: the piece that is attacked by pieces
        :return: list of pieces in game_state where type(piece) == type(self) and piece attacks location
        """
        pass

    def attacked(self):
        attacked = False
        for piece_type in self.game_state.piece_types:
            if piece_type.attackers_of_same_type(self):
                attacked = True
                break
        return attacked
