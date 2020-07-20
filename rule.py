from abc import ABC, abstractmethod
from game_state import GameState, dictionary_max


class Rule(ABC):
    def __init__(self, name, game_state=None, player=None, sub_rule=None, successor=None):
        self.name = name
        self.game_state = game_state
        self.player = player
        self.sub_rule = sub_rule
        self.successor = successor

    def __repr__(self):
        return str(self.name)

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


# -- Game -------------------------------------------------

class Game(Rule, ABC):
    def __init__(self, name, game_state=GameState(), sub_rule=None, history=None):
        super().__init__(name=name, game_state=game_state, player=None, sub_rule=sub_rule, successor=self)
        self.game_state.add_pieces(self)
        if history:
            self.history = history
        else:
            self.history = []

    def __repr__(self):
        return 'turn: ' + str(self.sub_rule)

    def execute_move(self, move):
        self.sub_rule = move[0]
        for rule, sub_move in move[2]:
            rule.execute_move(sub_move)
        self.history.append(move)

    def undo_move(self, move):
        for rule, sub_move in move[2]:
            rule.undo_move(sub_move)
        self.sub_rule = move[1]

    def revert(self):
        self.undo_move(self.history.pop(-1))


class SimpleTurn(Game):
    def get_legal_moves(self):
        legal = []
        for move in self.sub_rule.get_legal_moves():
            legal.append((self.sub_rule.successor, self.sub_rule, [(self.sub_rule, move)]))
        return legal

    def get_utility(self):
        utility = {}
        for player in self.game_state.get_players():
            utility.update(player.get_utility())
        return utility


# -- Combining Rule --------------------------------------- TODO This may be a little janky and unnecessary...

class RuleSum(Rule):
    def __init__(self, name=None, game_state=GameState(), player=None, successor=None, *sub_rules):
        self.all_subs = []
        for rule in sub_rules:
            self.all_subs.append(rule)
        super().__init__(name=name, game_state=game_state, player=player, successor=successor, sub_rule=sub_rules)

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
        piece = [self]
        [piece.extend(rule.get_piece()) for rule in self.sub_rule]
        return piece

    def get_utility(self):
        return dictionary_max(self.player, [rule.get_utility() for rule in self.sub_rule])


# -- Rule Factory Method ----------------------------------

def instantiate_rules_from_integer(rule_class, number_of_pieces, game_state=GameState()):
    rules = [rule_class(name=number_of_pieces, game_state=game_state)]
    for n in range(number_of_pieces - 1):
        rules.append(rule_class(successor=rules[n], name=number_of_pieces - 1 - n, game_state=game_state))
    rules[0].successor = rules[-1]
    rules.reverse()
    return rules


# -- Piece creator Method ---------------------------------

def piece(*rules):
    for i, rule in enumerate(rules[:-1]):
        rule.sub_rule = rules[i+1]
    rules[0].game_state.add_pieces(rules[0])
    return rules[0]
