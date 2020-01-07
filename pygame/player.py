#!/usr/bin/env python
""" player.py Humberto Henrique Campos Pinheiro 
Human and Computer classes
"""

from evaluator import Evaluator1,Evaluator2,Evaluator3
from config import WHITE, BLACK
from minimax import Minimax
from copy import deepcopy
import random


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

    def get_current_board(self, board):
        self.current_board = board

    def get_move(self):
        if self.level == 4:
            pass #TODO
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
