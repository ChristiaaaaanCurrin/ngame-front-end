from abc import ABC, abstractmethod
from game_state import GameState
from equality_modifiers import EqualityByArgs


class Rule(ABC):
    def __init__(self, name, game_state=GameState(), player=None, sub_rule=None, successor=None):
        self.name = name
        self.sub_rule = sub_rule
        self.player = player
        self.successor = successor
        self.game_state = game_state

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
        return self.sub_rule.get_bottom_rule()

    def get_piece(self):
        if self.sub_rule:
            return [self].extend(self.sub_rule.get_piece())
        else:
            return [self]


# -- Game -------------------------------------------------

class Game(Rule, ABC):
    def __init__(self, name, game_state=GameState(), sub_rule=None, history=None):
        super().__init__(name=name, game_state=game_state, player=None, sub_rule=sub_rule, successor=self)
        self.game_state.add_piece(self)
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


# -- Bottom Rule -----------------------------------------

class BottomRule(Rule, ABC):
    def __init__(self, name, game_state=GameState(), player=None, successor=None):
        super().__init__(name=name, game_state=game_state, player=player, sub_rule=None, successor=successor, )

    def get_bottom_rule(self):
        return self


# -- Player -----------------------------------------------
# Player Status

class PlayerStatus(EqualityByArgs):
    def __init__(self, tag, score, active):
        super().__init__(tag, score, active)
        self.tag = tag
        self.score = score
        self.active = active

    def utility_value(self, player_utility=1, total_utility=1):
        if self.score is not None:
            return self.score
        else:
            return player_utility / total_utility

    def __repr__(self):
        return str(self.tag)


win = PlayerStatus('w', 1, False)
lose = PlayerStatus('l', 0, False)
draw = PlayerStatus('d', None, False)
play_on = PlayerStatus('a', None, True)


# Player

class Player(BottomRule, ABC):
    def __init__(self, name, status, game_state=GameState(), successor=None):
        self.status = status
        super().__init__(name=name, player=self, successor=successor, game_state=game_state)

    def __repr__(self):
        return 'p' + str(self.name)


# -- Subordinate Rule ------------------------------------

class SubordinatePiece(Rule, ABC):
    def __eq__(self, other):
        return other.get_bottom_rule() == self.get_bottom_rule()

    @abstractmethod
    def attacks_piece(self, piece):
        """
        :param piece: piece that self might be 'attacking'
        :return: true if self 'attacks' piece
        """
        pass

    def is_attacked(self):
        attacked = False
        for piece in self.game_state.get_top_rules():
            if piece.attacks_piece(self):
                attacked = True
                break
        return attacked


# Rule Factory Method

def instantiate_pieces_from_integer(piece_class, number_of_pieces, game_state=GameState()):
    pieces = [piece_class(name=number_of_pieces, game_state=game_state)]
    for n in range(number_of_pieces - 1):
        pieces.append(piece_class(successor=pieces[n], name=number_of_pieces - 1 - n, game_state=game_state))
    pieces[0].successor = pieces[-1]
    pieces.reverse()
    return pieces

