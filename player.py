from abc import ABC, abstractmethod
from enum import Enum
from equality_modifiers import EqualityByType


# Basic Player Status Classes

class PlayerStatus(Enum):
    WIN = 1
    LOSE = 0
    DRAW = -2
    PLAY_ON = -1

    def utility_value(self, total):
        if self == PlayerStatus.WIN:
            return 1
        elif self == PlayerStatus.LOSE:
            return 0
        elif self == PlayerStatus.PLAY_ON:
            return 1 / total
        elif self == PlayerStatus.DRAW:
            return 1 / total
        else:
            return 9999

'''
class Win(PlayerStatus):
    def utility_value(self, total):
        return 1

    def __repr__(self):
        return 'Win'


class Lose(PlayerStatus):
    def utility_value(self, total):
        return 0

    def __repr__(self):
        return 'Lose'


class Draw(PlayerStatus):
    def utility_value(self, total):
        return 1 / total

    def __repr__(self):
        return 'Draw'


class PlayOn(PlayerStatus):
    def value(self, total):
        return 1 / total

    def __repr__(self):
        return 'PlayOn'

'''

# Basic Player Classes

class Player(ABC):
    def __init__(self):
        self.status = PlayerStatus.PLAY_ON

    @abstractmethod
    def turn(self):
        pass


class SimplePlayer(Player):
    def __init__(self, successor, tag):
        super().__init__()
        self.next = successor
        self.tag = tag

    def __repr__(self):
        return 'p' + str(self.tag)

    def turn(self):
        return self.next


# Static Methods

def simple_players_from_integer(number_of_players):
    players = [SimplePlayer(None, number_of_players)]
    for n in range(number_of_players-1):
        players.append(SimplePlayer(players[n], number_of_players-1-n))
    players[0].next = players[-1]
    players.reverse()
    return players
