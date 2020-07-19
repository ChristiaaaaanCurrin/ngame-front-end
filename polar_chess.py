from game_state import GameState
from rule import Rule, RuleSum
from player import Player
from coordinate_rule import SimpleCapture, CoordinateRule


class PolarChessGameState(GameState):
    def __init__(self, *rings):
        if rings:
            self.rings = rings
        else:
            self.rings = (1, 4, 12, 24, 24)

        super().__init__()

    def __repr__(self):
        return str(self.rings)


class RadialMove(CoordinateRule):
    def __init__(self, coords, step_size=1, game_state=PolarChessGameState(), player=None):
        super().__init__(name='radial ' + str(step_size), coords=coords, game_state=game_state, player=player)
        self.step_size = step_size

    def get_legal_moves(self):
        r = self.coords[0]
        t = self.coords[1]
        step = self.step_size
        rings = self.game_state.rings
        size = rings[r]

        if 0 <= (r + step) < len(rings):
            new_size = rings[r + self.step_size]
            return [((r + step, new_t), self.coords) for new_t in range(t * new_size // size % new_size,
                                                                        new_size - (size - t - 1) * new_size // size)]
        else:
            return []


class AngularMove(CoordinateRule):
    def __init__(self, coords, step_size=1, game_state=PolarChessGameState(), player=None):
        super().__init__(name='radial ' + str(step_size), coords=coords, game_state=game_state, player=player)
        self.step_size = step_size

    def get_legal_moves(self):
        sizes = self.game_state.rings
        r = self.coords[0]
        t = self.coords[1]
        new_t = (t + self.step_size) % sizes[r]
        return [((r, new_t), self.coords)]


x = PolarChessGameState()
x.add_pieces(SimpleCapture('t', PolarChessGameState(), 'p1', RadialMove((1, 0), 1)),
             SimpleCapture('s', PolarChessGameState(), 'p2', AngularMove((2, 0))))

piece_4 = SimpleCapture('r', PolarChessGameState(), 'p1',
                        RuleSum(None, GameState(), None, None, RadialMove((0, 0), 1), RadialMove((0, 0), -1)))

x.add_pieces(piece_4)


for top_rule in x.get_top_rules():
    print(top_rule)
    print(top_rule.get_legal_moves())
