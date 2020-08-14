from enum import Enum
from rule import SimpleTurn, Rule, piece
from game_state import GameState
from coordinate_rule import Tile, PatternRule


class Key(Enum):
    DEFAULT = 0
    PLAYER = 1
    PAWN = 2
    WALL = 3


class QuoridorPlayer(Rule):
    def __init__(self, side=0, walls=0, **kwargs):
        super().__init__(**kwargs)
        self.side = side % 4
        self.walls = walls

    def generate_legal_moves(self):
        legal = []
        if self.walls:
            wall = self.game_state.filter_top_rules(Key.WALL)[0]
            for sub_move in wall.get_legal_moves():
                legal.append((wall, sub_move))
        for pawn in self.game_state.filter_top_rules(Key.PAWN, self.player):
            for sub_move in pawn.get_legal_moves():
                legal.append((pawn, sub_move))
        return legal

    def execute_move(self, move):
        sub_piece, sub_move = move
        if sub_piece in self.game_state.filter_top_rules(Key.WALL):
            self.walls -= 1
        sub_piece.execute_move(sub_move)
        self.changed()

    def undo_move(self, move):
        sub_piece, sub_move = move
        if sub_piece in self.game_state.filter_top_rules(Key.WALL):
            self.walls += 1
        sub_piece.undo_move(sub_move)
        self.changed()


class Pawn(PatternRule):
    def get_step(self, coords):
        legal = []
        x, y = self.get_coords()
        for n in (-1, 1):
            if 0 <= x + n < self.game_state.columns:
                legal.append((x + n, y))
            if 0 <= y + n < self.game_state.rows:
                legal.append((x, y + n))
        return legal

    def does_skip(self, coords):
        for pawn in self.game_state.filter_top_rules(Key.PAWN):
            if pawn.get_coords() == coords:
                return True
        else:
            return False

    def does_stop_on(self, coords):
        return not self.does_skip(coords)


class Wall(Tile):
    def __init__(self, *coords, **kwargs):
        super().__init__(*coords, **kwargs)
        self.placed = False

    def generate_legal_moves(self):
        legal = []
        if not self.placed:
            for row in range(self.game_state.rows - 1):
                for column in range(self.game_state.columns - 1):
                    for orientation in (0, 1):
                        coords = row, column, orientation
                        for wall in self.game_state.filter_top_rules(Key.WALL):
                            if wall.coords[:1] == coords[:1]\
                              or wall.coords == ((row - (orientation ^ 1)), column - orientation, orientation):
                                break
                        else:
                            legal.append((row, column, orientation))
        return legal

    def execute_move(self, move):
        self.coords = move
        self.placed = True
        self.changed()

    def undo_move(self, move):
        self.coords = ()
        self.placed = False
        self.changed()


class PathFinder(Pawn):
    def does_stop_on(self, coords):
        return False

    def does_skip(self, coords):
        return False


def quoridor(players=4, total_walls=20, rows=9, columns=9):
    state = GameState(rows=rows, columns=columns)
    players = [QuoridorPlayer(side=side, player='p' + str(side + 1), name='p' + str(side + 1),
                              walls=total_walls//players, keys=[Key.PLAYER]) for side in range(players)]
    pawns = []
    for player in players:
        position = ((0, columns//2), (rows-1, columns//2), (0, rows//2), (columns-1, rows//2))[player.side]
        pawns.append(piece(Pawn(), Tile(*position), keys=(Key.PAWN, player.player), player=player.player))
    game = SimpleTurn(*players, keys=[Key.DEFAULT])

    walls = [Wall(keys=[Key.WALL]) for n in range(total_walls)]

    state.add_rules(game, *players, *pawns, *walls)
    return game


if __name__ == "__main__":
    test_game = quoridor()
    print(test_game.game_state)
    test_game.execute_move(test_game.get_legal_moves()[0])
    [print(test_game.move_to_string(move)) for move in test_game.get_legal_moves()]


"""
 09 08 07 06 05 04 03 02 01 00
 __|__|__|__|p1|__|__|__|__ 01
 __|__|__|__|__|__|__|__|__ 02
 __|__|__|__|__|__|__|__|__ 03
 __|__|__|__|__|__|__|__|__ 04
 p4|__|__|__|__|__|__|__|p3 05
 __|__|__|__|__|__|__|__|__ 06
 __|__|__|__|__|__|__|__|__ 07
 __|__|__|__|__|__|__|__|__ 08
   |  |  |  |p2|  |  |  |   09
"""