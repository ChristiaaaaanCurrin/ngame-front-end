from abc import ABC, abstractmethod
import numpy as np


class GameState(ABC):
    def __init__(self, top_token, players, tokens=None, pieces=None):
        self.top_token = top_token
        self.all_players = players

        if tokens:
            self.all_tokens = tokens
        else:
            self.tokens = [top_token]

        if pieces:
            self.all_sub_pieces = pieces
        else:
            self.all_pieces = []

    def players(self, *player_statuses, not_player=None):
        players = []
        for player in self.all_players:
            if (player.status in player_statuses or not player_statuses) and player != not_player:
                players.append(player)
        return players

    def sub_pieces(self, *players):
        if players:
            pieces = []
        else:
            pieces = self.all_sub_pieces

        for piece in self.all_pieces:
            for player in players:
                if piece.player == player and piece.location is not None:
                    pieces.append(piece)

        return pieces

    def tokens(self, *levels):
        tokens = []
        for token in self.all_tokens:
            if token.level in levels:
                tokens.append(token)
        return tokens

    def legal_moves(self):
        return self.top_token.legal_moves(self)

    def utility(self):
        utility = {}
        for player in self.players():
            utility[player] = player.utility(self)
        return utility

    def revert(self):
        if self.top_token.history:
            move = self.top_token.history.pop(-1)
            self.top_token.reverse_move(move)
            return True
        else:
            return False


def max_n(game_state, max_depth):
    """
    Similar to minimax, evaluates a game tree given best play (according to the utility method) by all players
    takes an integer depth and examines the tree of game states after all possible moves sequences up to 'max_depth'
    subsequent moves. End nodes (found by depth or by a lack of any legal moves after them) are evaluated by the
    'utility' method. Utilities are assigned to parent game states by which of the children is the best for the
    'player_to_move' of the parent. The resulting utility assigned to the original game state is returned
    :param game_state: game state to be tested
    :param max_depth: integer, indicates how many moves to the bottom of the value search tree
    :return: dictionary of values keyed by payers
    """
    move_tree = [game_state.legal_moves()]  # tracks unexplored moves of current game state and its parents
    utility_tree = [[]]  # gets an empty list for every node in the current branch, to be populated later
    depth = 0  # start at depth 0

    while True:
        # Starting from a new position
        player_to_maximize = game_state.top_token.player

        # In the middle of the tree? Go down.
        if depth != max_depth and move_tree[-1]:  # if in the middle of an unexplored branch of the game state tree
            move = move_tree[-1].pop(0)  # grab the first unexplored move and remove it from the move tree

            move.execute_move(game_state)  # make the move on the game_state
            utility_tree.append([])  # tack on an empty list for utilities
            move_tree.append(game_state.legal_moves())  # every legal move from the new_game state is a new branch
            depth = depth + 1  # record the change in depth
            continue  # rerun loop from new game state

        # Nowhere to go down? Go up.
        else:
            if (not game_state.legal_moves()) or (depth == max_depth):  # only need utility from bottom of the tree
                utility_tree[-1].append(game_state.utility())  # add utility to the list of the parent

            # If you're not at the top, you can go up
            if depth != 0:  # unless at the top...
                game_state.revert()  # revert from current position to parent position
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
        for player in game_state.players:
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
