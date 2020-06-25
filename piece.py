from abc import ABC, abstractmethod
from move import CombinationMove, TokenOwnerChange, RecordMove, PieceMoveAddRemove
from equality_modifiers import EqualityByArgs, Const


# ---------- Piece ---------------------------

class Piece(ABC):
    def __init__(self, player, successor=None):
        self.player = player
        self.successor = successor

    @abstractmethod
    def legal_moves(self, game_state):
        pass


# ---------- Token ---------------------------

class Token(Piece, ABC):
    def __init__(self, owner, successor=None):
        super().__init__(player=owner.player, successor=successor)
        self.owner = owner


class SimpleTurnToken(Token):
    def legal_moves(self, game_state):
        legal = []
        for move in self.owner.legal_moves(game_state):
            legal.append(CombinationMove(move, TokenOwnerChange(self, self.owner.successor)))
        return legal


class TopTurnToken(SimpleTurnToken):
    def __repr__(self):
        return 'turn'

    def legal_moves(self, game_state):
        legal = []
        for move in self.owner.legal_moves(game_state):
            legal.append(RecordMove(move, TokenOwnerChange(self, self.owner.successor)))
        return legal


# ---------- Player --------------------------
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


# Player Class

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


# ---------- Subordinate Piece ---------------

class SubordinatePiece(Piece, ABC):
    """
    Piece contains the minimum requirements for a piece: game_state, player, location, legal_moves().
    """

    def __init__(self, player=None, location=None, successor=None):
        """
        :param player: must be a Player in game_state.players
        :param location: identifies current piece properties in game_state
        :param successor: any piece that meaningfully comes after this one
        """
        super().__init__(player=player, successor=successor)
        self.location = location

    @abstractmethod
    def attacks_piece(self, game_state, piece):
        """
        this method should be overridden if attacked is to be used
        :param game_state: game state of self
        :param piece: the piece that is attacked by self
        :return: true if self attacks pieces, else false
        """
        pass

    def attacked(self, game_state):
        """
        :return: True if any piece in game_state "attacks" self according to attackers of same type
        """
        attacked = False
        for piece_type in game_state.piece_types:
            if piece_type.attacks_piece(game_state, self):
                attacked = True
                break
        return attacked


class SimpleMovePiece(SubordinatePiece, ABC):
    """
    A SimpleMovePiece is a Piece whose legal moves only involve going from one location to another and capturing
    (removing) other pieces. A SimpleMovePiece must have a method returning the locations accessible to self and
    a method returning a list of pieces that would be captured if self moved to a given location
    """

    @abstractmethod
    def accessible_locations(self, game_state):
        """
        :return: list of locations that self can move to
        """
        pass

    @abstractmethod
    def capturable_pieces(self, game_state, location):
        """
        :param game_state: the game_state of the piece
        :param location: potential location to which self might move
        :return: list of pieces captured if self moves to location
        """
        pass

    def legal_moves(self, game_state):
        """
        :return: list of legal moves for self given accessible locations
        """
        legal = []
        for location in self.accessible_locations(game_state):
            move = CombinationMove(PieceMoveAddRemove(self, location))  # A move will always change the pieces location
            for captured_piece in self.capturable_pieces(game_state, location):
                move.add_move(PieceMoveAddRemove(captured_piece))  # captures pieces by moving them to location None
            legal.append(move)
        return legal


class SimpleCapturePiece(SimpleMovePiece, ABC):
    """
    A SimpleCapturePiece captures by moving to the same location as the target piece.
    """

    def capturable_pieces(self, game_state, location):
        return filter(lambda x: x.location == location, game_state.pieces())


# TODO Complete this class
class PatternMovePiece(SimpleMovePiece, ABC):
    @abstractmethod
    def directions(self):
        pass

    @abstractmethod
    def skip_location(self, location):
        pass

    @abstractmethod
    def stop_on_location(self, location):
        pass

    def neighbors(self, game_state, *directions):
        neighbors = []
        for direction in directions:
            neighbors.extend(direction(game_state, self))
        return neighbors

    def accessible_locations(self, game_state):
        neighbors = []
        for direction in self.directions():
            edge = self.neighbors(game_state, direction)
            while edge:
                new_edge = []
                for tile in edge:
                    if self.stop_on_location(tile):
                        break
                    elif self.skip_location(tile):
                        new_edge.extend(tile.neighbors(game_state, direction))
                    else:
                        neighbors.append(tile)
                        new_edge.extend(tile.neighbors(game_state, direction))
                edge = new_edge
        return neighbors


# Piece Factory Method

def instantiate_pieces_from_integer(piece_class, number_of_pieces):
    pieces = [piece_class(None, number_of_pieces)]
    for n in range(number_of_pieces - 1):
        pieces.append(piece_class(pieces[n], number_of_pieces - 1 - n))
    pieces[0].successor = pieces[-1]
    pieces.reverse()
    return pieces
