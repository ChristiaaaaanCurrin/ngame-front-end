from abc import ABC, abstractmethod
from game_state import GameState, dictionary_max


class Rule(ABC):
    def __init__(self, game_state=None, player=None, sub_rule=None):
        self.game_state = game_state
        self.player = player
        self.sub_rule = sub_rule

    @abstractmethod
    def get_legal_moves(self):
        """
        :return: list of legal moves for self in game state
                 moves must contain enough information to be reversed
        """
        pass

    @abstractmethod
    def execute_move(self, move):
        """
        carries out instructions in move
        :param move: same type as an element of self.legal_moves() output
        """
        pass

    @abstractmethod
    def undo_move(self, move):
        """
        carries out inverse operation of self.execute_move(move)
        :param move: same type as an element of self.legal_moves() output
        """
        pass

    @abstractmethod
    def get_utility(self):
        pass

    def get_bottom_rule(self):
        if self.sub_rule:
            return self.sub_rule.get_bottom_rule()
        else:
            return self

    def get_piece(self):
        if self.sub_rule:
            return [self] + self.sub_rule.get_piece()
        else:
            return [self]

    def max_n(self, n):
        legal = self.get_legal_moves()
        if n == 0 or not legal:
            return self.get_utility()
        else:
            utilities = []
            for move in legal:
                self.execute_move(move)
                utilities.append(self.max_n(n-1))
                self.undo_move(move)
            if self.player:
                return dictionary_max(self.player, utilities)
            elif self.sub_rule:
                return dictionary_max(self.get_bottom_rule().player, utilities)


# -- Game -------------------------------------------------

class Game(Rule, ABC):
    def __init__(self, game_state=GameState(), sub_rule=None):
        super().__init__(game_state=game_state, player=None, sub_rule=sub_rule)
        self.game_state.add_pieces(self)

    def __repr__(self):
        return 'turn: ' + str(self.sub_rule)

    def execute_move(self, move):
        self.sub_rule = move[0]
        for rule, sub_move in move[2]:
            rule.execute_move(sub_move)

    def undo_move(self, move):
        for rule, sub_move in move[2]:
            rule.undo_move(sub_move)
        self.sub_rule = move[1]


class SimpleTurn(Game):
    def __init__(self, game_state, *sub_rules, turn=0):
        self.sequence = sub_rules
        self.turn = turn % len(self.sequence)
        super().__init__(game_state=game_state, sub_rule=self.sequence[0])

    def get_legal_moves(self):
        legal = []
        for move in self.sub_rule.get_legal_moves():
            legal.append((self.sub_rule, move))
        return legal

    def execute_move(self, move):
        sub_rule, sub_move = move
        self.turn = (self.turn + 1) % len(self.sequence)
        self.sub_rule = self.sequence[self.turn]
        sub_rule.execute_move(sub_move)

    def undo_move(self, move):
        sub_rule, sub_move = move
        sub_rule.undo_move(sub_move)
        self.turn = (self.turn - 1) % len(self.sequence)
        self.sub_rule = self.sequence[self.turn]

    def get_utility(self):
        utility = {}
        for sub_rule in self.sequence:
            utility.update(sub_rule.get_utility())
        return utility


# -- Combining Rule ---------------------------------------

class RuleSum(Rule):  # TODO This may be a little janky and unnecessary...
    def __init__(self, game_state=GameState(), player=None, *sub_rules):
        self.all_subs = []
        for rule in sub_rules:
            self.all_subs.append(rule)
        super().__init__(game_state=game_state, player=player, sub_rule=sub_rules)

    def __repr__(self):
        return 'Sum' + str([str(rule) for rule in self.sub_rule])

    def get_legal_moves(self):
        legal = []
        for rule in self.sub_rule:
            for sub_move in rule.get_legal_moves():
                legal.append((rule, sub_move))
        return legal

    def execute_move(self, move):
        rule, sub_move = move
        rule.execute_move(sub_move)

    def undo_move(self, move):
        rule, sub_move = move
        rule.undo_move(sub_move)

    def get_bottom_rule(self):
        if self.sub_rule:
            return self.sub_rule[-1].get_bottom_rule()
        else:
            return self

    def get_piece(self):
        this_piece = [self]
        [this_piece.extend(rule.get_piece()) for rule in self.sub_rule]
        return this_piece

    def get_utility(self):
        return dictionary_max(self.player, [rule.get_utility() for rule in self.sub_rule])


# -- Piece creator Method ---------------------------------

def piece(*rules):
    player = rules[0].player
    for i, rule in enumerate(rules[:-1]):
        rule.sub_rule = rules[i+1]
        rule.player = player
    rules[0].game_state.add_pieces(rules[0])
    return rules[0]
