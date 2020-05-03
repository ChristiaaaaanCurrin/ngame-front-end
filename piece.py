from abc import ABC, abstractmethod
from equality_modifiers import EqualityByArgs
from move import Move


class Location(ABC, EqualityByArgs):
    """
    Location includes useful overrides for __eq__ and __repr__ that make locations easier to deal with
    """
    def __init__(self, *coords):
        super().__init__(*coords)
        self.coords = coords

    def __eq__(self, other):
        return self.coords == other.coords

    def __repr__(self):
        return str(self.coords)


class PieceMoveAddRemove(Move):
    """
    A PieceMoveAddRemove carries the information required to change a piece based on a move.
    PieceMoveAddRemove is the output of Piece.legal_moves and the input of PieceGameState.execute_move.
    A list of PieceMoveAddRemove's is the input to PieceGameState.make_move.
    """
    def __init__(self, piece, new_location=None):
        """
        :param piece: piece to be altered
        :param new_location: location to which the piece will be moved
        """
        self.piece = piece
        self.new_location = new_location
        self.remove = not new_location  # pieces moved to new_location = None are "removed" or "captured"

    def __repr__(self):
        return str(self.piece) + ' -> ' + str(self.new_location)

    def anti_move(self):
        return PieceMoveAddRemove(self.piece, self.piece.location)

    def execute_move(self, game_state):
        self.piece.location = self.new_location
        if self.piece in game_state.pieces():
            if self.new_location:
                self.piece.location = self.new_location
            else:
                game_state.all_pieces.remove(self.piece)
        elif self.new_location:
            game_state.all_pieces.append(self.piece)


class Piece(ABC, EqualityByArgs):
    """
    Piece contains the minimum requirements for a piece: game_state, player, location, legal_moves().
    """
    def __init__(self, player=None, location=None):
        """
        :param player: must be a Player in game_state.players
        :param location: identifies current piece properties in game_state
        """
        super().__init__(player, location)
        self.player = player
        self.location = location

    @abstractmethod
    def legal_moves(self):
        """
        :return: what actions ("moves") the piece can legally make. must be of type PieceMoveAddRemove
        """
        pass

    @abstractmethod
    def attackers_of_same_type(self, piece):
        """
        this method should be overridden if attacked is to be used
        :param piece: the piece that is attacked by pieces
        :return: list of pieces in game_state where type(piece) == type(self) and piece "attacks" self
        """
        pass

    def attacked(self, game_state):
        """
        :return: True if any piece in game_state "attacks" self according to attackers of same type
        """
        attacked = False
        for piece_type in game_state.piece_types:
            if piece_type.attackers_of_same_type(self):
                attacked = True
                break
        return attacked


class SimpleMovePiece(Piece, ABC):
    """
    A SimpleMovePiece is a Piece whose legal moves only involve going from one location to another and capturing
    (removing) other pieces. A SimpleMovePiece must have a method returning the locations accessible to self and
    a method returning a list of pieces that would be captured if self moved to a given location
    """
    @abstractmethod
    def accessible_locations(self):
        """
        :return: list of locations that self can move to
        """
        pass

    @abstractmethod
    def captured_pieces(self, location):
        """
        :param location: potential location to which self might move
        :return: list of pieces captured if self moves to location
        """
        pass

    def legal_moves(self):
        """
        :return: list of legal moves for self given accessible locations
        """
        legal = []
        for location in self.accessible_locations():
            move = [PieceMoveAddRemove(self, location)]  # A move will always change the pieces location
            for captured_piece in self.captured_pieces(location):
                move.append(PieceMoveAddRemove(captured_piece))  # self captures pieces by moving them to location None
            legal.append(move)
        return legal


class SimpleCapturePiece(SimpleMovePiece, ABC):
    """
    A SimpleCapturePiece captures by moving to the same location as the target piece.
    """
    def captured_pieces(self, location):
        return filter(lambda x: x.location == location, self.game_state.pieces())


# INCOMPLETE
class PatternMovePiece(SimpleMovePiece, ABC):
    @abstractmethod
    def accessible_locations_step(self):
        """
        :return: list of functions giving closest legal moves (one step in the pattern for pattern move)
        """
        pass

    @abstractmethod
    def skip_location(self, location):
        pass

    @abstractmethod
    def stop_on_location(self, location):
        pass

    def accessible_locations(self):
        accessible_locations = []
        for neighbor_finder in self.accessible_locations_step():
            edge = neighbor_finder(self)
            while edge:
                new_edge = []
                for location in edge:
                    if location not in accessible_locations:
                        accessible_locations.append(location)
                        for piece in location.pieces_to_add:
                            for next_move in neighbor_finder(piece):
                                new_edge.append(next_move)
                edge = new_edge
        return accessible_locations
