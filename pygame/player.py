#!/usr/bin/env python
""" player.py Humberto Henrique Campos Pinheiro 
Human and Computer classes
"""

from evaluator import Evaluator1,Evaluator2,Evaluator3
from config import WHITE, BLACK
from minimax import Minimax
from copy import deepcopy
import random
import nn
import numpy as np
import itertools

def change_color(color):
    if color == BLACK:
        return WHITE
    else:
        return BLACK


class Human:

    """ Human player """

    def __init__(self, gui, color="black"):
        self.color = color
        self.gui = gui
        self.type = 1

    def get_move(self):
        """ Uses gui to handle mouse
        """
        validMoves = self.current_board.get_valid_moves(self.color)
        while True:
            move = self.gui.get_mouse_input()
            if move in validMoves:
                break
        self.current_board.apply_move(move, self.color)
        return 0, self.current_board

    def get_current_board(self, board):
        self.current_board = board


class Computer(object):

    def __init__(self, color, level,type,type2,prune=4):
        self.depthLimit = prune
        if type==1:
            evaluator = Evaluator1()
        elif type==2:
            evaluator = Evaluator2()
        else:
            evaluator = Evaluator3()
        self.minimaxObj = Minimax(evaluator.score)
        self.color = color
        self.type = 0
        self.level = level
        self.random = type2
        if level == 4:
            self.policy_net = nn.NN([64, 128, 128, 64, 64], 0)
            # This ought to decay
            self.epsilon = 0

            # Variables for Q learning
            self.play_history = []
            self.wins = 0
            self.policy_net.load("best.weights")

    def get_current_board(self, board):
        self.current_board = board

    def get_move(self):
        if self.level == 4:
            return self.minimaxObj.a_b(self.current_board, self.depthLimit, 1,self.color,
                                       change_color(self.color))
        if self.level == 3:
            return self.minimaxObj.minimax(self.current_board, None, self.depthLimit, self.color,
                                       change_color(self.color),self.random)
        if self.level == 2:
            max = 0
            maxindex = 0
            choices = self.current_board.get_valid_moves(self.color)
            whites,blacks,empty = self.current_board.count_stones()
            for i in choices:
                newBoard = deepcopy(self.current_board)
                newBoard.apply_move(i, self.color)
                newwhites,newblacks,newempty = newBoard.count_stones()
                if self.color == WHITE:
                    tmp = newwhites - whites
                else:
                    tmp = newblacks - blacks
                if tmp > max:
                    max = tmp
                    maxindex = i
            self.current_board.apply_move(maxindex,self.color)
            return 0,self.current_board
        if self.level == 1:
            move = random.sample(self.current_board.get_valid_moves(self.color), 1)[0]
            self.current_board.apply_move(move,self.color)
            return 0,self.current_board

    def RL(self,log_history = True):
        # Transform all of "this player's" tokens to 1s and the other player's
        # to -1s
        board_state = np.asarray(self.current_board.board).reshape((64,1))
        input_state = np.apply_along_axis(lambda x: int((x==self.color and 1) or (x!=0 and -1)),
                                          1, board_state).reshape((64,1))
        vaild_moves = self.current_board.get_valid_moves(self.color)
        made_move = False
        pos = None

        # epsilon greedy to pick random move
        if np.random.random() < self.epsilon:
            positions = list(itertools.product(range(8), repeat = 2))
            random.shuffle(positions)
            while not made_move and positions:
                pos = positions.pop()
                if pos in vaild_moves:
                    made_move = True
                    self.current_board.apply_move(pos,self.color)

        else:
            out = self.policy_net.getOutput(input_state)
            # Sort the possible moves lowest to highest desire
            positions = [(v,i) for i,v in enumerate(out)]
            positions.sort(key = lambda x: x[0], reverse = True)

            while not made_move and positions:
                # Grab next desired move point
                scalar_play_point = positions.pop()[1]
                # Convert the scalar to a 2D coordinate to play on the board
                pos = scalar_play_point // 8, scalar_play_point % 8
                if pos in vaild_moves:
                    made_move = True
                    self.current_board.apply_move(pos,self.color)

        if log_history:
            self.play_history.append((np.copy(input_state), pos[0]*8 + pos[1]))

        return 0,self.current_board