from abc import ABC, abstractmethod
from piece_game import PieceGameState, PieceGame
from player import win, lose, draw, play_on
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
    def __init__(self, stalemate_consequence=draw, multiple_winners=False, force_move=True):
        super().__init__(force_move)
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

        if player.status == play_on:
            if game_state.players(play_on, not_player=player):
                return Pass()

            elif (not self.multiple_winners) and game_state.players(win, not_player=player):
                return PlayerStatusChange(player, lose)

            elif not game_state.players(draw, not_player=player):
                return PlayerStatusChange(player, win)

            else:
                return PlayerStatusChange(player, draw)
        else:
            return Pass()

    def legal_moves(self, game_state):
        index_player = GameStatePlayerChange(game_state.player_to_move, game_state.player_to_move.turn())
        #update_players = tuple([self.evaluate_player_status(game_state, player) for player in game_state.players()])
        moves = self.player_legal_moves(game_state, game_state.player_to_move)

        if not game_state.players(play_on):
            return []
        elif game_state.player_to_move.status == play_on:
            if self.player_legal_moves(game_state, game_state.player_to_move):
                return [CombinationMove(index_player, move) for move in moves]  # *update_players

            elif self.in_check(game_state, game_state.player_to_move):
                game_state.player_to_move.status = lose
                return [index_player]  # *update_players

            else:
                game_state.player_to_move.status = self.stalemate_consequence
                return [index_player]  # *update_players
        else:
            return [index_player]  # *update_players

    def utility(self, game_state):
        total_utility2 = sum(map(len, map(lambda x: self.player_legal_moves(game_state, x), game_state.players())))
        total_utility = 0
        for player in game_state.players():
            print(self.player_legal_moves(game_state, player))
            total_utility = total_utility + len(self.player_legal_moves(game_state, player))
        print(total_utility)
        score = {}
        for player in game_state.players():
            if player.status.active:
                player_utility = len(self.player_legal_moves(game_state=game_state, player=player))
                print(player_utility)
                score[player] = player.status.utility_value(player_utility=player_utility, total_utility=total_utility)
            else:
                score[player] = player.status.utility_value(total_utility=len(game_state.players()))
        return score

