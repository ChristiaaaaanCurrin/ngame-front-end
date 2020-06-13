from abc import ABC, abstractmethod
from equality_modifiers import EqualityByArgs
from new_piece import Piece

# Basic Player Status Classes

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


# Basic Player Statuses

win = PlayerStatus('w', 1, False)
lose = PlayerStatus('l', 0, False)
draw = PlayerStatus('d', None, False)
play_on = PlayerStatus('a', None, True)


# Basic Player Classes

class Player(Piece, ABC):
    def __init__(self, successor, tag, status=play_on):
        super().__init__(player=self, successor=successor)
        self.status = status
        self.tag = tag

    def __repr__(self):
        return 'p' + str(self.tag)

    @abstractmethod
    def utility(self, game_state):
        pass

