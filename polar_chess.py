from chess import ChessGameState, ChessPlayer
from equality_modifiers import EqualityByArgs


class PolarChessTile(EqualityByArgs):
    def __init__(self, r, c):
        super().__init__(r, c)
        self.r = r
        self.c = c

    def neighbors(self, board, *directions):
        pass

