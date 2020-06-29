from equality_modifiers import EqualityByArgs


class Location(EqualityByArgs):
    def __init__(self, *coords):
        super().__init__(*coords)


# -- Player -----------------------------------------

class PlayerStatus(Location):
    def __init__(self, name, score, active):
        super().__init__(name, score, active)
        self.name = name
        self.score = score
        self.active = active

    def utility_value(self, player_utility=1, total_utility=1):
        if self.score is not None:
            return self.score
        else:
            return player_utility / total_utility

    def __repr__(self):
        return str(self.name)


win = PlayerStatus('w', 1, False)
lose = PlayerStatus('l', 0, False)
draw = PlayerStatus('d', None, False)
play_on = PlayerStatus('a', None, True)
