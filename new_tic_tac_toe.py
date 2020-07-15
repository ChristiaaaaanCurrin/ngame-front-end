from new_piece import Player, SimpleTurn, instantiate_pieces_from_integer
from piece import play_on, win, lose, draw
from new_game_state import GameState, max_n
from equality_modifiers import selective_inheritance


class TicTacToeGameState(GameState):
    def __init__(self, rows=3, columns=3, win_condition=3):

        self.rows = rows
        self.columns = columns
        self.win_condition = win_condition
        super().__init__()

    def __repr__(self):
        return str(self.top_piece) + ' ' + str([(player, player.occupied_coords) for player in self.players()])


class TicTacToePlayer(Player):
    def __init__(self, name='X', game_state=TicTacToeGameState(), successor=None, status=play_on, *occupied_coords):
        super().__init__(name=name, game_state=game_state, successor=successor, status=status)
        self.occupied_coords = []
        for coord in occupied_coords:
            self.occupied_coords.append(coord)

    def test_win(self, coord):
        test_win = False
        w = self.game_state.win_condition
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

    def utility(self):
        return {self: self.status.utility_value(total_utility=len(self.game_state.players()))}

    def legal_moves(self):
        legal = []
        if self.status == play_on and self.game_state:
            for row in range(self.game_state.rows):
                for column in range(self.game_state.columns):
                    coord = (row, column)

                    for player in self.game_state.players():
                        if coord in player.occupied_coords:
                            break
                    else:
                        if self.test_win(coord):
                            sub_moves = [(player, (lose, player.status)) for player in self.game_state.players()]
                            sub_moves.append((self, (win, self.status)))
                            legal.append((coord, *sub_moves))
                        else:
                            legal.append((coord,))

            if not legal:
                legal.append((None, *[(self, (draw, self.status))]))

        return legal

    def execute_move(self, move):
        coord, *sub_moves = move

        if coord:
            self.occupied_coords.append(coord)
        if sub_moves:
            for player, (status, old_status) in sub_moves:
                player.status = status

    def undo_move(self, move):
        coord, *sub_moves = move

        if coord:
            self.occupied_coords.remove(coord)
        if sub_moves:
            for player, (status, old_status) in sub_moves:
                player.status = old_status


test_players = instantiate_pieces_from_integer(TicTacToePlayer, 2, game_state=TicTacToeGameState())
test_game = SimpleTurn('ttc', test_players[0], game_state=test_players[0].game_state)
[print(player.status) for player in test_players]
[print(player.legal_moves()) for player in test_players]
print(test_game.legal_moves())

for m in range(0):
    if test_game.legal_moves():
        test_game.execute_move(test_game.legal_moves()[0])
    print(test_game)


print(test_game.utility())
print(max_n(test_game, 9))

print('--------------------\n--------------------')

