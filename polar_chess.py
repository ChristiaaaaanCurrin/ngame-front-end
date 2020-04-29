from game_prep import simple_players_from_integer
from chess_game import ChessPiece, ChessGameState
from piece_game import PieceGameState, PatternMovePiece, SimpleCapturePiece


class PolarChessGameState(ChessGameState, PieceGameState):
    def __init__(self,
                 ring_sizes=(1, 4, 12, 24, 24),
                 players=simple_players_from_integer(2),
                 player_to_move=None,
                 history=None):
        if not player_to_move:
            player_to_move = players[0]
        super().__init__(players=players, player_to_move=player_to_move, history=history)
        self.ring_sizes = ring_sizes

    def utility(self):
        pass

    def neural_net_input(self):
        pass

    def randomize_position(self):
        pass


class PolarChessTile:
    def __init__(self, ring_sizes, r_coord, t_coord):
        self.ring_sizes = ring_sizes
        self.r_coord = r_coord
        self.t_coord = t_coord

    def __repr__(self):
        return '(r = ' + str(self.r_coord)\
             + ', t = ' + str(self.t_coord)\
             + '/' + str(self.ring_sizes[self.r_coord]) + ')'

    def axial_neighbors(self):
        sizes = self.ring_sizes
        return [PolarChessTile(sizes, self.r_coord, (self.t_coord + m) % sizes[self.r_coord]) for m in (-1, 1)]

    def radial_neighbors(self, r_shift):
        r = self.r_coord
        t = self.t_coord
        size = self.ring_sizes[r]
        new_size = self.ring_sizes[r + r_shift]
        if 0 <= (r + r_shift) <= len(self.ring_sizes):
            return [PolarChessTile(self.ring_sizes, r + r_shift, new_t
                                   ) for new_t in range(t * new_size // size % new_size,
                                                        new_size - (size - t - 1) * new_size // size)]
        else:
            return []


class Lion(SimpleCapturePiece, ChessPiece):
    def __repr__(self):
        return 'Lion ' + str(self.player) + ' '  + str(self.location)

    def accessible_locations(self):
        accessible_locations = []

        for location in self.location.axial_neighbors()\
                      + self.location.radial_neighbors(1)\
                      + self.location.radial_neighbors(-1):
            if location not in map(lambda x: x.location, self.game_state.pieces(self.player)):
                accessible_locations.append(location)

        return accessible_locations

    def attackers_of_same_type(self, piece):
        attackers = []
        for new_piece in self.game_state.pieces():
            for location in Lion.accessible_locations(piece):
                if new_piece.location == location:
                    if new_piece.player != piece.player:
                        if type(new_piece) == type(self):
                            attackers.append(new_piece)
        return attackers


if __name__ == '__main__':

    test_tile = PolarChessTile([1, 4, 12, 24, 24], 1, 0)
    test_tile2 = PolarChessTile([1, 4, 12, 24, 24], 1, 1)
    test_neighbors = test_tile.radial_neighbors(1)
    print(test_tile)
    print(test_neighbors)
    test_game = PolarChessGameState()
    test_game.set_board([Lion(test_game, test_game.player_to_move, test_tile),
                         Lion(test_game, test_game.player_to_move.turn(), test_tile2)])
    print(test_game)
    print(test_game.legal_moves())
    print(Lion(test_game, test_game.player_to_move, test_tile))
    print(test_game.players)
