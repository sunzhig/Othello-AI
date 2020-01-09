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
        

    def get_current_board(self, board):
        self.current_board = board

    def get_move(self):
        if self.level == 4:
            return self.minimaxObj.a_b(self.current_board, None,self.depthLimit, 1,self.color,
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

class Trainer(object):
    def __init__(self, color):
        self.color = color

    def get_current_board(self, board):
        self.current_board = board

    def get_move(self):
        return self.greedy(self.current_board, self.color,
                                       change_color(self.color))
    def greedy(self,board, player, opponent):
        valid_moves = board.get_valid_moves(player)
        maxValue = -10000
        bestChild = board
        for move in valid_moves:
            child = deepcopy(board)
            child.apply_move(move,player)
            score = self.score(child, player, opponent)
            if score > maxValue:
                maxValue = score
                bestChild = child
        return 0,bestChild

    def dumbScore(self,array,colour,opponent):
        score = 0
        #+1 if it's player colour, -1 if it's opponent colour
        for x in range(8):
            for y in range(8):
                if array[x][y]==colour:
                    score+=1
                elif array[x][y]==opponent:
                    score-=1
        return score

    #Less simple but still simple heuristic. Weights corners and edges as more
    def slightlyLessDumbScore(self,array,colour,opponent):
        score = 0
        #Go through all the tiles	
        for x in range(8):
            for y in range(8):
                #Normal tiles worth 1
                add = 1
                #Edge tiles worth 3
                if (x==0 and 1<y<6) or (x==7 and 1<y<6) or (y==0 and 1<x<6) or (y==7 and 1<x<6):
                    add=3
                #Corner tiles worth 5
                elif (x==0 and y==0) or (x==0 and y==7) or (x==7 and y==0) or (x==7 and y==7):
                    add = 5
                #Add or subtract the value of the tile corresponding to the colour
                if array[x][y]==colour:
                    score+=add
                elif array[x][y]==opponent:
                    score-=add
        return score

    #Heuristic that weights corner tiles and edge tiles as positive, adjacent to corners (if the corner is not yours) as negative
    #Weights other tiles as one point
    def decentHeuristic(self,array,colour,opponent):
        score = 0
        cornerVal = 25
        adjacentVal = 5
        sideVal = 5
        #Go through all the tiles	
        for x in range(8):
            for y in range(8):
                #Normal tiles worth 1
                add = 1
                
                #Adjacent to corners are worth -3
                if (x==0 and y==1) or (x==1 and 0<=y<=1):
                    if array[0][0]==colour:
                        add = sideVal
                    else:
                        add = -adjacentVal


                elif (x==0 and y==6) or (x==1 and 6<=y<=7):
                    if array[7][0]==colour:
                        add = sideVal
                    else:
                        add = -adjacentVal

                elif (x==7 and y==1) or (x==6 and 0<=y<=1):
                    if array[0][7]==colour:
                        add = sideVal
                    else:
                        add = -adjacentVal

                elif (x==7 and y==6) or (x==6 and 6<=y<=7):
                    if array[7][7]==colour:
                        add = sideVal
                    else:
                        add = -adjacentVal


                #Edge tiles worth 3
                elif (x==0 and 1<y<6) or (x==7 and 1<y<6) or (y==0 and 1<x<6) or (y==7 and 1<x<6):
                    add=sideVal
                #Corner tiles worth 15
                elif (x==0 and y==0) or (x==0 and y==7) or (x==7 and y==0) or (x==7 and y==7):
                    add = cornerVal
                #Add or subtract the value of the tile corresponding to the colour
                if array[x][y]==colour:
                    score+=add
                elif array[x][y]==opponent:
                    score-=add
        return score

    #Seperating the use of heuristics for early/mid/late game.
    def score(self, board, player, opponent):
        whites, blacks, empty = board.count_stones()
        moves = whites + blacks
        valid_moves = board.get_valid_moves(player)
        if moves<=8:
            numMoves = 0
            for x in range(8):
                for y in range(8):
                    if (x,y)  in valid_moves:
                        numMoves += 1
            return numMoves+self.decentHeuristic(board.board,player,opponent)
        elif moves<=52:
            return self.decentHeuristic(board.board,player,opponent)
        elif moves<=58:
            return self.slightlyLessDumbScore(board.board,player,opponent)
        else:
            return self.dumbScore(board.board,player,opponent)


class Qlearner(object):
    def __init__(self, color, exp):
        self.color = color
        self.weights = [1,1]
        self.exp = exp

    def get_current_board(self, board):
        self.current_board = board
        
    def get_move(self):
        return self.greedy(self.current_board, self.color,
                                       change_color(self.color))
    def greedy(self,board, player, opponent):
        valid_moves = board.get_valid_moves(player)
        if random.random() < self.exp:
            pos = random.sample(valid_moves,1)
            board.apply_move(pos[0],player)
            return 0,board
        maxValue = -10000
        bestChild = board
        for move in valid_moves:
            child = deepcopy(board)
            child.apply_move(move,player)
            score,f1,f2 = self.score(child, player, opponent)
            if score > maxValue:
                maxValue = score
                bestChild = child
        self.updateweights(maxValue,player, opponent)
        return 0,bestChild

    def updateweights(self,value,player, opponent):
        alfa = 0.0004
        score, f1, f2 = self.score(self.current_board, player, opponent)
        differ = value - score
        self.weights[0] += alfa * differ * f1
        self.weights[1] += alfa * differ * f2
        a = abs(self.weights[0])
        b = abs(self.weights[1])
        self.weights[0] /= (a+b)
        self.weights[1] /= (a+b) 


    def score(self,board,player,opponent):
        priority_table = [
                [20, -3, 11, 8, 8, 11, -3, 20],
                [-3, -7, -4, 1, 1, -4, -7, -3],
                [11, -4, 2, 2, 2, 2, -4, 11],
                [8, 1, 2, -3, -3, 2, 1, 8],
                [8, 1, 2, -3, -3, 2, 1, 8],
                [11, -4, 2, 2, 2, 2, -4, 11],
                [-3, -7, -4, 1, 1, -4, -7, -3],
                [20, -3, 11, 8, 8, 11, -3, 20]
            ]
        table = 0
        valid_moves = board.get_valid_moves(player)
        numMoves = 0
        for x in range(8):
            for y in range(8):
                if (x,y)  in valid_moves:
                    numMoves += 1
        for x in range(8):
            for y in range(8):
                if board.board[x][y] == player:
                    table+=priority_table[x][y]
                elif board.board[x][y] == opponent:
                    table-=priority_table[x][y]
        score = self.weights[0] * numMoves + self.weights[1] * table
        return score, numMoves, table

