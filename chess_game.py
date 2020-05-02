from abc import ABC, abstractmethod
from piece_game import PieceGameState
from game_prep import Win, Lose, Draw, PlayOn, Pass, PlayerStatusChange


class ChessGameState(PieceGameState, ABC):
    """
    A ChessGame is a game where players cannot move so that their king is attacked. When a player's king is attacked,
    that player is in check. A player is in checkmate if the player is in check and cannot move. Players in checkmate
    loose the game and receive a score of 0. the remaining 1 point is divided evenly among players that have not lost
    by the end of the game.
    """
    def __init__(self, players, player_to_move, history=None, stalemate_consequence=Draw(), multiple_winners=False):
        super().__init__(players=players, player_to_move=player_to_move, history=history)
        self.multiple_winners = multiple_winners
        self.stalemate_consequence = stalemate_consequence
        self.kings = []

    def crown_kings(self, kings):
        for king in kings:
            self.kings.append(king)

    def in_check(self, player):
        in_check = False
        if self.kings:
            for king in self.kings:
                if king.player == player and king.attacked:
                    in_check = True
        return in_check

    def player_legal_moves(self, player):
        legal = []
        for move in self.piece_legal_moves(player):
            self.make_move(move)
            if not self.in_check(player):
                legal.append(move)
            self.revert()
        return legal

    def evaluate_player_status(self, player):
        other_players = filter(lambda x: x != self.player_to_move, self.players)
        if any(map(lambda x: x.status == PlayOn(), other_players)):
            return PlayerStatusChange(player, player.status)
        elif (not self.multiple_winners) and any(map(lambda x: x.status == Win(), other_players)):
            return PlayerStatusChange(player, Lose())
        elif all(map(lambda x: x.status == Lose(), other_players)):
            return PlayerStatusChange(player, Win())
        else:
            return PlayerStatusChange(player, Draw())

    def legal_moves(self):
        if all(map((lambda x: x.status != PlayOn(), self.players()))):
            return []
        elif self.player_to_move.status == PlayOn():
            if self.player_legal_moves(self.player_to_move):
                return self.player_legal_moves(self.player_to_move)

            elif self.in_check(self.player_to_move):
                self.player_to_move.status = Lose()
                return [[Pass()]]

            else:
                self.player_to_move.status = self.stalemate_consequence
                return [[Pass()]]
        else:
            return [[Pass()]]

    def utility(self):
        print(str(len(self.history)) + ' - ' + str(self.player_to_move))
        total_utility = sum(map(len, map(self.player_legal_moves, self.players)))
        score = {}
        for player in self.players:
            player_utility = len(self.player_legal_moves(player))
            print(str(player) + ' - ' + str(player_utility) + ' - ' + str(player.status))
            if player.status == PlayOn():
                score[player] = player.status.value(total_utility) * player_utility
            else:
                score[player] = player.status.value(len(self.players))
        return score

