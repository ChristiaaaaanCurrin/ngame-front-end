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
        player_to_maximize = self.player_to_move

        while True:
            if depth != 0 and move_tree[-1]:
                player_to_maximize = self.player_to_move
                move = move_tree[-1].pop(0)

                self.make_move(move)

                move_tree.append(self.legal_moves())
                value_tree.append([])
                depth = depth - 1
                continue

            else:
                print('STOPPED')
                print(depth)
                if self.legal_moves() and depth != 0:
                    value_tree[-2].append(best_move_utility(player_to_maximize, value_tree.pop(-1)))
                else:
                    value_tree[-1].append(self.utility())

                if self.revert():
                    print('REVERTED')
                    print(self)
                    depth = depth + 1
                    move_tree.pop(-1)
                    continue
                else:
                    print('BROKEN')
                    break

        return value_tree
