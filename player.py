from abc import ABC, abstractmethod
from equality_modifiers import EqualityByType


# Basic Player Status Classes

class PlayerStatus(EqualityByType, ABC):
    @abstractmethod
    def value(self, total):
        pass


class Win(PlayerStatus):
    def value(self, total):
        return 1

    def __repr__(self):
        return 'Win'


class Lose(PlayerStatus):
    def value(self, total):
        return 0

    def __repr__(self):
        return 'Lose'


class Draw(PlayerStatus):
    def value(self, total):
        return 1 / total

    def __repr__(self):
        return 'Draw'


class PlayOn(PlayerStatus):
    def value(self, total):
        return 1 / total

    def __repr__(self):
        return 'PlayOn'


# Basic Player Classes

class Player(ABC):
    def __init__(self):
        self.status = PlayOn()

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
    players = [SimplePlayer(None, number_of_players+1)]
    for n in range(number_of_players):
        players.append(SimplePlayer(players[n], number_of_players-n))
    players[0].next = players[-1]
    players.reverse()
    return players