from game_state import GameState
from rule import piece, SimpleTurn, Rule
from coordinate_rule import SimpleCapture, Tile, PatternRule


class Key:
    DEFAULT = 0
    PLAYER = 1
    PIECE = 2


class ChessPlayer(Rule):
    def __init__(self, *kings, **kwargs):
        super().__init__(**kwargs)
        self.kings = kings
        for king in self.kings:
            king.player = self.player

    def __repr__(self):
        return 'ChessPlayer(%s)' % str(self.player)

    def generate_legal_moves(self):
        legal = []
        for top_rule in self.game_state.filter_top_rules(self.player, Key.PIECE):
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
        self.changed()

    def undo_move(self, move):
        sub_rule, sub_move = move
        sub_rule.undo_move(sub_move)
        self.changed()


class RadialMove(PatternRule):
    def __init__(self, step_size=1, patterns=True, jumps=False, sub_rule=Tile(0, 0), **kwargs):
        self.radar = []
        super().__init__(sub_rule=sub_rule, **kwargs)
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
        self.radar = []
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
        for rule in self.game_state.filter_top_rules(self.player, *self.radar):
            if rule.get_coords() == coords:
                return True
        else:
            return False

    def does_stop_on(self, coords):
        if not self.patterns:
            return True
        for rule in self.game_state.filter_top_rules(*self.radar):
            if rule.get_coords() == coords:
                return True
        else:
            return False


class DiagonalMove(PatternRule):
    def __init__(self, step_size=1, clockwise=True, patterns=True, jumps=False, sub_rule=Tile(0, 0), **kwargs):
        self.radar = []
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
        for rule in self.game_state.get_top_rules(*self.radar):
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


def lion(game_state, player, *coords, **kwargs):
    kwargs = {'game_state': game_state, 'keys': (Key.PIECE, player),
              'player': player, 'name': 'L' + str(player), 'radar': [Key.PIECE],
              'subscriptions': [game_state.changed], **kwargs}
    return piece(SimpleCapture(),
                 RadialMove(1, False),
                 RadialMove(-1, False),
                 AngularMove(1, False),
                 AngularMove(-1, False),
                 Tile(*coords), **kwargs)


def leopard(game_state, player, *coords, **kwargs):
    kwargs = {'game_state': game_state, 'keys': (Key.PIECE, player),
              'player': player, 'name': 'P' + str(player), 'radar': [Key.PIECE],
              'subscriptions': [game_state.changed], **kwargs}
    return piece(SimpleCapture(),
                 RadialMove(),
                 RadialMove(-1),
                 Tile(*coords), **kwargs)


def bear(game_state, player, *coords, **kwargs):
    kwargs = {'game_state': game_state, 'keys': (Key.PIECE, player),
              'player': player, 'name': 'B' + str(player), 'radar': [Key.PIECE],
              'subscriptions': [game_state.changed], **kwargs}
    return piece(SimpleCapture(),
                 AngularMove(),
                 AngularMove(-1),
                 Tile(*coords), **kwargs)


def tiger(game_state, player, *coords, **kwargs):
    kwargs = {'game_state': game_state, 'keys': (Key.PIECE, player),
              'player': player, 'name': 'T' + str(player), 'radar': [Key.PIECE],
              'subscriptions': [game_state.changed], **kwargs}
    return piece(SimpleCapture(),
                 AngularMove(),
                 AngularMove(-1),
                 RadialMove(),
                 RadialMove(-1),
                 Tile(*coords), **kwargs)


def eagle(game_state, player, *coords, **kwargs):
    kwargs = {'game_state': game_state, 'keys': (Key.PIECE, player),
              'player': player, 'name': 'E'+str(player), 'radar': [Key.PIECE],
              'subscriptions': [game_state.changed], **kwargs}
    return piece(SimpleCapture(),
                 DiagonalMove(1, True, True, True),
                 DiagonalMove(-1, True, True, True),
                 DiagonalMove(1, False, True, True),
                 DiagonalMove(-1, False, True, True),
                 Tile(*coords), **kwargs)


def polar_chess(*piece_strings, rings=(1, 4, 12, 24, 24)):
    state = GameState(rings=rings)
    piece_types = {'L': lion, 'T': tiger, 'B': bear, 'P': leopard, 'E': eagle}
    player_strings = []
    for piece_string in piece_strings:
        t, p, *coords = piece_string

    Ly = lion(state, 'y', 4, 1)
    Lb = lion(state, 'b', 1, 2)

    y = ChessPlayer(Ly, name='y', player='y', keys=[Key.PLAYER, 'y'])
    b = ChessPlayer(Lb, name='b', player='b', keys=[Key.PLAYER, 'b'])

    game = SimpleTurn(y, b)

    state.add_rules(game, Ly, Lb, y, b,
                    eagle(state, 'b', 0, 0),
                    bear(state, 'y', 3, 3),
                    bear(state, 'y', 4, 23))
    return game


if __name__ == "__main__":
    test_game = polar_chess("haha")
    print(test_game.game_state)
    test_tiger = test_game.game_state.filter_top_rules(Key.PIECE)[-2]
    [print(test_game.move_to_string(move)) for move in test_game.get_legal_moves()]


'''
|                                  00                                   |  01
|       00        |       01        |       02        |       03        |  04
| 00  | 01  | 02  | 03  | 04  | 05  | 06  | 07  | 08  | 09  | 10  | 11  |  12
|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|  24
|00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|  24
'''
