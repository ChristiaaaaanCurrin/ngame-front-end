from game_prep import simple_players_from_integer
from chess_game import ChessGameState
from piece_game import PieceGameState, PatternMovePiece, SimpleCapturePiece, Location


class PolarChessGameState(ChessGameState, PieceGameState):
    def __init__(self,
                 ring_sizes=(1, 4, 12, 24, 24),
                 players=simple_players_from_integer(1),
                 player_to_move=None,
                 history=None):
        if not player_to_move:
            player_to_move = players[0]
        super().__init__(players=players, player_to_move=player_to_move, history=history)
        self.ring_sizes = ring_sizes

    def neural_net_input(self):
        neural_net_input = []
        for player in self.players:
            if player == self.player_to_move:
                neural_net_input.append(1)
            else:
                neural_net_input.append(0)
        for player in self.players:
            for r, ring_size in enumerate(self.ring_sizes):
                for t in range(ring_size):
                    if PolarChessTile(self.ring_sizes, r, t) in map(lambda x: x.location, self.pieces(player)):
                        neural_net_input.append(1)
                    else:
                        neural_net_input.append(0)
        return neural_net_input

    def randomize_position(self):
        pass


class PolarChessTile(Location):
    def __init__(self, ring_sizes, r_coord, t_coord):
        super().__init__(ring_sizes, r_coord, t_coord)
        self.ring_sizes = ring_sizes
        self.r_coord = r_coord
        self.t_coord = t_coord

    def __eq__(self, other):
        return self.r_coord == other.r_coord\
            and self.t_coord == other.t_coord\
            and self.ring_sizes[self.r_coord] == other.ring_sizes[self.r_coord]

    def __repr__(self):
        return '(r = ' + str(self.r_coord)\
             + ', t = ' + str(self.t_coord)\
             + '/' + str(self.ring_sizes[self.r_coord]) + ')'

    def axial_neighbors(self, t_shift):
        sizes = self.ring_sizes
        return [PolarChessTile(sizes, self.r_coord, (self.t_coord + t_shift) % sizes[self.r_coord])]

    def radial_neighbors(self, r_shift):
        r = self.r_coord
        t = self.t_coord
        size = self.ring_sizes[r]
        if 0 <= (r + r_shift) < len(self.ring_sizes):
            new_size = self.ring_sizes[r + r_shift]
            return [PolarChessTile(self.ring_sizes, r + r_shift, new_t
                                   ) for new_t in range(t * new_size // size % new_size,
                                                        new_size - (size - t - 1) * new_size // size)]
        else:
            return []


class Lion(SimpleCapturePiece):
    def __repr__(self):
        return 'Lion ' + str(self.player) + ' ' + str(self.location)

    def accessible_locations(self):
        accessible_locations = []

        if self.location:
            for location in self.location.axial_neighbors(1)\
                          + self.location.axial_neighbors(-1)\
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

    test_game = PolarChessGameState()

    test_tile = PolarChessTile(test_game.ring_sizes, 1, 0)
    test_tile2 = PolarChessTile(test_game.ring_sizes, 3, 1)
    test_game.set_board([Lion(test_game, test_game.player_to_move, test_tile),
                         Lion(test_game, test_game.player_to_move.turn(), test_tile2)])
    #test_game.crown_kings(test_game.pieces())
    print(test_game.legal_moves())
    print(test_game.utility())
    for move in test_game.legal_moves():
        test_game.make_move(move)
        print(test_game.utility())
        test_game.revert()
    print(test_game.n_max(5))
