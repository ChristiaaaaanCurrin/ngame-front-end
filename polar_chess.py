from game_state import GameState
from rule import piece, SimpleTurn, Rule, ZeroSum, stack
from coordinate_rule import SimpleCapture, Tile, PatternRule
from timeit import default_timer


class ChessGame(ZeroSum):
    def does_lose(self, player):
        return self.get_bottom_rule().player == player\
               and self.get_bottom_rule().is_in_check()\
               and not self.get_bottom_rule().get_legal_moves()

    def does_win(self, player):
        return self.active == [player] and not self.drawers

    def does_draw(self, player):
        return not self.get_legal_moves()


class ChessPlayer(Rule):
    def __init__(self, name, game_state=GameState(), *kings):
        super().__init__(name=name, player=name, game_state=game_state)
        self.kings = kings
        for king in self.kings:
            king.player = self.player

    def get_legal_moves(self):
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
        return {self.player: len(self.get_legal_moves())}


class RadialMove(PatternRule):
    def __init__(self, step_size=1, patterns=True, jumps=False, sub_rule=Tile(0, 0), player=None, **kwargs):
        super().__init__(sub_rule=sub_rule, game_state=GameState(), player=player, **kwargs)
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
    def __init__(self, step_size=1, patterns=True, jumps=False, sub_rule=Tile(0, 0), **kwargs):
        super().__init__(sub_rule=sub_rule, **kwargs)
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
    def __init__(self, step_size=1, clockwise=True, patterns=True, jumps=False, sub_rule=Tile(0, 0), **kwargs):
        super().__init__(sub_rule=sub_rule, **kwargs)

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

        if 0 <= (r + step) < len(rings) and rings[r + step] > 1 and rings[r] > 1:
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
    return piece(SimpleCapture(game_state=game_state, player=player, name='L'),
                 RadialMove(1, False),
                 RadialMove(-1, False),
                 AngularMove(1, False),
                 AngularMove(-1, False),
                 Tile(*coords))


def leopard(game_state, player, *coords):
    return piece(SimpleCapture(game_state=game_state, player=player, name='P'),
                 RadialMove(),
                 RadialMove(-1),
                 Tile(*coords))


def bear(game_state, player, *coords):
    return piece(SimpleCapture(game_state=game_state, player=player, name='B'),
                 AngularMove(),
                 AngularMove(-1),
                 Tile(*coords))


def tiger(game_state, player, *coords):
    return piece(SimpleCapture(game_state=game_state, player=player, name='T'),
                 AngularMove(),
                 AngularMove(-1),
                 RadialMove(),
                 RadialMove(-1),
                 Tile(*coords))


def eagle(game_state, player, *coords):
    return piece(SimpleCapture(game_state=game_state, player=player, name='E'),
                 DiagonalMove(1, True, True, True),
                 DiagonalMove(-1, True, True, True),
                 DiagonalMove(1, False, True, True),
                 DiagonalMove(-1, False, True, True),
                 Tile(*coords))


if __name__ == "__main__":
    piece_state = GameState(rings=(1, 4, 12, 24, 24))
    y = ChessPlayer('y', piece_state, lion(piece_state, 'y', 2, 1))
    b = ChessPlayer('b', piece_state, lion(piece_state, 'b', 3,  11))
    bear(piece_state, 'b', 3, 0)
    bear(piece_state, 'y', 3, 4)
    bear(piece_state, 'b', 3, 10)
    bear(piece_state, 'y', 3, 5)
    g = stack(ChessGame('y', 'b'), SimpleTurn(y, b, game_state=piece_state))

    if True:
        print("BEGIN EVALUATION")
        start = default_timer()
        for n in range(1, 6):
            print("***", n, "***")
            print(g.max_n(depth=2, width=1, temp=0, k=n))
            print(default_timer() - start)
        print("END EVALUATION")


'''
|                                  00                                   |  01
|       00        |       01        |       02        |       03        |  04
| 00  | 01  | 02  | 03  | 04  | 05  | 06  | 07  | 08  | 09  | 10  | 11  |  12
|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|  24
|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|  24
'''
