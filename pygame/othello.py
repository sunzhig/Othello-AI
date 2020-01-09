#!/usr/bin/env python
"""
othello.py Humberto Henrique Campos Pinheiro
Game initialization and main loop

"""

import pygame
import ui
import player
import board
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
        self.gui = ui.Gui()
        self.board = board.Board()
        self.get_options()

    def get_options(self):
        # set up players
        player1, player2, level, mode = self.gui.show_options()
        random_index = []
        if player1 == "human":
            self.now_playing = player.Human(self.gui, BLACK)
        else:
            self.now_playing = player.Computer(BLACK, level,3,True)
        if player2 == "human":
            self.other_player = player.Human(self.gui, WHITE)
        else:
            self.other_player = player.Computer(WHITE, level,1,True)
        if mode == 'random':
            l = list(range(64))
            l.remove(35)
            l.remove(36)
            l.remove(27)
            l.remove(28)
            random_index = random.sample(l,4)
            for i in random_index:
                self.board.board[i%8][i//8] = -1
        self.gui.show_game(random_index)
        self.gui.update(self.board.board, 2, 2, self.now_playing.color,[])

    def run(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(2000)
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
            if self.other_player.type == 1:
                valid_moves = self.board.get_valid_moves(self.other_player.color)
            self.gui.update(self.board.board, blacks, whites,
                            self.now_playing.color,valid_moves)
            self.now_playing, self.other_player = self.other_player, self.now_playing
        self.gui.show_winner(winner)
        pygame.time.wait(3000)
        self.restart()

    def restart(self):
        self.board = board.Board()
        self.get_options()
        self.run()


def main():
    game = Othello()
    game.run()


if __name__ == '__main__':
    main()
