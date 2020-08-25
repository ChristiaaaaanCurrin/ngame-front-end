from abc import ABC, abstractmethod
from game_state import GameState
from event import Event, Subscriber


class Rule(ABC, Subscriber):
    def __init__(self, **kwargs):
        """
        :param game_state: GameState, all rules in the same game should have the same game state
        :param keys: dictionary key in self.game_state.top_rules
        :param sub_rule: next rule in linked piece
        :param name: string representation of rule
        :param player: player who "owns" self
        """
        super().__init__()  # initiates rule as a subscriber
        self.changed = Event()  # Event that broadcasts changes to self
        self.game_state = GameState()  # all rules in the same game should have the same game state
        self.keys = [0]  # keys determine how the rule is binned in the game state
        # each key corresponds with a dictionary entry in self.game_state.top_rules
        self.sub_rule = None  # the next rule in the linked "piece"
        self.name = ""  # string representation of the rule
        self.player = None  # player who "owns" self
        self.legal = []  # stored list of legal moves according to self. this list is updated on subscribed events
        self.__dict__.update(kwargs)
        super().__init__(self.game_state.changed)

    def __repr__(self):
        if self.name:
            return str(self.name)
        else:
            return str(type(self).__name__) + '(%s)' % self.sub_rule.__repr__()

    def requirements(self):
        """
        :return: dictionary of attributes sought by self, keyed by attribute names
        """
        requirements = {}
        if self.sub_rule:
            requirements.update(self.sub_rule.requirements())
        return requirements

    def minimal(self):
        """
        :return: custom type with the required attributes to interact with self
        """
        return type('Minimal' + self.__name__, (object,), self.requirements())

    @abstractmethod
    def generate_legal_moves(self):
        """
        :return: iterable containing legal moves for self, moves must contain enough information to be reversed
        """
        pass

    def get_legal_moves(self):
        """
        :return: list of legal moves for self, moves must contain enough information to be reversed
        """
        if self.update_flag:
            self.legal = self.generate_legal_moves()
            self.update_flag = False
        return self.legal

    @abstractmethod
    def execute_move(self, move):  # TODO add optional *args for open ended moves?
        """
        carries out instructions in move. must call self.changed()
        :param move: same type as an element of self.legal_moves() output
        """
        pass

    @abstractmethod
    def undo_move(self, move):
        """
        carries out inverse operation of self.execute_move(move). must call self.changed()
        :param move: same type as an element of self.legal_moves() output
        """
        pass

    @staticmethod
    def move_to_string(move):
        """
        :param move: same type as element of self.get_legal_moves()
        :return: human - friendly string of move
        """
        return str(move)

    def get_piece(self):
        """
        :return: the linked list of sub_rules underneath self
        """
        if self.sub_rule:
            return [self] + self.sub_rule.get_piece()
        else:
            return [self]

    def get_bottom_rule(self):
        """
        :return: last element of linked list of sub_rules ( =self.get_piece()[-1] )
        """
        if self.sub_rule:
            return self.sub_rule.get_bottom_rule()
        else:
            return self

    def get_player(self):
        """
        :return: the player who owns (and would control) self
        """
        if self.player:
            return self.player
        elif self.sub_rule:
            return self.sub_rule.get_player()
        else:
            return None


# -- Player and Turn Handlers -----------------------------

class SimpleTurn(Rule):
    def __init__(self, *sub_rules, turn=0, **kwargs):
        """
        :param sub_rules: list of rules that this rule cycles through
        :param turn: turn that this rule is on
        :param kwargs: passed to Rule.__init__()
        """
        self.sequence = sub_rules
        self.turn = turn % len(self.sequence)
        super().__init__(sub_rule=self.sequence[0], **kwargs)

    def get_piece(self):
        """
        This rule includes all its sub rules in its piece
        """
        this_piece = [self]
        [this_piece.extend(sub_rule.get_piece()) for sub_rule in self.sequence]
        return this_piece

    def generate_legal_moves(self):
        """
        gets legal moves of current child
        """
        legal = []
        for sub_move in self.sub_rule.get_legal_moves():
            legal.append((self.sub_rule, sub_move))
        return legal

    @staticmethod
    def move_to_string(move):
        sub_rule, sub_move = move
        return sub_rule.move_to_string(sub_move)

    def execute_move(self, move=None):
        """
        increments turn and updates current sub_rule, then asks sub_rule to execute sub_move
        :param move: (sub_piece (piece to execute move), sub_move (move to be executed))
        """
        self.turn = (self.turn + 1) % len(self.sequence)
        self.sub_rule = self.sequence[self.turn]
        if move:
            sub_rule, sub_move = move
            sub_rule.execute_move(sub_move)
        self.changed()

    def undo_move(self, move=None):
        """
        increments turn in reverse and updates current sub_rule, then asks sub_rule to undo sub_move
        :param move: (sub_piece (piece to undo move), sub_move(move to be undone))
        """
        if move:
            sub_rule, sub_move = move
            sub_rule.undo_move(sub_move)
        self.turn = (self.turn - 1) % len(self.sequence)
        self.sub_rule = self.sequence[self.turn]
        self.changed()


# -- Piece Creator Functions ------------------------------

def piece(*rules, **kwargs):
    """
    arranges rules into a linked (by sub_rule attribute) list and sets attributes specified by kwargs to be the same
    across all rules
    :param rules: rules to be linked
    :param kwargs: attributes for all rules in piece to share
    :return: top rule of new piece
    """
    kwargs = {**kwargs}
    for i, rule in enumerate(rules[:-1]):
        rule.sub_rule = rules[i+1]
        rule.__dict__.update(kwargs)
    rules[-1].__dict__.update(kwargs)
    return rules[0]


if __name__ == "__main__":
    pass