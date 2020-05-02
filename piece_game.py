from abc import ABC, abstractmethod
from game_prep import GameState, Move, Pass, EqualityByArgs


class PieceGameState(GameState, ABC):
    """
    In a PieceGameState, the moves are controlled by the pieces. The pieces are the only changing element during
    the game (beside player_to_move) and they dictate what legal moves are available and the affect of making a move.
    Pieces have, at minimum, a game_state that the piece is part of, a player that the piece belongs to,
    a location that helps track the consequences of moves, and a method returning a list of legal moves
    that describes how the pieces are able to influence the game.
    """
    def __init__(self, players, player_to_move=None, pieces=None, history=None):
        super().__init__(players=players, player_to_move=player_to_move)

        self.all_pieces = []
        self.piece_types = []
        if pieces:
            self.set_board(pieces)

        if history:
            self.history = history
        else:
            self.history = []

    def __repr__(self):
        string = str(self.player_to_move) + ' to move\n'
        for piece in self.pieces():
            string = string + str(piece) + '\n'
        return string

    def set_board(self, pieces):
        for piece in pieces:
            piece.game_state = self
            self.all_pieces.append(piece)
            if type(piece) not in map(type, self.piece_types):
                self.piece_types.append(piece)

    def pieces(self, player=None):
        pieces = []
        if player:
            for piece in self.all_pieces:
                if piece.player == player:
                    pieces.append(piece)
        else:
            pieces = self.all_pieces
        return pieces

    def piece_legal_moves(self, player):
        legal = []
        for piece in self.pieces(player):
            for move in piece.legal_moves():
                legal.append(move)
        return legal

    def legal_moves(self):
        return self.piece_legal_moves(self.player_to_move)

    def index_turn(self, move):
        self.player_to_move = self.player_to_move.turn()

    @abstractmethod
    def evaluate_player_status(self, player):
        """
        find what player status "should be"
        :param player: player whose status is to be changed
        :return: PlayerStatusChange
        """
        pass

    def make_move(self, move):
        revert_move = []
        for piece_move in move:
            revert_move.append(piece_move.anti_move())
            piece_move.execute_move()
        revert_status = self.evaluate_player_status(self.player_to_move)
        self.history.append((self.player_to_move, revert_move, revert_status))
        self.index_turn(move)

    def revert(self):
        if self.history:
            (previous_player, revert_move, revert_status) = self.history.pop(-1)
            self.player_to_move = previous_player
            for piece_move in revert_move:
                piece_move.execute_move()
            revert_status.execute_move()
            return True
        else:
            return False


class DefaultPieceGameState(PieceGameState):
    """
    DefaultPieceGameState is a dummy PieceGameState that allows pieces to be instantiated without a game
    """
    def __init__(self):
        super().__init__(players=None)

    def evaluate_player_status(self, player):
        return Pass()

    def utility(self):
        return {}

    def neural_net_input(self):
        return []

    def randomize_position(self):
        pass


class Location(ABC, EqualityByArgs):
    """
    Location includes useful overrides for __eq__ and __repr__ that make locations easier to deal with
    """
    def __init__(self, *coords):
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

    def execute_move(self):
        self.piece.location = self.new_location
        if self.piece in self.piece.game_state.pieces():
            if self.new_location:
                self.piece.location = self.new_location
            else:
                self.piece.game_state.all_pieces.remove(self.piece)
        elif self.new_location:
            self.piece.game_state.all_pieces.append(self.piece)


class Piece(ABC, EqualityByArgs):
    """
    Piece contains the minimum requirements for a piece: game_state, player, location, legal_moves().
    """
    def __init__(self, game_state=None, player=None, location=None):
        """
        :param game_state: must be a PieceGameState
        :param player: must be a Player in game_state.players
        :param location: identifies current piece properties in game_state
        """
        if game_state:
            self.game_state = game_state
        else:
            self.game_state = DefaultPieceGameState()
        self.player = player
        self.location = location

    @abstractmethod
    def legal_moves(self):
        """
        :return: what actions ("moves") the piece can legally make. must be of type PieceMoveAddRemove
        """
        pass

    def attackers_of_same_type(self, piece):
        """
        this method should be overridden if attacked is to be used
        :param piece: the piece that is attacked by pieces
        :return: list of pieces in game_state where type(piece) == type(self) and piece "attacks" self
        """
        return []

    def attacked(self):
        """
        :return: True if any piece in game_state "attacks" self according to attackers of same type
        """
        attacked = False
        for piece_type in self.game_state.piece_types:
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
