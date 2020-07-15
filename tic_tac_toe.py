from piece import instantiate_pieces_from_integer, TopTurnToken, Player, play_on, win, lose, draw, Piece
from move import Move, PlayerStatusChange, CombinationMove
from game_state import GameState, max_n


class TicTacToeMove(Move):
    def __init__(self, player, coords):
        self.player = player
        self.coords = coords

    def __repr__(self):
        return str(self.player) + str(self.coords)

    def execute_move(self, game_state):
        if self.coords in self.player.occupied_coords:
            self.player.occupied_coords.remove(self.coords)
        else:
            self.player.occupied_coords.append(self.coords)

    def get_reverse_move(self):
        return self


class TicTacToePlayer(Player):
    def __init__(self, successor, tag, *occupied_coords):
        super().__init__(successor, tag)
        self.occupied_coords = []
        for coord in occupied_coords:
            self.occupied_coords.append(coord)

    def test_win(self, game_state, coord):
        test_win = False
        w = game_state.win_condition
        occupied_coords = self.occupied_coords + [coord]

        if len(occupied_coords) >= w:
            for coord in occupied_coords[0:-w]:
                if all(map(lambda x: x in occupied_coords, [tuple(map(sum, zip(coord, (m, 0)))) for m in range(w)])):
                    test_win = True

                if all(map(lambda x: x in occupied_coords, [tuple(map(sum, zip(coord, (0, m)))) for m in range(w)])):
                    test_win = True

                if all(map(lambda x: x in occupied_coords, [tuple(map(sum, zip(coord, (m, m)))) for m in range(w)])):
                    test_win = True
        return test_win

    def utility(self, game_state):
        return self.status.utility_value(total_utility=len(game_state.players()))

    def legal_moves(self, game_state):
        legal = []
        if self.status == play_on:
            for row in range(game_state.rows):
                for column in range(game_state.columns):
                    coord = (row, column)
                    for player in game_state.players():
                        if coord in player.occupied_coords:
                            break
                    else:
                        if self.test_win(game_state, coord):
                            move = CombinationMove(TicTacToeMove(self, coord))
                            for player in game_state.players():
                                move.add_move(PlayerStatusChange(player, lose))
                            move.add_move(PlayerStatusChange(self, win))
                            legal.append(move)
                        else:
                            legal.append(TicTacToeMove(self, coord))
            if not legal:
                return [PlayerStatusChange(self, draw)]
        return legal


class TicTacToeGameState(GameState):
    def __init__(self, top_token=None, players=instantiate_pieces_from_integer(TicTacToePlayer, 2),
                 rows=3, columns=3, win_condition=3, tokens=None, pieces=None, history=None):
        super().__init__(top_token, players, tokens, pieces, history)
        if top_token:
            self.top_token = top_token
        else:
            self.top_token = TopTurnToken(players[0])
        self.rows = rows
        self.columns = columns
        self.win_condition = win_condition

    def __repr__(self):
        return str(self.top_token.player) + str([(player, player.occupied_coords) for player in self.players()])


test_game = TicTacToeGameState()
test_players = instantiate_pieces_from_integer(TicTacToePlayer, 2)
print(test_game)
"""
for m in range(2):
    if test_game.legal_moves():
        test_game.legal_moves()[0].execute_move(test_game)
    print(test_game)
"""
print(max_n(game_state=test_game, max_depth=9))
print(test_game)
