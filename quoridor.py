from rule import ZeroSum, SimpleTurn, Rule, piece
from game_state import GameState
from coordinate_rule import CoordinateRule, Tile, PatternRule


class QuoridorGame(ZeroSum):
    def does_win(self, player):
        for pawn in self.game_state.filter_top_rules("pawns", self.get_player()):
            orientation = self.get_bottom_rule().side >> 1
            position = pawn.get_bottom_rule().coords[orientation]
            target = (self.game_state.rows - 1, 0, self.game_state.columns - 1, 0)[self.get_bottom_rule().side]
            if position == target:
                return True
        else:
            return False

    def does_lose(self, player):
        return False

    def does_draw(self, player):
        return False


class QuoridorPlayer(Rule):
    def __init__(self, side=0, walls=0, **kwargs):
        super().__init__(**kwargs)
        self.side = side % 4
        self.walls = [Wall(game_state=self.game_state, path=['walls']) for n in range(walls)]
        self.used = []

    def get_legal_moves(self):
        legal = []
        if self.walls:
            wall = self.walls[-1]
            for sub_move in wall.get_legal_moves():
                legal.append((wall, sub_move))
        for pawn in self.game_state.get_top_rules('pawns', self.player):
            for sub_move in pawn.get_legal_moves():
                legal.append((pawn, sub_move))
        return legal

    def execute_move(self, move):
        sub_piece, sub_move = move
        if sub_piece in self.walls:
            self.walls.remove(sub_piece)
            self.used.append(sub_piece)
        sub_piece.execute_move(sub_move)

    def undo_move(self, move):
        sub_piece, sub_move = move
        if sub_piece in self.used:
            self.used.remove(sub_piece)
            self.walls.append(sub_piece)
        sub_piece.undo_move(sub_move)

    def get_utility(self):
        return {self.player: 0.3}


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
        for pawn in self.game_state.get_top_rules("pawns"):
            if pawn.get_coords() == coords:
                return True
        else:
            return False

    def does_stop_on(self, coords):
        return not self.does_skip(coords)


class Wall(Tile):
    def get_legal_moves(self):
        legal = []
        for row in range(self.game_state.rows - 1):
            for column in range(self.game_state.columns - 1):
                for orientation in (0, 1):
                    coords = row, column, orientation
                    for wall in self.game_state.get_top_rules("walls"):
                        if wall.coords[:1] == coords[:1]\
                          or wall.coords == ((row - (orientation ^ 1)), column - orientation, orientation):
                            break
                    else:
                        legal.append((row, column, orientation))
        return legal

    def execute_move(self, move):
        self.game_state.add_rules(self)
        self.coords = move

    def undo_move(self, move):
        self.game_state.remove_rules(self)


class PathFinder(Pawn):
    def does_stop_on(self, coords):
        return False

    def does_skip(self, coords):
        return False


def quoridor(players=2, walls=20, rows=9, columns=9):
    game_state = GameState(rows=rows, columns=columns)

    ps = [QuoridorPlayer(side=side,
                         player='p' + str(side + 1),
                         name='p' + str(side + 1),
                         walls=walls//players,
                         game_state=game_state) for side in range(players)]

    for p in ps:
        position = ((0, columns//2), (rows-1, columns//2), (0, rows//2), (columns-1, rows//2))[p.side]
        piece(Pawn(), Tile(*position), game_state=game_state, keys=("pawns", p.player), player=p.player)

    game = piece(QuoridorGame(*[p.player for p in ps]), SimpleTurn(*ps), game_state=game_state)
    return game


if __name__ == "__main__":
    test_game = quoridor()
    print(test_game.max_n(5, 5, 1, 0))


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