from enum import Enum
from rule import SimpleTurn, Rule, piece
from game_state import GameState
from coordinate_rule import Tile, PatternRule


class Key:
    DEFAULT = 0
    PLAYER = 1
    PAWN = 2
    WALL = 3


class QuoridorPlayer(Rule):
    def __init__(self, side=0, walls=0, goal=(), **kwargs):
        super().__init__(**kwargs)
        self.side = side % 4
        self.goal = goal
        self.walls = walls

    def generate_legal_moves(self):
        legal = []
        if self.walls:
            wall = Wall(game_state=self.game_state, keys=[Key.WALL])
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
    def __init__(self, **kwargs):
        self.path_finder = False
        super().__init__(**kwargs)

    def get_step(self, coords):
        legal = []
        r, c = coords
        for n in (-1, 1):
            if 0 <= r + n < self.game_state.columns:
                for wall in self.game_state.filter_top_rules(Key.WALL):
                    if (r + (n - 1)//2, c, 1) == wall.get_coords() or (r + (n - 1)//2, c - 1, 1) == wall.get_coords():
                        break
                else:
                    legal.append((r + n, c))
            if 0 <= c + n < self.game_state.rows:
                for wall in self.game_state.filter_top_rules(Key.WALL):
                    if (r, c + (n - 1)//2, 0) == wall.get_coords() or (r - 1, c + (n - 1)//2, 0) == wall.get_coords():
                        break
                else:
                    legal.append((r, c + n))
        return legal

    def does_skip(self, coords):
        for pawn in self.game_state.filter_top_rules(Key.PAWN):
            if pawn.get_coords() == coords:
                return True and not self.path_finder
        else:
            return False

    def does_stop_on(self, coords):
        return not self.path_finder and not self.does_skip(coords)


class Wall(Tile):
    def __init__(self, *coords, **kwargs):
        super().__init__(*coords, **kwargs)

    def __repr__(self):
        return "Wall%s" % str(self.coords)

    def generate_legal_moves(self):
        legal = []
        for row in range(self.game_state.rows - 1):
            for column in range(self.game_state.columns - 1):
                for orientation in (0, 1):
                    coords = row, column, orientation
                    for wall in self.game_state.filter_top_rules(Key.WALL):
                        if wall.coords[:-1] == coords[:-1]\
                          or wall.coords == ((row - (orientation ^ 1)), column - orientation, orientation):
                            break
                    else:
                        legal.append((row, column, orientation))
        return legal

    def execute_move(self, move):
        self.coords = move
        self.game_state.add_rules(self)
        self.changed()

    def undo_move(self, move):
        self.coords = ()
        self.game_state.add_rules(self)
        self.changed()


def quoridor(num_players=2, total_walls=20, rows=9, columns=9):
    players = []
    pawns = []
    for side in range(num_players):
        goal = ([((rows - 1, c),    (0, c))[side & 1] for c in range(columns)],
                [((r, columns - 1), (r, 0))[side & 1] for r in range(rows)])[side >> 1]

        player = QuoridorPlayer(side=side, player='p' + str(side + 1), name='p' + str(side + 1),
                                walls=total_walls//num_players, keys=[Key.PLAYER], goal=goal)
        players.append(player)
        position = ((0, columns//2), (rows-1, columns//2), (0, rows//2), (columns-1, rows//2))[player.side]
        pawns.append(piece(Pawn(), Tile(*position), keys=(Key.PAWN, player.player), player=player.player))

    game = SimpleTurn(*players, keys=[Key.DEFAULT])
    state = GameState(rows=rows, columns=columns, top_rules={Key.PLAYER: [], Key.PAWN: [], Key.WALL: []})
    state.add_rules(game, *players, *pawns)
    return game


if __name__ == "__main__":
    test_game = quoridor()
    pl1 = test_game.game_state.filter_top_rules(Key.PLAYER)[0]
    p1 = test_game.game_state.filter_top_rules(Key.PAWN)[0]
    p2 = test_game.game_state.filter_top_rules(Key.PAWN)[1]
    print(p1)


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