from rule import Rule
from abc import ABC
from game_state import GameState


class CoordinateRule(Rule, ABC):
    def __init__(self, name, coords, game_state=GameState(), player=None):
        super().__init__(name=name, game_state=game_state, player=player, successor=None)
        self.coords = coords

    def __repr__(self):
        return str(self.name) + str(self.coords)

    def execute_move(self, move):
        self.coords = move[0]

    def undo_move(self, move):
        self.coords = move[1]

    def get_utility(self):
        return {self.player: 1}


# -- Capture Rule -----------------------------------------

class CaptureRule(Rule, ABC):
    def __eq__(self, other):
        return other.get_bottom_rule() == self.get_bottom_rule()

    def attacks_piece(self, piece):
        """
        :param piece: piece that self might be 'attacking'
        :return: true if self 'attacks' piece
        """
        for sub_rule, sub_move, *pieces_to_capture in self.get_legal_moves():
            if piece in pieces_to_capture:
                return True
        else:
            return False

    def is_attacked(self):
        attacked = False
        for piece in self.game_state.get_top_rules():
            if piece.attacks_piece(self):
                attacked = True
                break
        return attacked

    def execute_move(self, move):
        sub_rule, sub_move, *pieces_to_capture = move
        self.game_state.remove_piece(*pieces_to_capture)
        sub_rule.execute_move(sub_move)

    def undo_move(self, move):
        sub_rule, sub_move, *pieces_to_capture = move
        sub_rule.undo_move(sub_move)
        self.game_state.add_pieces(*pieces_to_capture)


class SimpleCapture(CaptureRule):
    def __init__(self, name, game_state=GameState(), player=None, sub_rule=None, successor=None):
        super().__init__(name=name, game_state=game_state, player=player, sub_rule=sub_rule, successor=successor)

    def __repr__(self):
        return "Simple Capture " + str(self.sub_rule)

    def get_legal_moves(self):
        legal = []
        for new_coords, old_coords in self.sub_rule.get_legal_moves():
            to_capture = []
            for top_rule in self.game_state.get_top_rules():
                if hasattr(top_rule.get_bottom_rule(), 'coords') and top_rule.get_bottom_rule().coords == new_coords:
                    to_capture.append(top_rule)
            legal.append((self.sub_rule, (new_coords, old_coords), *to_capture))
        return legal

    def get_utility(self):
        return {self.player: 1}

