from game import n_max
from chess_game import ChessGameState, ChessGame
from player import simple_players_from_integer
from piece import PatternMovePiece, SimpleCapturePiece, Location
from piece_game import PieceGameState, PieceGame
from time import time


class PolarChessGameState(ChessGameState, PieceGameState):
    def __init__(self,
                 ring_sizes=(1, 4, 12, 24, 24),
                 players=simple_players_from_integer(2),
                 player_to_move=None, pieces=None, kings=None, history=None):
        super().__init__(players=players, player_to_move=player_to_move, pieces=pieces, kings=kings, history=history)
        self.ring_sizes = ring_sizes


class PolarChessGame(ChessGame, PieceGame):
    def neural_net_input(self, game_state):
        neural_net_input = []
        for pl in game_state.players:
            if pl == game_state.player_to_move:
                neural_net_input.append(1)
            else:
                neural_net_input.append(0)
        for pl in game_state.players():
            for r, ring_size in enumerate(game_state.ring_sizes):
                for t in range(ring_size):
                    if PolarChessTile(game_state.ring_sizes, r, t) in map(lambda x: x.location, game_state.pieces(pl)):
                        neural_net_input.append(1)
                    else:
                        neural_net_input.append(0)
        return neural_net_input

    def default_game_state(self):
        return PolarChessGameState()

    def randomize_position(self, game_state):
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

    def accessible_locations(self, game_state):
        accessible_locations = []

        if self.location:
            for location in self.location.axial_neighbors(1)\
                          + self.location.axial_neighbors(-1)\
                          + self.location.radial_neighbors(1)\
                          + self.location.radial_neighbors(-1):
                if location not in map(lambda x: x.location, game_state.pieces(self.player)):
                    accessible_locations.append(location)

        return accessible_locations

    def attackers_of_same_type(self, game_state, piece):
        attackers = []
        for new_piece in game_state.pieces():
            for location in self.accessible_locations(game_state=game_state):
                if new_piece.location == location:
                    if new_piece.player != piece.player:
                        if type(new_piece) == type(self):
                            attackers.append(new_piece)
        return attackers


if __name__ == '__main__':

    test_game = PolarChessGame()

    test_game_state = test_game.default_game_state()

    points = [(0, 0), (3, 12)]
    test_pieces = []ch
    player = test_game_state.player_to_move
    for point in points:
        player = player.turn()
        test_tile = PolarChessTile(test_game_state.ring_sizes, point[0], point[1])
        test_pieces.append(Lion(player=player, location=test_tile))

    test_game_state.add_pieces(*test_pieces)
    test_game_state.crown_kings(*test_pieces)

    print(n_max(test_game, test_game_state, 6))

    print(test_game_state)
    print(test_pieces[1].legal_moves(test_game_state))
    print(test_game.player_legal_moves(test_game_state, test_game_state.player_to_move))
    print(test_game_state)