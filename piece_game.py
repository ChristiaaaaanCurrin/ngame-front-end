from abc import ABC, abstractmethod
from game_prep import GameState


class PieceGameState(GameState, ABC):
    def __init__(self, players, player_to_move, history):
        super().__init__(players, player_to_move)

        self.all_pieces = []

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
            self.all_pieces.append(piece)

    def pieces(self, player=None):
        pieces = []
        if player:
            for piece in self.all_pieces:
                if piece.player == player:
                    pieces.append(piece)
        else:
            pieces = self.all_pieces
        return pieces

    def legal_moves(self):
        legal = []
        for piece in self.pieces(self.player_to_move):
            for move in piece.legal_moves(self):
                legal.append(move)
        return legal

    def execute_move(self, piece_move):
        piece_move.piece.location = piece_move.new_location
        if piece_move.piece in self.pieces():
            if piece_move.new_location:
                piece_move.piece.location = piece_move.new_location
            else:
                self.all_pieces.remove(piece_move.piece)
        elif piece_move.new_location:
            self.all_pieces.append(piece_move.piece)

    def make_move(self, move):
        revert_move = []
        for piece_move in move:
            revert_move.append(piece_move.anti_move())
            self.execute_move(piece_move)
        self.history.append((self.player_to_move, revert_move))
        self.player_to_move = self.player_to_move.turn()

    def revert(self):
        if self.history:
            (previous_player, revert_move) = self.history.pop(-1)
            for piece_move in revert_move:
                self.execute_move(piece_move)
                self.player_to_move = previous_player
            return True
        else:
            return False


class PieceMoveAddRemove:
    def __init__(self, piece, new_location=None):
        self.piece = piece
        self.new_location = new_location
        self.remove = not new_location

    def __repr__(self):
        return str(self.piece) + ' -> ' + str(self.new_location)

    def anti_move(self):
        return PieceMoveAddRemove(self.piece, self.piece.location)


class Piece(ABC):
    def __init__(self, game_state, player, location):
        self.player = player
        self.location = location
        self.game_state = game_state

    @abstractmethod
    def legal_moves(self):
        """
        :return: what actions ("moves") the piece can legally make
        """
        pass


class SimpleMovePiece(Piece, ABC):
    @abstractmethod
    def accessible_locations(self):
        pass

    @abstractmethod
    def captured_pieces(self, location):
        pass

    def legal_moves(self):
        legal = []
        for location in self.accessible_locations():
            move = [PieceMoveAddRemove(self, location)]
            for piece in self.captured_pieces(location):
                move.append(PieceMoveAddRemove(piece))
            legal.append(move)
        return legal


class SimpleCapturePiece(SimpleMovePiece, ABC):
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
