import pygame
import player
import board
import ui
from config import BLACK, WHITE
import random
import numpy as np

class Othello:
    """
    Game main class.
    """

    def __init__(self):
        """ Show options screen and start game modules"""
        # start
        self.reply = 20
        self.size = 10

    def start(self):
        trainer = player.Trainer(BLACK)
        qlearner = player.Qlearner(WHITE,1)
        for i in range(self.reply):
            win = 0
            print("Epoch: %d"%i)
            qlearner.exp = (np.exp(-0.017*i)+0.11)/1.1
            print(qlearner.exp)
            for j in range(self.size):
                self.board = board.Board()
                self.now_playing = trainer
                self.other_player = qlearner
                self.run()
                if self.winner == 'white':
                    win+=1
            print("ql wins %d"%(win)) 
        print(qlearner.weights)
        
    def run(self):
        while True:
            if self.board.game_ended():
                whites, blacks, empty = self.board.count_stones()
                if whites > blacks:
                    winner = WHITE
                elif blacks > whites:
                    winner = BLACK
                else:
                    winner = None
                break
            self.now_playing.get_current_board(self.board)
            if self.board.get_valid_moves(self.now_playing.color) != []:
                score, self.board = self.now_playing.get_move()
            self.now_playing, self.other_player = self.other_player, self.now_playing
        if winner == WHITE:
            win = 'white'
        elif winner == BLACK:
            win = 'black'
        else:
            win = 'tie'
        self.winner = win


def main():
    game = Othello()
    game.start()


if __name__ == '__main__':
    main()