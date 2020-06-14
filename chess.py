from piece import instantiate_pieces_from_integer, TopTurnToken, Player, play_on, win, lose, draw
from move import Move, PlayerStatusChange, CombinationMove
from game_state import GameState


class ChessGameState(GameState):
    def __init__(self, top_token, players, tokens=None, pieces=None, kings=None, history=None):
        super().__init__(top_token=top_token, players=players, tokens=tokens, pieces=pieces, history=history)
        if kings:
            self.all_kings = kings
        else:
            self.all_kings = []

    def kings(self, player):
        kings = []
        for king in self.all_kings:
            if player == king.player:
                kings.append(king)
        return kings


class ChessPlayer(Player):
    def in_check(self, game_state):
        in_check = False
        for king in game_state.kings(self):
            if king.attacked(game_state):
                in_check = True
                break
        return in_check

    def utility(self, game_state):
        pass

    def legal_moves(self, game_state):
        legal = []
        for piece in game_state.pieces(self):
            for move in piece.legal_moves(game_state):
                move.execute_move(game_state)
                if self.in_check(game_state):
                    pass
                else:
                    legal.append(move)
        return legal
