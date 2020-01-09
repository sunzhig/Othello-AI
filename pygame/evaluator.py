from config import BLACK, WHITE, EMPTY


class Evaluator1(object):
    WIPEOUT_SCORE = 1000  # a move that results a player losing all pieces
    PIECE_COUNT_WEIGHT = [0, 0, 0, 4, 1]
    POTENTIAL_MOBILITY_WEIGHT = [5, 4, 3, 2, 0]
    MOBILITY_WEIGHT = [7, 6, 5, 4, 0]
    CORNER_WEIGHT = [35, 35, 35, 35, 0]
    EDGE_WEIGHT = [0, 3, 4, 5, 0]
    XSQUARE_WEIGHT = [-8, -8, -8, -8, 0]

    def get_piece_differential(self, deltaBoard, band):
        """Return the piece differential score Given a board resultant of the
        difference between the initial board and the board after the
        move and a weight band returns the count of the pieces the
        player has gained minus the same count for the opponent.

        """
        if Evaluator1.PIECE_COUNT_WEIGHT[band] != 0:
            whites, blacks, empty = deltaBoard.count_stones()
            if self.player == WHITE:
                myScore = whites
                yourScore = blacks
            else:
                myScore = blacks
                yourScore = whites
            return Evaluator1.PIECE_COUNT_WEIGHT[band] * (myScore - yourScore)
        return 0

    def get_corner_differential(self, deltaCount, deltaBoard, band):
        """Return the corner differential score Given a board resultant of
        the difference between the initial board and the board after
        the move and a weight band returns the count of the corner the
        player has gained minus the same count for the opponent.

        """
        if Evaluator1.CORNER_WEIGHT[band] != 0:
            # corner differential
            myScore = 0
            yourScore = 0
            for i in [0, 7]:
                for j in [0, 7]:
                    if deltaBoard.board[i][j] == self.player:
                        myScore += 1
                    elif deltaBoard.board[i][j] == self.enemy:
                        yourScore += 1
                    if myScore + yourScore >= deltaCount:
                        break
                if myScore + yourScore >= deltaCount:
                    break
            return Evaluator1.CORNER_WEIGHT[band] * (myScore - yourScore)
        return 0

    def get_edge_differential(self, deltaCount, deltaBoard, band):
        """Return the piece differential score Given a board resultant of the
        difference between the initial board and the board after the
        move and a weight band returns the count of the A-squares and
        B-squares the player has gained minus the same count for the
        opponent.  A-squares are the (c1, f1, a3, a6, h3, h6, c8, f8).
        B-squares are the (d1, e1, a4, a5, h4, h5, d8, e8).

        """
        if Evaluator1.EDGE_WEIGHT[band] != 0:
            myScore = 0
            yourScore = 0
            squares = [(a, b) for a in [0, 7] for b in range(1, 7)] \
                + [(a, b) for a in range(1, 7) for b in [0, 7]]
            for x, y in squares:
                if deltaBoard.board[x][y] == self.player:
                    myScore += 1
                elif deltaBoard.board[x][y] == self.enemy:
                    yourScore += 1
                if myScore + yourScore >= deltaCount:
                    break
            return Evaluator1.EDGE_WEIGHT[band] * (myScore - yourScore)
        return 0

    def get_xsquare_differential(self, startBoard, currentBoard, deltaBoard, band):
        """ Return the difference of x-squares owned between the players
        A x-square is the square in front of each corner. Consider only new pieces, not flipped
        ones and only squares next to open corner.
        startBoard - board before the move
        currentBoard - board after the move
        deltaBoard - differential board between startBoard and currentBoard
        """
        if Evaluator1.XSQUARE_WEIGHT[band] != 0:
            myScore = 0
            yourScore = 0
            for x, y in [(a, b) for a in [1, 6] for b in [1, 6]]:
                if deltaBoard.board[x][y] != EMPTY and startBoard.board[x][y] == EMPTY:
                    # if the piece is new consider this square if the nearest
                    # corner is open
                    cornerx = x
                    cornery = y
                    if cornerx == 1:
                        cornerx = 0
                    elif cornerx == 6:
                        cornerx = 7
                    if cornery == 1:
                        cornery = 0
                    elif cornery == 6:
                        cornery = 7
                    if currentBoard.board[cornerx][cornery] == EMPTY:
                        if currentBoard.board[x][y] == self.player:
                            myScore += 1
                        elif currentBoard.board[x][y] == self.enemy:
                            yourScore += 1
            return Evaluator1.XSQUARE_WEIGHT[band] * (myScore - yourScore)
        return 0

    def get_potential_mobility_differential(self, startBoard, currentBoard, band):
        """ Return the difference between opponent and player number of frontier pieces.
        startBoard - board before the move
        currentBoard - board after the move
        band - weight
        """
        if Evaluator1.POTENTIAL_MOBILITY_WEIGHT[band] != 0:
            myScore = currentBoard.get_adjacent_count(
                self.enemy) - startBoard.get_adjacent_count(self.enemy)
            yourScore = currentBoard.get_adjacent_count(
                self.player) - startBoard.get_adjacent_count(self.player)
            return Evaluator1.POTENTIAL_MOBILITY_WEIGHT[band] * (myScore - yourScore)
        return 0

    def get_mobility_differential(self, startBoard, currentBoard, band):
        """ Return the difference of number of valid moves between the player and his opponent.
        startBoard - board before the move
        currentBoard - board after the move
        band - weight
        """
        myScore = len(currentBoard.get_valid_moves(self.player)) - \
            len(startBoard.get_valid_moves(self.player))
        yourScore = len(currentBoard.get_valid_moves(
            self.enemy)) - len(startBoard.get_valid_moves(self.enemy))
        return Evaluator1.MOBILITY_WEIGHT[band] * (myScore - yourScore)

    def score(self, startBoard, board, currentDepth, player, opponent):
        """ Determine the score of the given board for the specified player.
        - startBoard the board before any move is made
        - board the board to score
        - currentDepth depth of this leaf in the game tree
        - searchDepth depth used for searches.
        - player current player's color
        - opponent opponent's color
        """
        self.player = player
        self.enemy = opponent
        sc = 0
        whites, blacks, empty = board.count_stones()
        deltaBoard = board.compare(startBoard)
        deltaCount = sum(deltaBoard.count_stones())

        # check wipe out
        if (self.player == WHITE and whites == 0) or (self.player == BLACK and blacks == 0):
            return -Evaluator1.WIPEOUT_SCORE
        if (self.enemy == WHITE and whites == 0) or (self.enemy == BLACK and blacks == 0):
            return Evaluator1.WIPEOUT_SCORE

        # determine weigths according to the number of pieces
        piece_count = whites + blacks
        band = 0
        if piece_count <= 16:
            band = 0
        elif piece_count <= 32:
            band = 1
        elif piece_count <= 48:
            band = 2
        elif piece_count <= 64 - currentDepth:
            band = 3
        else:
            band = 4

        sc += self.get_piece_differential(deltaBoard, band)
        sc += self.get_corner_differential(deltaCount, deltaBoard, band)
        sc += self.get_edge_differential(deltaCount, deltaBoard, band)
        sc += self.get_xsquare_differential(startBoard,
                                            board, deltaBoard, band)
        sc += self.get_potential_mobility_differential(startBoard, board, band)
        sc += self.get_mobility_differential(startBoard, board, band)
        return sc

class Evaluator2(object):
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
    def score(self, startBoard, board, currentDepth, player, opponent):
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

class Evaluator3(object):
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
    def score(self, startBoard, board, currentDepth, player, opponent):
        valid_moves = board.get_valid_moves(player)
        whites,blacks,empty = board.count_stones()
        numMoves = whites+blacks
        score = 0
        if numMoves <= 8:
            num = 0
            for x in range(8):
                for y in range(8):
                    if (x,y)  in valid_moves:
                        num += 1
            score+=num
        if numMoves > 58:
            if player == BLACK:
                score = blacks - whites
            elif player == WHITE:
                score = whites - blacks
            return score
        for x in range(8):
            for y in range(8):
                if board.board[x][y] == player:
                    score+=Evaluator3.priority_table[x][y]
                elif board.board[x][y] == opponent:
                    score-=Evaluator3.priority_table[x][y]

        return score
