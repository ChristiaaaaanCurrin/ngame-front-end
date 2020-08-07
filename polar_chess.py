from game_state import GameState
from rule import piece, SimpleTurn
from player import Player, play_on
from coordinate_rule import SimpleCapture, Tile, PatternRule
from timeit import default_timer


class PolarChessGameState(GameState):
    def __init__(self, *rings):
        if rings:
            self.rings = rings
        else:
            self.rings = (1, 4, 12, 24, 24)

        super().__init__()

    def __repr__(self):
        return str(self.rings)


class ChessPlayer(Player):
    def __init__(self, name, game_state=GameState(), *kings, status=play_on):
        super().__init__(name=name, status=status, game_state=game_state)
        self.kings = kings
        for king in self.kings:
            king.player = self.player

    def get_legal_moves(self):  # TODO include status changes in legal moves
        legal = []
        for top_rule in self.game_state.get_top_rules(self.player):
            for move in top_rule.get_legal_moves():
                top_rule.execute_move(move)
                if not self.is_in_check():
                    legal.append((top_rule, move))
                top_rule.undo_move(move)
        return legal

    @staticmethod
    def move_to_string(move):
        top_rule, sub_move = move
        return str(top_rule) + top_rule.move_to_string(sub_move)

    def is_in_check(self):
        for king in self.kings:
            if king.is_attacked():
                return True
        return False

    def execute_move(self, move):
        sub_rule, sub_move = move
        sub_rule.execute_move(sub_move)

    def undo_move(self, move):
        sub_rule, sub_move = move
        sub_rule.undo_move(sub_move)

    def get_utility(self):
        return {self.player: self.status.utility_value(len(self.get_legal_moves()))}


class RadialMove(PatternRule):
    def __init__(self, step_size=1, patterns=True, jumps=False, sub_rule=Tile(0, 0), player=None):
        super().__init__(sub_rule=sub_rule, game_state=PolarChessGameState(), player=player)
        self.step_size = step_size
        self.patterns = patterns
        self.jumps = jumps

    def get_step(self, coords):
        r = coords[0]
        t = coords[1]
        step = self.step_size
        rings = self.game_state.rings
        size = rings[r]

        if 0 <= (r + step) < len(rings):
            new_size = rings[r + self.step_size]
            starting_coord = t * new_size // size % new_size
            ending_coord = new_size - (size - t - 1) * new_size // size

            return [(r + step, new_t) for new_t in range(starting_coord, ending_coord)]

        else:
            return []

    def does_skip(self, coords):
        for rule in self.game_state.get_top_rules(self.player):
            if hasattr(rule.get_bottom_rule(), 'coords'):
                if rule.get_bottom_rule().coords == coords:
                    return True
        else:
            return False

    def does_stop_on(self, coords):
        if not self.patterns:
            return True
        for rule in self.game_state.get_top_rules():
            if hasattr(rule.get_bottom_rule(), 'coords'):
                if rule.get_bottom_rule().coords == coords:
                    return True
        else:
            return False


class AngularMove(PatternRule):
    def __init__(self, step_size=1, patterns=True, jumps=False, sub_rule=Tile(0, 0), player=None):
        super().__init__(sub_rule=sub_rule, game_state=PolarChessGameState(), player=player)
        self.step_size = step_size
        self.patterns = patterns
        self.jumps = jumps

    def get_step(self, coords):
        rings = self.game_state.rings
        r = coords[0]
        t = coords[1]
        new_t = (t + self.step_size) % rings[r]
        return [(r, new_t)]

    def does_skip(self, coords):
        for rule in self.game_state.get_top_rules(self.player):
            if hasattr(rule.get_bottom_rule(), 'coords'):
                if rule.get_bottom_rule().coords == coords:
                    return True
        else:
            return False

    def does_stop_on(self, coords):
        if not self.patterns:
            return True
        for rule in self.game_state.get_top_rules():
            if hasattr(rule.get_bottom_rule(), 'coords'):
                if rule.get_bottom_rule().coords == coords:
                    return True
        else:
            return False


class DiagonalMove(PatternRule):
    def __init__(self, step_size=1, clockwise=True, patterns=True, jumps=False, sub_rule=Tile(0, 0), player=None):
        super().__init__(sub_rule=sub_rule, game_state=PolarChessGameState(), player=player)

        self.step_size = step_size
        self.clockwise = clockwise
        self.patterns = patterns
        self.jumps = jumps

    def get_step(self, coords):
        r = coords[0]
        t = coords[1]
        rings = self.game_state.rings
        size = rings[r]
        step = self.step_size

        if 0 <= (r + step) < len(rings):
            new_size = rings[r + step]
            if self.clockwise:
                new_t = new_size - (size - t - 1) * new_size // size
                if new_t * size == (t + 1) * new_size:
                    return [(r + step, new_t % new_size)]
            else:
                new_t = t * new_size // size - 1
                if (new_t + 1) * size == t * new_size:
                    return [(r + step, new_t % new_size)]

        return []

    def does_skip(self, coords):
        for rule in self.game_state.get_top_rules(self.player):
            if hasattr(rule.get_bottom_rule(), 'coords'):
                if rule.get_bottom_rule().coords == coords:
                    return True
        else:
            return False

    def does_stop_on(self, coords):
        if not self.patterns:
            return True
        if self.jumps:
            return False
        for top_rule in self.game_state.get_top_rules():
            if hasattr(top_rule.get_bottom_rule(), 'coords'):
                if top_rule.get_bottom_rule().coords == coords:
                    return True
        else:
            return False


def lion(game_state, player, *coords):
    return piece(SimpleCapture(game_state, player).named('L'),
                 RadialMove(1, False),
                 RadialMove(-1, False),
                 AngularMove(1, False),
                 AngularMove(-1, False),
                 Tile(*coords))


def leopard(game_state, player, *coords):
    return piece(SimpleCapture(game_state, player).named('P'),
                 RadialMove(),
                 RadialMove(-1),
                 Tile(*coords))


def bear(game_state, player, *coords):
    return piece(SimpleCapture(game_state, player).named('B'),
                 AngularMove(),
                 AngularMove(-1),
                 Tile(*coords))


def tiger(game_state, player, *coords):
    return piece(SimpleCapture(game_state, player).named('T'),
                 AngularMove(),
                 AngularMove(-1),
                 RadialMove(),
                 RadialMove(-1),
                 Tile(*coords))


def eagle(game_state, player, *coords):
    return piece(SimpleCapture(game_state, player).named('E'),
                 DiagonalMove(1, True, True, True),
                 DiagonalMove(-1, True, True, True),
                 DiagonalMove(1, False, True, True),
                 DiagonalMove(-1, False, True, True),
                 Tile(*coords))


if __name__ == "__main__":
    s = PolarChessGameState()
    Ly = lion(s, 'y', 4, 23)
    Lb = lion(s, 'b', 0, 0)
    y = ChessPlayer('y', s, Ly)
    b = ChessPlayer('b', s, Lb)
    g = SimpleTurn(s, y, b)

    s.add_pieces(bear(s, 'b', 1, 0))
    print(g.get_bottom_rule().player)
    for m in g.get_legal_moves():
        print(g.move_to_string(m))
    print("BEGIN EVALUATION")
    start = default_timer()
    print(g.max_n(4))
    stop = default_timer()
    print("END EVALUATION")
    print("time to complete:", stop - start)


'''
|                                  00                                   |  01
|       00        |       01        |       02        |       03        |  04
| 00  | 01  | 02  | 03  | 04  | 05  | 06  | 07  | 08  | 09  | 10  | 11  |  12
|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|  24
|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|  24
'''
