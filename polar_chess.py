from game_prep import GameState, Piece, simple_players_from_integer

class PolarChessPiece:
    def __init__(self, player, location):
        self.player = player
        self.location = location

    def legal_moves(self, board, pieces):


class PolarChess(GameState):
    def __init__(self, players=simple_players_from_integer(2), player_to_move=None):
        if not player_to_move:
            player_to_move = players[0]
        super.__init__(players, player_to_move)

    def make_move(self, move):
        piece_to_move = move[0]
