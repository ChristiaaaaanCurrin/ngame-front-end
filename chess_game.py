from abc import ABC, abstractmethod
from piece_game import PieceGameState


class ChessGameState(PieceGameState, ABC):
    """
    A ChessGame is a game where players cannot move so that their king is attacked. When a player's king is attacked,
    that player is in check. A player is in checkmate if the player is in check and cannot move. Players in checkmate
    loose the game and receive a score of 0. the remaining 1 point is divided evenly among players that have not lost
    by the end of the game.
    """
    def __init__(self, players, player_to_move, history=None):
        super().__init__(players=players, player_to_move=player_to_move, history=history)

        self.kings = []
        self.winning_players = players

    def crown_kings(self, kings):
        for king in kings:
            self.kings.append(king)

    def in_check(self, player):
        in_check = False
        if self.kings:
            for king in self.kings:
                if king.player == player and king.attackers:
                    in_check = True
        return in_check

    def legal_moves(self):
        legal = []
        for piece in self.pieces(self.player_to_move):
            for move in piece.legal_moves():
                self.make_move(move)
                if not self.in_check(piece.player):
                    legal.append(move)
                self.revert()
        return legal

    def score(self):
        score = {}
        for player in self.players:
            if player in self.winning_players:
                score[player] = 0
            else:
                score[player] = 1 / len(self.winning_players)