import numpy as np


class GameState:
    def __init__(self):
        self._top_rules = []
        self._players = []

    def get_players(self, *player_statuses, not_player=None):
        players = []
        for player in self._players:
            if (player.status in player_statuses or not player_statuses) and player != not_player:
                players.append(player)
        return players

    def get_top_rules(self, *players):
        if players:
            return filter(lambda x: x.player in players, self._top_rules)
        else:
            return self._top_rules

    def get_all_rules(self):
        all_rules = []
        for top_rule in self._top_rules:
            all_rules.extend(top_rule.get_piece())
        return all_rules

    def add_pieces(self, *top_rules):
        for top_rule in top_rules:
            if top_rule not in self._top_rules:
                self._top_rules.append(top_rule)

                for rule in top_rule.get_piece():
                    rule.game_state = self
                    if rule.player and rule.player not in self._players:
                        self._players.append(rule.player)

    def add_players(self, *rules):
        for rule in rules:
            if rule.player not in self._players:
                self._players.append(rule.player)

    def remove_pieces(self, *top_rules):
        for rule in top_rules:
            while rule in self._top_rules:
                self._top_rules.remove(rule)


def max_n(game, max_depth):
    """
    Similar to minimax, evaluates a game tree given best play (according to the utility method) by all players
    takes an integer depth and examines the tree of game states after all possible moves sequences up to 'max_depth'
    subsequent moves. End nodes (found by depth or by a lack of any legal moves after them) are evaluated by the
    'utility' method. Utilities are assigned to parent game states by which of the children is the best for the
    'player_to_move' of the parent. The resulting utility assigned to the original game state is returned
    :param game: game to be tested
    :param max_depth: integer, indicates how many moves to the bottom of the value search tree
    :return: dictionary of values keyed by payers
    """
    move_tree = [game.get_legal_moves()]  # tracks unexplored moves of current game state and its parents
    utility_tree = [[]]  # gets an empty list for every node in the current branch, to be populated later
    depth = 0  # start at depth 0

    while True:
        # Starting from a new position
        player_to_maximize = game.get_bottom_rule().player

        # In the middle of the tree? Go down.
        if depth != max_depth and move_tree[-1]:  # if in the middle of an unexplored branch of the game state tree
            move = move_tree[-1].pop(0)  # grab the first unexplored move and remove it from the move tree

            game.execute_move(move)  # make the move on the game_state
            utility_tree.append([])  # tack on an empty list for utilities
            move_tree.append(game.get_legal_moves())  # every legal move from the new_game state is a new branch
            depth = depth + 1  # record the change in depth
            continue  # rerun loop from new game state

        # Nowhere to go down? Go up.
        else:
            if (not game.get_legal_moves()) or (depth == max_depth):  # only need utility from bottom of the tree
                utility_tree[-1].append(game.get_utility())  # add utility to the list of the parent

            # If you're not at the top, you can go up
            if depth != 0:  # unless at the top...
                game.revert()  # revert from current position to parent position
                # utility of the position is the best child utility for the player to move
                # utility of the position is added to the utility list of the parent
                utility_tree[-2].append(dictionary_max(player_to_maximize, utility_tree.pop(-1)))
                move_tree.pop(-1)  # cut the explored branch from the tree
                depth = depth - 1  # record change in depth
                continue  # rerun loop from new game state
            # Can't go down or up? Must be done.
            else:
                # utility of the position is the best child utility for the player to move
                n_max_utility = dictionary_max(player_to_maximize, utility_tree[-1])
                break  # exit the loop
    return n_max_utility  # don't forget why you came here


def neural_net_training_data(game, game_state, n_max_depth, batch_size):
    """
    creates a list containing 'batch size' tuples of inputs and outputs for the neural net
    inputs are lists of values that contain all the information for the position
    outputs are lists of values that contain the n_max evaluation for the position to depth 'n_max_depth'
    :param game: game of game_state
    :param game_state: game state to be evaluated
    :param n_max_depth: integer, indicates the depth to which the neural net inputs are evaluated
    :param batch_size: integer, indicates the number of positions used as training data
    :return: list of tuples of lists of values
    """
    training_data = []
    for i in range(batch_size):
        game.randomize_position(game_state)  # create random position
        neural_net_output = []
        for player in game_state.get_players:
            neural_net_output.append(max_n(game_state, n_max_depth)[player])  # generate output from n_max function
        training_data.append((np.asarray(game.neural_net_input(game_state)), np.asarray(neural_net_output)))
    return training_data  # don't forget to return


def dictionary_max(key, dictionaries):
    """

    :param key: a key in the dictionary
    :param dictionaries: list of dictionaries with the same keys, dictionary entries must be ordered (<,> defined)
    :return: the dictionary where the value of dictionary[key] is maximized
    """
    current_max = dictionaries[0]
    for dictionary in dictionaries:
        if dictionary[key] > current_max[key]:
            current_max = dictionary
    return current_max
