from rule import Rule
from gui import GameGUI
from tkinter import *


class TicTacToe(Rule):
    def __init__(self, players=('X', 'O'), turn=0, rows=3, columns=3, to_win=3, explore=False, **kwargs):
        self.players = players
        self.turn = turn
        self.rows = rows
        self.columns = columns
        self.to_win = to_win
        self.explore = explore
        self.history = []
        self.board = []
        self.win_masks = []
        self.occupancy = {}
        super().__init__(player=players[turn], **kwargs)

    def refresh_init(self):
        self.game_state.add_rules(self)
        super().refresh_init()

        for player in self.players:
            self.occupancy[player] = 0
        self.board = [[None for c in range(self.columns)] for r in range(self.rows)]

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
        return '~Tic Tac Toe~'

    def clear_board(self):
        for row in self.board:
            for n in range(len(row)):
                row[n] = None
        for player in self.players:
            self.occupancy[player] = 0

    def execute_move(self, move):
        if self.explore:
            if move == "restart":
                self.clear_board()
                return
            elif move == "undo":
                self.undo_move(self.history.pop(-1))
                return
            else:
                self.history.append(move)
        r, c = move
        self.board[r][c] = self.player
        self.occupancy[self.player] = self.occupancy[self.player] | (1 << (r*self.columns + c))
        self.turn = (self.turn + 1) % len(self.players)
        self.player = self.players[self.turn]
        self.changed()

    def undo_move(self, move):
        r, c = move
        self.board[r][c] = None
        self.turn = (self.turn - 1) % len(self.players)
        self.player = self.players[self.turn]
        self.occupancy[self.player] = self.occupancy[self.player] & ~(1 << (r*self.columns + c))
        self.changed()

    def winners(self):
        winners = []
        for player in self.players:
            for mask in self.win_masks:
                if not ((~self.occupancy[player]) & mask):
                    winners.append(player)
                    break
        return winners

    def generate_legal_moves(self):
        legal = []
        if not self.winners():
            for r in range(self.rows):
                for c in range(self.columns):
                    if not self.board[r][c]:
                        legal.append((r, c))
        if self.explore:
            legal.append("undo")
            legal.append("restart")
        return legal


if __name__ == "__main__":
    g = TicTacToe(rows=4, columns=4)
    print(g.win_masks)
