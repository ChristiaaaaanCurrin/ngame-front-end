from game import GameState
from neural_net import VanillaNetwork
import random


class TicTacToe(GameState):
    def __init__(self, players=('x', 'o'), player_to_move=None, rows=3, columns=3, win_condition=3, pieces=None,
                 history=None):
        super().__init__(players, player_to_move)

        self.board = []
        self.rows = rows
        self.columns = columns
        for m in range(rows):
            for n in range(columns):
                self.board.append((m, n))

        self.win_condition = win_condition

        self.pieces = {}
        if pieces is None:
            for player in players:
                self.pieces[player] = []
        else:
            self.pieces = pieces

        if history is None:
            self.history = []
        else:
            self.history = history

    def __str__(self):
        return 'tic tac toe ' \
               + str(self.rows) \
               + 'X' + str(self.columns) \
               + ' ' + str(self.pieces) \
               + ', ' + str(self.player_to_move) + ' to move'

    def win(self, player):
        win = False
        w = self.win_condition
        pieces = self.pieces[player]

        if len(pieces) >= w:
            for piece in pieces[0:-w]:
                if all(map(lambda x: x in pieces, [tuple(map(sum, zip(piece, (m, 0)))) for m in range(w)])):
                    win = True

                if all(map(lambda x: x in pieces, [tuple(map(sum, zip(piece, (0, m)))) for m in range(w)])):
                    win = True

                if all(map(lambda x: x in pieces, [tuple(map(sum, zip(piece, (m, m)))) for m in range(w)])):
                    win = True
        return win

    def randomize_position(self):
        while True:
            for player in self.players:
                self.pieces[player] = []

            for tile in self.board:
                seed = random.randint(0, len(self.players))
                if seed != 0:
                    self.pieces[self.players[seed - 1]].append(tile)

            for player in self.players:
                if self.win(player):
                    break
            else:
                break
        self.player_to_move = self.players[random.randint(0, len(self.players)-1)]

    def legal_moves(self):
        legal = []
        for vertex in self.board:
            if all(map(lambda x: vertex not in self.pieces[x], self.pieces)):
                legal.append(vertex)
        for player in self.players:
            if self.win(player):
                legal = []
        return legal

    def make_move(self, move):
        self.pieces[self.player_to_move].append(move)
        self.player_to_move = self.players[(self.players.index(self.player_to_move) + 1) % len(self.players)]
        self.history.append(move)

    def revert(self):
        if self.history:
            self.player_to_move = self.players[self.players.index(self.player_to_move) - 1]
            self.pieces[self.player_to_move].remove(self.history.pop(-1))
            return True
        else:
            return False

    def utility(self):
        utility = {}
        win = False

        for player in self.players:
            if self.win(player):
                utility[player] = 1
                win = True
            else:
                utility[player] = 0

        if not win:
            for player in self.players:
                utility[player] = 0.5

        return utility

    def neural_net_input(self):
        out = []

        for player in self.players:
            if player == self.player_to_move:
                out.append(1)
            else:
                out.append(0)

        for player in self.players:
            for tile in self.board:
                if tile in self.pieces[player]:
                    out.append(1)
                else:
                    out.append(0)

        return out


if __name__ == "__main__":
    test_game = TicTacToe()
    print(test_game.n_max(9))
    """
    test_training_data = test_game.neural_net_training_data(3, 1000)

    test_network = VanillaNetwork([len(test_game.neural_net_input()), 10, 10, 10, 10, len(test_game.utility())])

    test_network.SGD(test_training_data, 3, 100, 1)
    """