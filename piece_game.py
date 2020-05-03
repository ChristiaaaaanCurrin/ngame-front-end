from abc import ABC, abstractmethod
from equality_modifiers import EqualityByArgs
from move import Move, CombinationMove, Pass, GameStatePlayerChange, PlayerStatusChange
from game import Game, GameState


class PieceGameState(GameState, ABC):
    def __init__(self, players, player_to_move, pieces):
        super().__init__(players=players, player_to_move=player_to_move)
        self.all_pieces = pieces

    def __repr__(self):
        string = str(self.player_to_move) + ' to move\n'
        for piece in self.pieces():
            string = string + str(piece) + '\n'
        return string

    def pieces(self, player=None):
        pieces = []
        if player:
            for piece in self.all_pieces:
                if piece.player == player:
                    pieces.append(piece)
        else:
            pieces = self.all_pieces
        return pieces


class PieceGame(Game, ABC):
    """
    In a PieceGame, the moves are controlled by the pieces. The pieces are the only changing element during
    the game (beside player_to_move) and they dictate what legal moves are available and the affect of making a move.
    Pieces have, at minimum, a player that the piece belongs to,
    a location that helps track the consequences of moves, and a method returning a list of legal moves
    that describes how the pieces are able to influence a game_state.
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

    def set_board(self, pieces):
        for piece in pieces:
            piece.game_state = self
            self.all_pieces.append(piece)
            if type(piece) not in map(type, self.piece_types):
                self.piece_types.append(piece)

    def piece_legal_moves(self, game_state, player):
        legal = []
        for piece in game_state.pieces(player):
            for move in piece.legal_moves():
                legal.append(move)
        return legal

    def legal_moves(self, game_state):
        piece_moves = self.piece_legal_moves(game_state, game_state.player_to_move)
        player_change = GameStatePlayerChange(game_state, game_state.player_to_move.turn())
        player_status_changes = [PlayerStatusChange(game_state, player) for player in game_state.players]
        legal = CombinationMove(player_change, *piece_moves, *player_status_changes)
        return legal

    @abstractmethod
    def evaluate_player_status(self, player):
        """
        find what player status "should be"
        :param player: player whose status is to be changed
        :return: PlayerStatusChange
        """
        pass

    def make_move(self, move, game_state):
        revert_move = move.anti_move()
        move.execute_move(game_state)
        game_state.history.append(revert_move)

    def revert(self, game_state):
        if self.history:
            revert_move = self.history.pop(-1)
            revert_move.execute_move(game_state)
            return True
        else:
            return False

'''
class DefaultPieceGameState(PieceGameState):
    """
    DefaultPieceGameState is a dummy PieceGameState that allows pieces to be instantiated without a game
    """
    def __init__(self):
        super().__init__(players=None)

    def evaluate_player_status(self, player):
        return Pass()

    def utility(self, game_state):
        return {}


    def randomize_position(self):
        pass

'''