#!/usr/bin/env python
"""
othello.py Humberto Henrique Campos Pinheiro
Game initialization and main loop

"""

import pygame
import player
import board
import ui
from config import BLACK, WHITE
import random

# py2exe workaround
# import sys
# import os
# sys.stdout = open(os.devnull, 'w')
# sys.stderr = open(os.devnull, 'w')


class Othello:
    """
    Game main class.
    """

    def __init__(self):
        """ Show options screen and start game modules"""
        # start
        self.reply = 100
        self.gui = ui.Gui()


    def start(self):
        bwin = 0
        wwin = 0
        tie = 0
        for i in range(self.reply):
            self.restart()
            pygame.time.wait(3000)
            if self.winner == 'white':
                wwin+=1
            elif self.winner == 'black':
                bwin+=1
            else:
                tie+=1
        print("Total run %d times:black wins %d times,white wins %d times,tie %d times"%(self.reply,bwin,wwin,tie)) 
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
            whites, blacks, empty = self.board.count_stones()
            valid_moves = []
            self.gui.update(self.board.board, blacks, whites,
                            self.now_playing.color,valid_moves)
            self.now_playing, self.other_player = self.other_player, self.now_playing
        if winner == WHITE:
            win = 'white'
        elif winner == BLACK:
            win = 'black'
        else:
            win = 'tie'
        self.winner = win
        print("Winner is %s"%(win))

    def restart(self):
        self.board = board.Board()
        self.now_playing = player.Computer(BLACK, 3,3,False)
        self.other_player = player.Computer(WHITE, 3,3,True)
        l = list(range(64))
        l.remove(35)
        l.remove(36)
        l.remove(27)
        l.remove(28)
        random_index = [12,24,38,48]
        for i in random_index:
            self.board.board[i%8][i//8] = -1
        self.gui.show_game(random_index)
        self.gui.update(self.board.board, 2, 2, self.now_playing.color,[])
        self.run()


def main():
    game = Othello()
    game.start()


if __name__ == '__main__':
    main()
