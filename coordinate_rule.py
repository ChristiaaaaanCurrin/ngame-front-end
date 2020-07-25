from rule import Rule
from abc import ABC, abstractmethod
from game_state import GameState


class Tile(Rule):
    def __init__(self, *coords):
        super().__init__()
        self.coords = coords

    def __eq__(self, other):
        return hasattr(other, 'coords') and self.coords == other.coords

    def __repr__(self):
        return str(self.coords)

    def get_legal_moves(self):
        return []

    def execute_move(self, move):
        self.coords = move[0]

    def undo_move(self, move):
        self.coords = move[1]

    def get_utility(self):
        return {self.player: 0}


class CoordinateRule(Rule, ABC):
    def __init__(self, game_state=GameState(), player=None, sub_rule=None):
        super().__init__(game_state=game_state, player=player, sub_rule=sub_rule)

    def string_legal(self):
        string_legal = []
        for new_coords, old_coords in self.get_legal_moves():
            string_legal.append(new_coords)
        return string_legal

    def execute_move(self, move):
        self.get_bottom_rule().execute_move(move)

    def undo_move(self, move):
        self.get_bottom_rule().undo_move(move)

    def get_utility(self):
        return {self.player: 0}


# -- Pattern Rule -----------------------------------------

class PatternRule(CoordinateRule, ABC):
    @abstractmethod
    def get_step(self, coords):
        pass

    @abstractmethod
    def does_stop_on(self, coords):
        pass

    @abstractmethod
    def does_skip(self, coords):
        pass

    def get_legal_moves(self):
        edge = self.get_step(self.get_bottom_rule().coords)
        legal = self.sub_rule.get_legal_moves()
        while edge:
            new_edge = []
            for coords in edge:
                if not self.does_skip(coords):
                    legal.append((coords, self.get_bottom_rule().coords))
                if not self.does_stop_on(coords):
                    new_edge.extend(self.get_step(coords))
            edge = new_edge
        return legal


# -- Capture Rule -----------------------------------------

class CaptureRule(Rule, ABC):
    def __eq__(self, other):
        return other.get_bottom_rule() == self.get_bottom_rule()

    def does_attack_piece(self, piece):
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
            if hasattr(piece, 'does_attack_piece') and piece.does_attack_piece(self):
                attacked = True
                break
        return attacked

    def execute_move(self, move):
        sub_rule, sub_move, *pieces_to_capture = move
        self.game_state.remove_pieces(*pieces_to_capture)
        sub_rule.execute_move(sub_move)

    def undo_move(self, move):
        sub_rule, sub_move, *pieces_to_capture = move
        sub_rule.undo_move(sub_move)
        self.game_state.add_pieces(*pieces_to_capture)


class SimpleCapture(CaptureRule):
    def __init__(self, game_state=GameState(), player=None, sub_rule=None):
        super().__init__(game_state=game_state, player=player, sub_rule=sub_rule)

    def get_string_legal(self):
        string_legal = ''
        for sub_rule, (new_coords, old_coords), *to_capture in self.get_legal_moves():
            string_legal = string_legal + str(new_coords)
            if to_capture:
                string_legal = string_legal + 'X' + str(to_capture)
            string_legal = string_legal + ', '
        return string_legal

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

