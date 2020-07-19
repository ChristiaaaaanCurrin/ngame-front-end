from equality_modifiers import EqualityByArgs
from rule import Rule
from game_state import GameState
from abc import ABC


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

class Player(Rule, ABC):
    def __init__(self, name, status, game_state=GameState(), successor=None):
        self.status = status
        super().__init__(name=name, player=self, successor=successor, game_state=game_state)
        self.game_state.add_players(self)

    def __repr__(self):
        return 'p' + str(self.name)