import random
import json
import numpy as np

LEARN = True

class Game:
    def __init__(self):
        self.board = range(0,9)
        self.gameover = False
        self.current_player = 'X'
        self.turns = 0
        try:
            f = open("policyO.dat","r")
            self.policyO = json.loads(f.read())
            f.close()
        except (IOError, ValueError) as e:
            self.policyO = {}
        if LEARN:
            try:
                fx = open("policyX.dat","r")
                self.policyX = json.loads(fx.read())
                fx.close()
            except (IOError, ValueError) as e:
                self.policyX = {}
        self.actionsO = []
        self.actionsX = []
        self.winner = None

    def display_board(self):
        print self.board[0],self.board[1],self.board[2]
        print self.board[3],self.board[4],self.board[5]
        print self.board[6],self.board[7],self.board[8]

    def get_player_input(self):
        move = -1
        while move not in range(0,9):
            move = raw_input("Turn "+str(self.turns)+": Player X, please select a square: ");
            try:
                move = int(move)
            except ValueError:
                move = -1
            finally:
                if move in range(0,9):
                    if self.board[move] in ('X','O'):
                        print "Occupied!"
                        move = -1
                else:
                    print "Invalid input!"
                    move = -1
        self.board[move] = 'X'
        # End Turn
        self.current_player = 'O'

    def get_ai_player_input(self):
        state = "".join(str(e) for e in self.board)
        if state not in self.policyX:
            # Create new fully random move policy based on available moves
            self.policyX[state] = []
            for count,elem in enumerate(self.board):
                # Create a blank slate for all legal moves
                if self.board[count] in range(0,9):
                    self.policyX[state].append(1)
                else:
                    self.policyX[state].append(0)
        move_prob = np.array(self.policyX[state][0:9])/float(sum(self.policyX[state][0:9]))
        pick_move = np.random.choice(9,1, p=move_prob)
        # Record the move being made
        self.board[int(pick_move[0])] = 'X'
        self.actionsX.append((state,int(pick_move[0])))
        self.current_player = 'O'

    def get_random_player_input(self):
        legal = []
        for i in self.board:
            if i in range(0,9):
                legal.append(i)
        move = random.choice(legal)
        self.board[move] = 'X'
        # End Turn
        self.current_player = 'O'

    def get_opponent_input(self):
        state = "".join(str(e) for e in self.board)
        if state not in self.policyO:
            # Create new fully random move policy based on available moves
            self.policyO[state] = []
            for count,elem in enumerate(self.board):
                # Create a blank slate for all legal moves
                if self.board[count] in range(0,9):
                    self.policyO[state].append(1)
                else:
                    self.policyO[state].append(0)
        move_prob = np.array(self.policyO[state][0:9])/float(sum(self.policyO[state][0:9]))
        pick_move = np.random.choice(9,1, p=move_prob)
        # Record the move being made
        self.board[int(pick_move[0])] = 'O'
        self.actionsO.append((state,int(pick_move[0])))
        self.current_player = 'X'

    def check_endgame(self):
        opponent = {'O':'X','X':'O'}
        for a,b,c in [(0,1,2), (3,4,5), (6,7,8),
                      (0,3,6), (1,4,7), (2,5,8),
                      (0,4,8), (2,4,6)]:
            if opponent[self.current_player] == self.board[a] == self.board[b] == self.board[c]:
                self.gameover = True
                if not LEARN:
                    print "Game over - Player", opponent[self.current_player], "wins!"
                    self.display_board();
                self.winner = opponent[self.current_player]
                return opponent[self.current_player]
        if self.turns >= 9:
            self.gameover = True
            if not LEARN:
                self.display_board();
                print "Game over - board is full!"

    def learn(self):
        if self.winner == 'O':
            result = 10
        elif self.winner == 'X':
            result = -10
        else:
            result = 1
        for i,b in enumerate(self.actionsO):
            # print self.policyO[b[0]][b[1]]
            multiplier = (i+1.0)/len(self.actionsO)
            self.policyO[b[0]][b[1]] += multiplier * result
            self.policyO[b[0]][b[1]] = max(self.policyO[b[0]][b[1]],0.01)
        # write policy json
        with open('policyO.dat', 'w') as outfile:
            json.dump(self.policyO, outfile)
            outfile.close();

        if LEARN:
            if(result != 1):
                result = -result
            for i,b in enumerate(self.actionsX):
                # print self.policyO[b[0]][b[1]]
                multiplier = (i+1.0)/len(self.actionsX)
                self.policyX[b[0]][b[1]] += multiplier * result
                self.policyX[b[0]][b[1]] = max(self.policyX[b[0]][b[1]],0.01)
            with open('policyX.dat', 'w') as outfile:
                json.dump(self.policyX, outfile)
                outfile.close();

game = Game()

# Learning Mode
if LEARN:
    plays = 0
    winrate = {'X':0,'O':0,"T":0}
    while plays < 10000:
        plays += 1
        if plays % 100 == 0:
            print plays
        while not game.gameover:
            game.get_ai_player_input();
            game.turns += 1;
            game.check_endgame();
            if game.winner is None and game.turns < 9:
                game.get_opponent_input();
                game.turns += 1;
                game.check_endgame();
        game.learn();
        if game.winner is None:
            winrate["T"] += 1
        else:
            winrate[game.winner] += 1
        if plays % 100 == 0:
            print "X:", winrate["X"], "O:", winrate["O"], "T:", winrate["T"], "O%:", 100*float(winrate["O"])/plays
        game = Game();
else:
    while not game.gameover:
        game.display_board();
        game.get_player_input();
        game.turns += 1;
        game.check_endgame();
        if game.winner is None and game.turns < 9:
            game.get_opponent_input();
            game.turns += 1;
            game.check_endgame();
    game.learn();
