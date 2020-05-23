from abc import ABC, abstractmethod
from move import Move, CombinationMove, Pass, GameStatePlayerChange, PlayerStatusChange
from game import Game, GameState


class PieceGameState(GameState, ABC):
    def __init__(self, players, player_to_move=None, pieces=None, history=None):
        super().__init__(players=players, player_to_move=player_to_move)
        if pieces:
            self.all_pieces = pieces
        else:
            self.all_pieces = []

        self.piece_types = []
        for piece in self.all_pieces:
            if type(piece) not in map(type, self.piece_types):
                self.piece_types.append(piece)

        if history:
            self.history = history
        else:
            self.history = []

    def __repr__(self):
        string = ''
        for player in self.players():
            string = string + str(player) + ' ' + str(player.status) + ', '
        string = string + '\n' + str(self.player_to_move) + ' to move,'
        for piece in self.pieces():
            string = string + '\n' + str(piece)
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

    def add_pieces(self, *pieces):
        for piece in pieces:
            self.all_pieces.append(piece)
            if type(piece) not in map(type, self.piece_types):
                self.piece_types.append(piece)

    def remove_pieces(self, *pieces):
        for piece in pieces:
            if piece in self.pieces():
                self.all_pieces.remove(piece)


class PieceGame(Game, ABC):
    """
    In a PieceGame, the moves are controlled by the pieces. The pieces are the only changing element during the game
    (beside player_to_move) and they dictate what legal moves are available and the affect of making a move. Pieces
    have, at minimum, a player that the piece belongs to, a location that helps track the consequences of moves, and
    a method returning a list of legal moves that describes how the pieces are able to influence a game_state.
    """
    def __init__(self, force_move=True):
        self.force_move = force_move

    def piece_legal_moves(self, game_state, player):
        legal = []
        for piece in game_state.pieces(player):
            for move in piece.legal_moves(game_state):
                legal.append(move)
        return legal

    def make_move(self, game_state, move):
        move.execute_move(game_state)
        for player in game_state.players():
            self.evaluate_player_status(game_state, player).execute_move(game_state)
        game_state.history.append(move)

    def revert(self, game_state):
        if game_state.history:
            revert_move = game_state.history.pop(-1).anti_move()
            revert_move.execute_move(game_state)
            return True
        else:
            return False

