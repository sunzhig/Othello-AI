# Minimax module
# Implements a generic minimax with alpha-beta
# prunning algorithm for games like chess or reversi.
# Thu Feb 18 21:54:38 Humberto Pinheiro
from copy import deepcopy
INFINITY = 100000


class Minimax(object):

    def __init__(self, heuristic_eval):
        """ Create a new minimax object
        player - current player's color
        opponent - opponent's color
        """
        self.heuristic_eval = heuristic_eval

    # error: always return the same board in same cases
    def minimax(self, board, parentBoard, depth, player, opponent,type,
                alfa=-INFINITY, beta=INFINITY):
        bestChild = board
        if depth == 0:
            return (self.heuristic_eval(parentBoard, board, depth,
                                        player, opponent), board)
        valid_moves = board.get_valid_moves(player)
        for move in valid_moves:
            child = deepcopy(board)
            child.apply_move(move,player)
            if board.board[move[0]][move[1]] == -1 and type == True:
                child1 = deepcopy(board)
                child2 = deepcopy(board)
                child1.board[move[0]][move[1]] = player
                for i in range(1, 9):
                    child.flip(i, move, player)
                child2.board[move[0]][move[1]] = opponent
                for i in range(1, 9):
                    child2.flip(i, move, opponent)
                score1, newChild1 = self.minimax(
                child, board, depth - 1, opponent, player, type, -beta, -alfa)
                score2, newChild2 = self.minimax(
                child2, board, depth - 1, opponent, player, type, -beta, -alfa)
                score = 0.6 * score1 + 0.4 * score2
            else:
                score, newChild = self.minimax(
                    child, board, depth - 1, opponent, player, type,-beta, -alfa)
            score = -score
            if score > alfa:
                alfa = score
                bestChild = child
            if beta <= alfa:
                break

        return (self.heuristic_eval(board, board, depth, player,
                                    opponent), bestChild)
