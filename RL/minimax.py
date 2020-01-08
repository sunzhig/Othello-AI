# Minimax module
# Implements a generic minimax with alpha-beta
# prunning algorithm for games like chess or reversi.
# Thu Feb 18 21:54:38 Humberto Pinheiro
from copy import deepcopy


class Minimax(object):

    def __init__(self, heuristic_eval):
        """ Create a new minimax object
        player - current player's color
        opponent - opponent's color
        """
        self.heuristic_eval = heuristic_eval

    # error: always return the same board in same cases
    def minimax(self, board, depth, player, opponent):
        valid_moves = board.get_valid_moves(player)
        maxValue = -10000
        maxmove = None
        for move in valid_moves:
            child = deepcopy(board)
            child.updateBoard(player, move[0], move[1])
            score = self.heuristic_eval(child, player, opponent)
            if score > maxValue:
                maxValue = score
                maxmove = move
        return maxmove
