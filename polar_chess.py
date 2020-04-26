from game_prep import GameState, simple_players_from_integer


class PolarChess(GameState):
    def __init__(self, players=simple_players_from_integer(2), player_to_move=None):
        if not player_to_move:
            player_to_move = players[0]
        super().__init__(players, player_to_move)


