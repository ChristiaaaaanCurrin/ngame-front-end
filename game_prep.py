class GameState:
    def __init__(self, players, player_to_move):
        self.players = players
        self.player_to_move = players[player_to_move]

    def utility(self):
        pass

    def make_move(self, move):
        pass

    def revert(self):
        pass

    def legal_moves(self):
        pass

    def neural_net_input(self):
        pass

    def n_max(self, depth):
        def best_move_utility(player, utilities):
            current_max = utilities[0]
            for utility in utilities:
                if utility[player] > current_max[player]:
                    current_max = utility
            return current_max

        move_tree = [self.legal_moves()]
        value_tree = [[]]
        while True:
            player_to_maximize = self.player_to_move
            if depth != 0 and move_tree[-1]:
                move = move_tree[-1].pop(0)

                self.make_move(move)

                value_tree.append([])
                move_tree.append(self.legal_moves())
                depth = depth - 1
                continue

            else:
                if self.legal_moves() and depth != 0:
                    pass
                else:
                    value_tree[-1].append(self.utility())

                if self.revert():
                    depth = depth + 1
                    move_tree.pop(-1)
                    value_tree[-2].append(best_move_utility(player_to_maximize, value_tree.pop(-1)))
                    continue
                else:
                    value_tree[-1] = best_move_utility(self.player_to_move, value_tree[-1])
                    break

        return value_tree
