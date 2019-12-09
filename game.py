import sys
import pygame
import pygame.rect
import os
import random
from tkinter import messagebox
import tkinter as tk
import time


current_path = os.path.dirname(__file__)
whitePawn = pygame.transform.scale(pygame.image.load(os.path.join(current_path, 'whitePawn.png')), (200, 200))
blackPawn = pygame.transform.scale(pygame.image.load(os.path.join(current_path, 'blackPawn.png')), (200, 200))

def isValid(row, col):
    return row >= 0 and row < 3 and col >= 0 and col < 3

class Move:
    def __init__(self, moveFrom, moveTo):
        self.moveFrom = moveFrom
        self.moveTo = moveTo
    def __eq__(self, other):
        return self.moveFrom == other.moveFrom and self.moveTo == other.moveTo
    def __repr__(self):
        return str(self.moveFrom) + ' ' + str(self.moveTo)
class Pawn:
    def __init__(self, white):
        self.white = white
class Game:
    def __init__(self):
        self.board = [[None] * 3 for _ in range(3)]
        self.clickedRow = -1
        self.clickedCol = -1
        self.turn = True # True for human, False for AI
        for i in range(3):
            self.board[0][i] = Pawn(False)
            self.board[1][1] = None
            self.board[2][i] = Pawn(True)
    def getAllMoves(self, player):
        allMoves = []
        for row in range(3):
            for col in range(3):
                p = self.board[row][col]
                if p is not None and p.white == player:
                    r = row - 1
                    if not player:
                        r = row + 1
                    for c in range(col - 1, col + 2):
                        if isValid(r, c):
                            otherPiece = self.board[r][c]
                            if c == col and otherPiece is None:
                                allMoves += [Move((row, col), (r, c))]
                            elif c != col and otherPiece is not None and otherPiece.white != player:
                                allMoves += [Move((row, col), (r, c))]
        return allMoves
    def executeMove(self, move, player):
        if move is None:
            return None
        elif move in self.getAllMoves(player):
            self.board[move.moveTo[0]][move.moveTo[1]] = self.board[move.moveFrom[0]][move.moveFrom[1]]
            self.board[move.moveFrom[0]][move.moveFrom[1]] = None
            g.turn = not(g.turn)
            return True
        else:
            return False
    def getWinner(self): #returns True if human won, False if AI won and None if game is not yet finished
        for c in range(3):
            p = self.board[0][c]
            if p is not None and p.white is True:
                return True
            p = self.board[2][c]
            if p is not None and p.white is False:
                return False
        if len(self.getAllMoves(self.turn)) == 0:
            return not(self.turn)
        else:
            return None
        
class AI:
    def __init__(self):
        self.hashes = ('0x26f3', '0x25bb', '0x1e11', '0xd9d', '0x1f08', '0x244a', '0xbfd', '0xd41', '0x1da9',
                       '0xc08', '0xc18', '0x1e62', '0x453', '0x1c5f', '0xa56', '0x1b1b', '0x46e', '0xac2', 
                       '0x1b36')
        self.aiFile = open(os.path.join(current_path, 'trained_ai.txt'), 'r')
        self.lastMove = []
    def ternaryToHex(self, ternary):
        dec = 0
        index = 0
        for c in reversed(ternary):
            dec += int(c)*(3**index)
            index += 1
        return hex(dec)
    def mirroredTernary(self, ternary):
        mirroredTernary = ''
        for i in range(3):
            mirroredTernary += ternary[3*i + 2] + ternary[3*i + 1] + ternary[3*i]
        return mirroredTernary
    def getAllMovesFromTernary(self, ternary):
        allMoves = []
        b = [[None]* 3 for _ in range(3)]
        for row in range(3):
            for col in range(3):
                i = row*3 + col
                b[row][col] = int(ternary[i])
        for row in range(3):
            for col in range(3):
                if b[row][col] == 1:
                    r = row + 1
                    for c in range(col-1, col+2):
                        if isValid(r, c):
                            if (c == col and b[r][c] == 0) or (c != col and b[r][c] == 2):
                                allMoves += [Move((row, col), (r, c))]
        return allMoves
    def mirrorMove(self, move):
        def mirror(n):
            return -(n-1)+1
        f = move.moveFrom
        t = move.moveTo
        return Move((f[0], mirror(f[1])), (t[0], mirror(t[1])))
    def getSmartMove(self, hexa, ternary):
        allMoves = self.getAllMovesFromTernary(ternary)
        if len(allMoves) == 0:
            return None
        row = self.hashes.index(hexa)
        while row > 0:
            next(self.aiFile)
            row -= 1
        line = next(self.aiFile)
        self.aiFile.seek(0)
        moveIndex = random.randint(0,12)%len(allMoves)
        while line[moveIndex] == '0':
            moveIndex = random.randint(0,12)%len(allMoves)
        self.lastMove = [hexa, moveIndex]
        return allMoves[moveIndex]
    def learn(self):
        self.aiFile = open(os.path.join(current_path, 'trained_ai.txt'), 'r')
        string = ''
        row = self.hashes.index(self.lastMove[0])
        while row > 0:
            string += next(self.aiFile)
            row -= 1
        line = next(self.aiFile)
        for i in range(len(line)):
            if i == self.lastMove[1]:
                string += '0'
            else:
                string += line[i]
        for line in self.aiFile:
            string += line
        self.aiFile = open(os.path.join(current_path, 'trained_ai.txt'), 'w')
        self.aiFile.write(string)
        self.aiFile.close()
    def getMove(self, ternary):
        hexa = self.ternaryToHex(ternary)
        if hexa in self.hashes:
            return self.getSmartMove(hexa, ternary)
        ternary = self.mirroredTernary(ternary)
        mirrorHexa = self.ternaryToHex(ternary)
        if mirrorHexa in self.hashes:
            return self.mirrorMove(self.getSmartMove(mirrorHexa, ternary))
        return None
        
        

def drawBoard(pygame, display, game):
    pygame.draw.rect(display, (245,230,191), pygame.Rect(0,0,600,600))
    pygame.draw.rect(display, (102,68,58), pygame.Rect(0,200,200,200))
    pygame.draw.rect(display, (102,68,58), pygame.Rect(200,0,200,200))
    pygame.draw.rect(display, (102,68,58), pygame.Rect(200,400,200,200))
    pygame.draw.rect(display, (102,68,58), pygame.Rect(400,200,200,200))
    b = game.board
    if game.clickedRow != -1 and game.clickedCol != -1:
        pygame.draw.rect(display, (255,0,0), pygame.Rect(game.clickedCol*200,game.clickedRow*200,200,200), 4)
    for row in range(3):
        for col in range(3):
            p = b[row][col]
            if p is not None:
                if p.white:
                    display.blit(whitePawn, (col*200,row*200,100,100))
                else:
                    display.blit(blackPawn, (col*200,row*200,100,100))
if __name__ == '__main__':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init() # pylint: disable=maybe-no-member
    screen = pygame.display.set_mode([600,600])
    pygame.display.set_caption('hexapawn')
    g = Game()
    ai = AI()
    running = True # our variable to control the loop.
    winner = None
    while running:
        drawBoard(pygame, screen, g)
        pygame.display.update()
        if winner == None:
            winner = g.getWinner()
            if winner != None:
                root = tk.Tk()
                root.withdraw()
                if winner == True:
                    ai.learn()
                    messagebox.showinfo("hexapawn", "Human Wins")
                else:
                    messagebox.showinfo("hexapawn", "AI Wins")
            elif g.turn == False: # time for AI move
                ternary = '' # encode board state for AI
                for row in range(3):
                    for col in range(3):
                        p = g.board[row][col]
                        if p == None:
                            ternary += '0'
                        elif p.white == False:
                            ternary += '1'
                        else:
                            ternary += '2'
                if g.executeMove(ai.getMove(ternary), False) == None:
                    winner = True
                time.sleep(0.4)
        for event in pygame.event.get():
            # time for Human move
            if g.turn and winner == None and event.type == pygame.MOUSEBUTTONUP: #pylint:disable=maybe-no-member
                pos = pygame.mouse.get_pos()
                newCol, newRow = pos[0] // 200, pos[1] // 200
                if g.clickedCol == -1 and g.clickedRow == -1:
                    g.clickedCol, g.clickedRow = newCol, newRow
                elif g.clickedCol == newCol and g.clickedRow == newRow:
                    g.clickedCol, g.clickedRow = -1, -1
                else:
                    g.executeMove(Move((g.clickedRow, g.clickedCol), (newRow, newCol)), g.turn)
                    g.clickedCol, g.clickedRow = -1, -1
            elif event.type == pygame.QUIT: # pylint: disable=maybe-no-member
                running = False # break the loop
                pygame.quit() # pylint: disable=maybe-no-member
                sys.exit()
                quit()