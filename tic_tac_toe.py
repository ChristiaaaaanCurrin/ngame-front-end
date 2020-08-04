from rule import Rule
from timeit import default_timer


class TicTacToe(Rule):
    def __init__(self, players=('X', 'O'), turn=0, rows=3, columns=3, to_win=3):
        super().__init__(player=players[turn])
        self.players = players
        self.turn = turn
        self.rows = rows
        self.columns = columns
        self.to_win = to_win
        self.occupancy = {}
        for player in self.players:
            self.occupancy[player] = 0
        self.board = [[None for c in range(columns)] for r in range(rows)]

        self.win_masks = []

        row_mask = (1 << self.to_win) - 1
        for r in range(self.rows):
            self.win_masks.append(row_mask)
            for c in range(self.columns - self.to_win):
                row_mask = row_mask << 1
                self.win_masks.append(row_mask)
            row_mask = row_mask << self.to_win

        column_mask = 1
        for w in range(self.to_win - 1):
            column_mask = 1 | (column_mask << self.columns)
        for c in range(self.columns):
            self.win_masks.append(column_mask)
            for r in range(self.rows - self.to_win):
                column_mask = column_mask << self.columns
                self.win_masks.append(column_mask)
            column_mask = column_mask << 1

        diagonal_mask = 1
        for w in range(self.to_win - 1):
            diagonal_mask = diagonal_mask | (diagonal_mask << (self.columns + 1))
        for r in range(self.rows - self.to_win + 1):
            for c in range(self.columns - self.to_win + 1):
                self.win_masks.append(diagonal_mask)
                diagonal_mask = diagonal_mask << 1
            diagonal_mask = diagonal_mask << self.to_win

        diagonal_mask = 1 << (self.columns - 1)
        for w in range(self.to_win - 1):
            diagonal_mask = diagonal_mask | (diagonal_mask << (self.columns - 1))
        for r in range(self.rows - self.to_win + 1):
            for c in range(self.columns - self.to_win + 1):
                self.win_masks.append(diagonal_mask)
                diagonal_mask = diagonal_mask >> 1
            diagonal_mask = diagonal_mask << self.to_win

    def __str__(self):
        return str(self.board)\
             + str([(player, bin(self.occupancy[player])) for player in self.players])\
             + str(self.winners())

    def execute_move(self, move):
        r, c = move
        self.board[r][c] = self.player
        self.occupancy[self.player] = self.occupancy[self.player] | (1 << (r*self.columns + c))
        self.turn = (self.turn + 1) % len(self.players)
        self.player = self.players[self.turn]

    def undo_move(self, move):
        r, c = move
        self.board[r][c] = None
        self.turn = (self.turn - 1) % len(self.players)
        self.player = self.players[self.turn]
        self.occupancy[self.player] = self.occupancy[self.player] & ~(1 << (r*self.columns + c))

    def winners(self):
        winners = []
        for player in self.players:
            for mask in self.win_masks:
                if not ((~self.occupancy[player]) & mask):
                    winners.append(player)
                    break
        return winners

    def get_legal_moves(self):
        legal = []
        if not self.winners():
            for r in range(self.rows):
                for c in range(self.columns):
                    if not self.board[r][c]:
                        legal.append((r, c))
        return legal

    def get_utility(self):
        utility = {}
        winners = self.winners()
        if winners:
            for player in self.players:
                if player in winners:
                    utility[player] = 1
                else:
                    utility[player] = -1
        else:
            for player in self.players:
                utility[player] = 0
        return utility


if __name__ == "__main__":
    g = TicTacToe(rows=3, columns=3, to_win=3)
    for m in g.win_masks:
        print(bin(m))

    start = default_timer()
    print(g.max_n(16))
    stop = default_timer()
    print(stop - start)
