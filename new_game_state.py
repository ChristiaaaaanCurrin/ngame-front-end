from abc import ABC, abstractmethod
import numpy as np


class GameState:
    def __init__(self):
        self.top_piece = None
        self._super_pieces = []
        self._players = []
        self._sub_pieces = []

    def players(self, *player_statuses, not_player=None, add_piece=None):
        if add_piece and add_piece not in self.players():
            self._players.append(add_piece)
        elif add_piece:
            return False

        players = []
        for player in self._players:
            if (player.status in player_statuses or not player_statuses) and player != not_player:
                players.append(player)
        return players

    def super_pieces(self, *players, add_piece=None):
        if add_piece and add_piece not in self.super_pieces():
            self._super_pieces.append(add_piece)
        elif add_piece:
            return False

        supers = [self.top_piece] + self._super_pieces
        return supers

    def sub_pieces(self, *players, add_piece=None):
        if add_piece and add_piece not in self._sub_pieces:
            self._sub_pieces.append(add_piece)
        elif add_piece:
            return False
        if players:
            pieces = []
            for player in players:
                for piece in self._sub_pieces:
                    if piece.player == player and piece.location is not None:
                        pieces.append(piece)
        else:
            pieces = self.sub_pieces
        return pieces

    def all_pieces(self):
        return self.players() + self.sub_pieces() + self.sub_pieces()

    def add_piece(self, *pieces):
        count = 0
        for piece in pieces:
            if piece.player is piece and self.players(add_piece=piece):
                count = count + 1
            elif piece.bottom().player is piece.bottom and self.super_pieces(add_piece=piece):
                self.super_pieces(add_piece=piece)
                count = count + 1
            elif self.sub_pieces(add_piece=piece):
                count = count + 1
        return count

    def remove_piece(self, *pieces):
        count = 0
        for piece in pieces:
            while piece in self._players:
                self._players.remove(piece)
                count = count + 1
            while piece in self._sub_pieces:
                self._sub_pieces.remove(piece)
                count = count + 1
        return count


def max_n(top_piece, max_depth):
    """
    Similar to minimax, evaluates a game tree given best play (according to the utility method) by all players
    takes an integer depth and examines the tree of game states after all possible moves sequences up to 'max_depth'
    subsequent moves. End nodes (found by depth or by a lack of any legal moves after them) are evaluated by the
    'utility' method. Utilities are assigned to parent game states by which of the children is the best for the
    'player_to_move' of the parent. The resulting utility assigned to the original game state is returned
    :param top_piece: top piece of game to be tested
    :param max_depth: integer, indicates how many moves to the bottom of the value search tree
    :return: dictionary of values keyed by payers
    """
    move_tree = [top_piece.legal_moves()]  # tracks unexplored moves of current game state and its parents
    utility_tree = [[]]  # gets an empty list for every node in the current branch, to be populated later
    depth = 0  # start at depth 0

    while True:
        # Starting from a new position
        player_to_maximize = top_piece.bottom().player

        # In the middle of the tree? Go down.
        if depth != max_depth and move_tree[-1]:  # if in the middle of an unexplored branch of the game state tree
            move = move_tree[-1].pop(0)  # grab the first unexplored move and remove it from the move tree

            top_piece.execute_move(move)  # make the move on the game_state
            utility_tree.append([])  # tack on an empty list for utilities
            move_tree.append(top_piece.legal_moves())  # every legal move from the new_game state is a new branch
            depth = depth + 1  # record the change in depth
            continue  # rerun loop from new game state

        # Nowhere to go down? Go up.
        else:
            if (not top_piece.legal_moves()) or (depth == max_depth):  # only need utility from bottom of the tree
                utility_tree[-1].append(top_piece.utility())  # add utility to the list of the parent

            # If you're not at the top, you can go up
            if depth != 0:  # unless at the top...
                top_piece.revert()  # revert from current position to parent position
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
