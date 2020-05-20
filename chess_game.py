from abc import ABC, abstractmethod
from piece_game import PieceGameState, PieceGame
from player import Win, Lose, Draw, PlayOn
from move import PlayerStatusChange, Pass, CombinationMove, GameStatePlayerChange


class ChessGameState(PieceGameState, ABC):
    """
    A ChessGameState must have a list of pieces, a list of kings, and a running history.
    """
    def __init__(self, players, player_to_move=None, pieces=None, kings=None, history=None):
        super().__init__(players=players, player_to_move=player_to_move, pieces=pieces, history=history)
        if kings:
            self.kings = kings
        else:
            self.kings = []

    def crown_kings(self, *kings):
        for king in kings:
            self.kings.append(king)


class ChessGame(PieceGame, ABC):
    """
    A ChessGame is a game where players cannot move so that their king is attacked. When a player's king is attacked,
    that player is in check. A player is in checkmate if the player is in check and cannot move. Players in checkmate
    loose the game and receive a score of 0. the remaining 1 point is divided evenly among players that have not lost
    by the end of the game.
    """
    def __init__(self, stalemate_consequence=Draw(), multiple_winners=False):
        self.multiple_winners = multiple_winners
        self.stalemate_consequence = stalemate_consequence

    def in_check(self, game_state, player):
        in_check = False
        if game_state.kings:
            for king in game_state.kings:
                if king.player == player and king.attacked(game_state):
                    in_check = True
        return in_check

    def player_legal_moves(self, game_state, player):
        legal = []
        for move in self.piece_legal_moves(game_state, player):
            self.make_move(game_state=game_state, move=move)
            if not self.in_check(game_state=game_state, player=player):
                legal.append(move)
            self.revert(game_state)
        return legal

    def evaluate_player_status(self, game_state, player):

        if player.status == PlayOn():
            if game_state.players(PlayOn(), not_player=player):
                return Pass()

            elif (not self.multiple_winners) and game_state.players(Win(), not_player=player):
                return PlayerStatusChange(player, Lose())

            elif not game_state.players(Win(), Draw(), PlayOn(), not_player=player):
                return PlayerStatusChange(player, Win())

            else:
                return PlayerStatusChange(player, Draw())
        else:
            return Pass()

    def legal_moves(self, game_state):
        index_player = GameStatePlayerChange(game_state, game_state.player_to_move.turn())
        update_players = tuple([self.evaluate_player_status(game_state, player) for player in game_state.players()])
        moves = self.player_legal_moves(game_state, game_state.player_to_move)

        if not game_state.players(PlayOn()):
            return []
        elif game_state.player_to_move.status == PlayOn():
            if self.player_legal_moves(game_state, game_state.player_to_move):
                return [CombinationMove(index_player, *update_players, move) for move in moves]

            elif self.in_check(game_state, game_state.player_to_move):
                game_state.player_to_move.status = Lose()
                return [CombinationMove(index_player, *update_players)]

            else:
                game_state.player_to_move.status = self.stalemate_consequence
                return [CombinationMove(index_player, *update_players)]
        else:
            return [CombinationMove(index_player, *update_players)]

    def utility(self, game_state):
        total_utility = sum(map(len, map(lambda x: self.player_legal_moves(game_state, x), game_state.players())))
        score = {}
        for player in game_state.players():
            if player.status == PlayOn():
                player_utility = len(self.player_legal_moves(game_state=game_state, player=player))
                score[player] = player.status.value(total_utility) * player_utility
            else:
                score[player] = player.status.value(len(game_state.players()))
        return score

