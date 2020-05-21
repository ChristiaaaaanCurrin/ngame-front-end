from abc import ABC, abstractmethod
from equality_modifiers import EqualityByArgs


# Basic Player Status Classes

class PlayerStatus(EqualityByArgs):
    def __init__(self, tag, score, active):
        super().__init__(tag, score, active)
        self.tag = tag
        self.score = score
        self.active = active

    def utility_value(self, player_utility=1, total_utility=1):
        if self.score:
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

class Player(ABC):
    def __init__(self):
        self.status = play_on

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
