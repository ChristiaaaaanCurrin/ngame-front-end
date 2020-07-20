from game_state import GameState
from rule import Rule, RuleSum, piece
from player import Player
from coordinate_rule import SimpleCapture, Tile, MovementRule


class PolarChessGameState(GameState):
    def __init__(self, *rings):
        if rings:
            self.rings = rings
        else:
            self.rings = (1, 4, 12, 24, 24)

        super().__init__()

    def __repr__(self):
        return str(self.rings)


class RadialMove(MovementRule):
    def __init__(self, sub_rule=Tile(0, 0), step_size=1):
        super().__init__(name='radial ' + str(step_size) + ' ', sub_rule=sub_rule, game_state=PolarChessGameState())
        self.step_size = step_size

    def get_legal_moves(self):
        tile = self.get_bottom_rule()
        r = tile.coords[0]
        t = tile.coords[1]
        step = self.step_size
        rings = self.game_state.rings
        size = rings[r]

        legal = self.sub_rule.get_legal_moves()
        if 0 <= (r + step) < len(rings):
            new_size = rings[r + self.step_size]
            starting_coord = t * new_size // size % new_size
            ending_coord = new_size - (size - t - 1) * new_size // size
            legal.extend([((r + step, new_t), tile.coords) for new_t in range(starting_coord, ending_coord)])
        return legal


class AngularMove(MovementRule):
    def __init__(self, step_size=1, sub_rule=Tile(0, 0)):
        super().__init__(name='angular ' + str(step_size), sub_rule=sub_rule, game_state=PolarChessGameState())
        self.step_size = step_size

    def get_legal_moves(self):
        tile = self.get_bottom_rule()
        rings = self.game_state.rings
        r = tile.coords[0]
        t = tile.coords[1]
        new_t = (t + self.step_size) % rings[r]
        return self.sub_rule.get_legal_moves() + [((r, new_t), tile.coords)]


x = PolarChessGameState()
x.add_pieces(SimpleCapture('t', PolarChessGameState(), 'p1', RadialMove(sub_rule=Tile(1, 0), step_size=1)),
             SimpleCapture('s', PolarChessGameState(), 'p2', RadialMove(sub_rule=Tile(2, 0))))

rule_5 = piece(SimpleCapture('r', PolarChessGameState(), 'p1'),
               RadialMove(step_size=1),
               RadialMove(step_size=-1),
               Tile(3, 3))

x.add_pieces(rule_5)

c
for top_rule in x.get_top_rules():
    print(top_rule)
    print(top_rule.get_legal_moves())
