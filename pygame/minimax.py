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
    
    def alpha_beta(game, depth, alpha, beta):
        best_action = -1, -1
        if game.is_game_ended():
            value = np.sum(game.board)
            if game.color == WHITE:
                value = -value
            value += MARGIN if value > 0 else -MARGIN
            return best_action, value

        if depth == 0 or is_timeout():
            value = np.sum(game.board * WEIGHTS)
            if game.color == WHITE:
                value = -value
            return best_action, value

        board = game.board
        color = game.color

        has_legal_move = False
        for i in range(8):
            for j in range(8):
                if board[i][j] != 0 or not game.place(i, j, color, check_only=True):
                    continue
                has_legal_move = True
                new_game = game.copy()
                new_game.apply_moveXY(i, j)
                value = -alpha_beta(new_game, depth - 1, -beta, -alpha)[1]
                if value > alpha:
                    alpha = value
                    best_action = i, j
                    if beta <= alpha:
                        return best_action, value

        if not has_legal_move:
            new_game = game.copy()
            new_game.apply_moveXY(-1, -1)
            return best_action, -alpha_beta(new_game, depth, -beta, -alpha)[1]

        return best_action, alpha
    def a_b(self,board, pastboard,depth, maximizing, player, opponent,alpha=-INFINITY, beta=INFINITY):
        choices = board.get_valid_moves(player)
        if depth==0 or len(choices)==0:
            return ([self.heuristic_eval(board, board, depth,player, opponent),board])
        if maximizing:
            v = -float("inf")
            bestBoard = board
            for move in choices:
                child = deepcopy(board)
                child.apply_move(move,player)
                boardValue = self.a_b(child,board,depth-1,False,opponent,player,alpha,beta)[0]
                if boardValue>v:
                    v = boardValue
                    bestBoard = child
                alpha = max(alpha,v)
                if beta <= alpha:
                    break
            return([v,bestBoard])
        else:
            v = float("inf")
            bestBoard = board
            for move in choices:
                child = deepcopy(board)
                child.apply_move(move,player)
                boardValue = self.a_b(child,board,depth-1,True,opponent,player,alpha,beta)[0]
                if boardValue<v:
                    v = boardValue
                    bestBoard = child
                beta = min(beta,v)
                if beta<=alpha:
                    break
            return([v,bestBoard])