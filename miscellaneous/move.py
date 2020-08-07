from abc import ABC, abstractmethod
from miscellaneous.equality_modifiers import EqualityByType

# keep me


class Move(ABC):
    """
    A move contains enough information to modify the GameState and undo itself
    """

    @abstractmethod
    def get_reverse_move(self):
        """
        :return: a Move carries instructions to undo self
        """
        pass

    @abstractmethod
    def execute_move(self, game_state):
        pass


class CombinationMove(Move):
    def __init__(self, *component_moves):
        self.component_moves = component_moves

    def __eq__(self, other):
        return self.component_moves == other.components

    def __repr__(self):
        return 'CombinationMove' + str(self.component_moves)

    def add_move(self, *moves):
        self.component_moves = self.component_moves + moves

    def remove_move(self, remove_component):
        new_components = []
        for component in self.component_moves:
            if component != remove_component:
                new_components.append(component)
        self.component_moves = new_components

    def get_reverse_move(self):
        anti_components = []
        for component in self.component_moves:
            anti_components.append(component.get_reverse_move())
        return CombinationMove(*anti_components)

    def execute_move(self, game_state):
        for component in self.component_moves:
            component.execute_move(game_state)

# TODO RecordMove as argument in execute_move for all moves.
class RecordMove(CombinationMove):
    def __repr__(self):
        return 'RecordMove' + str(self.component_moves)

    def execute_move(self, game_state):
        super().execute_move(game_state)
        game_state.history.append(self)


class Pass(Move, EqualityByType):
    """
    A Pass is a Move that does nothing. All passes are the same (equality by type).
    """
    def __repr__(self):
        return 'Pass'

    def get_reverse_move(self):
        """
        To undo nothing, do nothing again
        """
        return self

    def execute_move(self, game_state):
        pass


class PlayerStatusChange(Move):
    """
    A players status changes the status of a player
    """
    def __init__(self, player, new_status):
        """
        :param player: player whose status is to be changed
        :param new_status: new status of player
        """
        self.player = player
        self.new_status = new_status
        self.old_status = self.player.status

    def __repr__(self):
        return str(self.player) + ' -> ' + str(self.new_status)

    def get_reverse_move(self):
        return PlayerStatusChange(self.player, self.old_status)

    def execute_move(self, game_state):
        self.player.status = self.new_status


class TokenOwnerChange(Move):
    def __init__(self, token, new_owner):
        self.token = token
        self.old_owner = self.token.owner
        self.new_owner = new_owner

    def __repr__(self):
        return str(self.token) + ' -> ' + str(self.new_owner)

    def execute_move(self, game_state):
        self.token.owner = self.new_owner
        self.token.player = self.new_owner.player

    def get_reverse_move(self):
        return TokenOwnerChange(self.token, self.old_owner)

# TODO split to avoid side effects.
class PieceMoveAddRemove(Move):
    def __init__(self, piece, location=None):
        self.piece = piece
        self.new_location = location
        self.old_location = self.piece.location

    def __repr__(self):
        return str(self.piece) + ' -> ' + str(self.new_location)

    def execute_move(self, game_state):
        self.piece.location = self.new_location
        if self.piece in game_state.pieces():
            if self.new_location:
                pass
            else:
                game_state.remove_pieces(self.piece)
        elif self.new_location:
            game_state.add_pieces(self.piece)

    def get_reverse_move(self):
        return PieceMoveAddRemove(self.piece, self.old_location)