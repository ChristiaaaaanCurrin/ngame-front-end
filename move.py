from abc import ABC, abstractmethod
from equality_modifiers import EqualityByType, EqualityByArgs


# Basic Move Classes

class Move(ABC):
    """
    A move contains enough information to modify the GameState and undo itself
    """

    @abstractmethod
    def anti_move(self):
        """
        :return: a Move that carries instructions to undo self
        """
        pass

    @abstractmethod
    def execute_move(self, game_state):
        pass


class CombinationMove(Move):
    def __init__(self, *components):
        self.components = components

    def __eq__(self, other):
        return self.components == other.components

    def add_move(self, move):
        return self.components + tuple([move])

    def anti_move(self):
        anti_components = []
        for component in self.components:
            anti_components.append(component.anti_move())
        return CombinationMove(*anti_components)

    def execute_move(self, game_state):
        for component in self.components:
            component.execute_move(game_state)


class Pass(Move, EqualityByType):
    """
    A Pass is a Move that does nothing. All passes are the same (equality by type).
    """
    def __repr__(self):
        return 'Pass'

    def anti_move(self):
        """
        To undo nothing, do nothing again
        """
        return self

    def execute_move(self, game_state):
        pass


class PlayerStatusChange(Move):
    """
    A players status changes the status of a player (does not need a gamestate to function)
    """
    def __init__(self, player, new_status):
        """
        :param player: player whose status is to be changed
        :param new_status: new status of player
        """
        self.player = player
        self.new_status = new_status

    def __repr__(self):
        return str(self.player) + ' -> ' + str(self.new_status)

    def anti_move(self):
        return PlayerStatusChange(self.player, self.player.status)

    def execute_move(self, game_state):
        self.player.status = self.new_status


class GameStatePlayerChange(Move, EqualityByArgs):
    def __init__(self, game_state, new_player_to_move):
        super().__init__()
        self.game_state = game_state
        self.new_player_to_move = new_player_to_move

    def anti_move(self):
        return GameStatePlayerChange(self.game_state, self.game_state.player_to_move)

    def execute_move(self, game_state):
        game_state.player_to_move = self.new_player_to_move

