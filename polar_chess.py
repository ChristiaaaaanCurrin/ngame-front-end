from game_state import GameState
from rule import piece
from player import Player
from coordinate_rule import SimpleCapture, Tile, PatternRule


class PolarChessGameState(GameState):
    def __init__(self, *rings):
        if rings:
            self.rings = rings
        else:
            self.rings = (1, 4, 12, 24, 24)

        super().__init__()

    def __repr__(self):
        return str(self.rings)


class RadialMove(PatternRule):
    def __init__(self, step_size=1, patterns=True, jumps=False, sub_rule=Tile(0, 0)):
        super().__init__(name='radial ' + str(step_size) + ' ', sub_rule=sub_rule, game_state=PolarChessGameState())
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
    def __init__(self, step_size=1, patterns=True, jumps=False, sub_rule=Tile(0, 0)):
        super().__init__(name='angular ' + str(step_size), sub_rule=sub_rule, game_state=PolarChessGameState())
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
    def __init__(self, step_size=1, clockwise=True, patterns=True, jumps=False, sub_rule=Tile(0, 0)):

        super().__init__(name='diagonal ' + str(step_size) + ' ' + str(clockwise),
                         sub_rule=sub_rule, game_state=PolarChessGameState())
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
        for rule in self.game_state.get_top_rules():
            if hasattr(rule.get_bottom_rule(), 'coords'):
                if rule.get_bottom_rule().coords == coords:
                    return True
        else:
            return False


def lion(player, *coords):
    return piece(SimpleCapture('L', PolarChessGameState(), player),
                 RadialMove(1, False),
                 RadialMove(-1, False),
                 AngularMove(1, False),
                 AngularMove(-1, False),
                 Tile(*coords))


def leopard(player, *coords):
    return piece(SimpleCapture('P', PolarChessGameState(), player),
                 RadialMove(),
                 RadialMove(-1),
                 Tile(*coords))


def bear(player, *coords):
    return piece(SimpleCapture('B', PolarChessGameState(), player),
                 AngularMove(),
                 AngularMove(-1),
                 Tile(*coords))


def tiger(player, *coords):
    return piece(SimpleCapture('T', PolarChessGameState(), player),
                 AngularMove(),
                 AngularMove(-1),
                 RadialMove(),
                 RadialMove(-1),
                 Tile(*coords))


def eagle(player, *coords):
    return piece(SimpleCapture('E', PolarChessGameState(), player),
                 DiagonalMove(1, True, True, True),
                 DiagonalMove(-1, True, True, True),
                 DiagonalMove(1, False, True, True),
                 DiagonalMove(-1, False, True, True),
                 Tile(*coords))


x = PolarChessGameState()

x.add_pieces(leopard('y', 0, 0),
             eagle('y', 1, 0),
             leopard('b', 4, 23),
             bear('b', 2, 3))

for rule in x.get_top_rules():
    print(rule)
    print(rule.get_string_legal())


'''
|                                  00                                   |  01
|       00        |       01        |       02        |       03        |  04
| 00  | 01  | 02  | 03  | 04  | 05  | 06  | 07  | 08  | 09  | 10  | 11  |  12
|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|  24
|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|  24
'''