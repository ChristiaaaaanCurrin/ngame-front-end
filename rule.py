from abc import ABC, abstractmethod
from game_state import GameState
from evaluator import max_by_key
from random import sample, random


class Rule(ABC):
    def __init__(self, **kwargs):
        self.game_state = GameState()
        self.keys = ['state']
        self.watch = []
        self.sub_rule = None
        self.name = "rule"
        self.player = None
        self.__dict__.update(kwargs)

    def __str__(self):
        return str(self.name) + str(self.sub_rule)

    def requirements(self):
        requirements = {}
        if self.sub_rule:
            requirements.update(self.sub_rule.requirements())
        return requirements

    def minimal(self):
        return type('Minimal' + self.__name__, (object,), self.requirements())

    @abstractmethod
    def get_legal_moves(self):
        """
        :return: list of legal moves for self, moves must contain enough information to be reversed
        """
        pass

    @abstractmethod
    def execute_move(self, move):  # TODO add optional *args for open ended moves?
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
        """
        :return: dictionary of values keyed by players. should be between 0 and 1
        """
        pass

    @staticmethod
    def move_to_string(move):
        """
        :param move: same type as element of self.get_legal_moves()
        :return: human - friendly string of move
        """
        return str(move)

    def get_bottom_rule(self):
        """
        :return: last element of linked list of sub_rules ( =self.get_piece()[-1] )
        """
        if self.sub_rule:
            return self.sub_rule.get_bottom_rule()
        else:
            return self

    def get_player(self):
        if self.player:
            return self.player
        elif self.sub_rule:
            return self.sub_rule.get_player()
        else:
            return None

    def get_piece(self):
        """
        :return: linked list of sub_rules
        """
        if self.sub_rule:
            return [self] + self.sub_rule.get_piece()
        else:
            return [self]

    def max_n(self, depth, width=-1, temp=1, k=1):
        """
        searches game tree and applies max_n algorithm to evaluate current game
        :param depth: maximum depth of search
        :param width: maximum branches from this node
        :param temp: probability of selecting the child branches randomly
        :param k: depth of intermediate searches for determining continuation line
        :return: evaluation of current game ( = utility from the end of the expected branch)
        """

        player = self.get_player()
        legal = self.get_legal_moves()
        if 0 <= width < len(legal):
            if temp < random():
                def evaluate(m):
                    self.execute_move(m)
                    utility = self.max_n(k)[player]
                    self.undo_move(m)
                    return utility
                legal = sorted(legal, key=evaluate)[:width]
            else:
                legal = sample(self.get_legal_moves(), width)
        if depth == 0 or not legal:
            return self.get_utility()
        else:
            utilities = []
            for move in legal:
                self.execute_move(move)
                utilities.append(self.max_n(depth - 1, width, temp))
                self.undo_move(move)
            return max_by_key(player, utilities)


# -- Player and Turn Handlers -----------------------------

class SimpleTurn(Rule):
    def __init__(self, *sub_rules, turn=0, **kwargs):
        self.sequence = sub_rules
        self.turn = turn % len(self.sequence)
        super().__init__(sub_rule=self.sequence[0], **kwargs)

    def __str__(self):
        return 'turn: ' + str(self.sub_rule)

    def get_legal_moves(self):
        legal = []
        for sub_move in self.sub_rule.get_legal_moves():
            legal.append((self.sub_rule, sub_move))
        return legal

    @staticmethod
    def move_to_string(move):
        sub_rule, sub_move = move
        return sub_rule.move_to_string(sub_move)

    def execute_move(self, move=None):
        self.turn = (self.turn + 1) % len(self.sequence)
        self.sub_rule = self.sequence[self.turn]
        if move:
            sub_rule, sub_move = move
            sub_rule.execute_move(sub_move)

    def undo_move(self, move=None):
        if move:
            sub_rule, sub_move = move
            sub_rule.undo_move(sub_move)
        self.turn = (self.turn - 1) % len(self.sequence)
        self.sub_rule = self.sequence[self.turn]

    def get_utility(self):
        utility = {}
        for sub_rule in self.sequence:
            utility.update(sub_rule.get_utility())
        return utility


class WinLoseDraw(Rule, ABC):
    def __init__(self, *players, sub_rule=None, **kwargs):
        super().__init__(sub_rule=sub_rule, **kwargs)
        self.players = players
        self.active = list(self.players)
        self.winners = []
        self.losers = []
        self.drawers = []
        self.history = []

    @abstractmethod
    def does_win(self, player):
        pass

    @abstractmethod
    def does_lose(self, player):
        pass

    @abstractmethod
    def does_draw(self, player):
        pass

    @abstractmethod
    def win_lose_draw(self):
        pass

    def get_legal_moves(self):
        if self.active:
            return self.sub_rule.get_legal_moves()
        else:
            return []

    def execute_move(self, move):
        self.sub_rule.execute_move(move)
        self.history.append((self.winners, self.losers, self.drawers, self.active))
        self.win_lose_draw()

    def undo_move(self, move):
        self.sub_rule.undo_move(move)
        self.winners, self.losers, self.drawers, self.active = self.history.pop(-1)


class ZeroSum(WinLoseDraw, ABC):
    def win_lose_draw(self):
        win = []
        lose = []
        draw = []
        for p, player in enumerate(self.active):
            if self.does_win(player):
                win.append(self.active.pop(p))
            elif self.does_lose(player):
                lose.append(self.active.pop(p))
            elif self.does_draw(player):
                draw.append(self.active.pop(p))
        self.drawers.extend(draw)
        self.losers.extend(lose)
        self.winners = win
        if self.winners:
            self.losers.extend(self.active)
            self.losers.extend(self.drawers)
            self.active.clear()
            self.drawers.clear()

    def get_utility(self):
        utilities = {}
        active = len(self.active)
        draw = len(self.drawers)
        sharing_players = active + draw
        for player in self.winners:
            utilities[player] = 1
        for player in self.losers:
            utilities[player] = 0
        for player in self.drawers:
            utilities[player] = 1 / sharing_players
        if self.active:
            total_utility = sum(map(lambda p: self.sub_rule.get_utility()[p], self.active)) * sharing_players / active
            for player in self.active:
                utilities[player] = self.sub_rule.get_utility()[player] / total_utility
        return utilities


# -- Piece Creator Functions ------------------------------

def piece(*rules, **kwargs):
    for i, rule in enumerate(rules[:-1]):
        rule.sub_rule = rules[i+1]
        rule.__dict__.update(kwargs)
    rules[-1].__dict__.update(kwargs)
    rules[0].game_state.add_rules(rules[0])
    return rules[0]
