import random, copy, pygame, sys
from enum import Enum

# Implementation of 2048 game in Python



###################### Global variables ########################



squareLen = 100 # length (px) of one square's side in display

class Move(Enum):
    """Enumeration of all possible game moves"""
    up = 0
    down = 1
    left = 2
    right = 3

moveDict = {pygame.K_UP: Move.up, pygame.K_DOWN: Move.down, pygame.K_LEFT: Move.left, pygame.K_RIGHT: Move.right}  # map key events to moves

gameSize = 5  # 5x5 game



######################## Classes ###############################



class GameState(object):
    """2d array of all values in current game's state."""

    def __init__(self, size):
        self.size = size
        self.data = [[None for x in range(size)] for y in range(size)]  # 2d array, represents game state

    def drawTo(self, screen):
        """Draw state of game to screen."""
        screen.fill((119,110,101))
        font = pygame.font.Font(None, 60)  # create text font with size 60
        for y in range(self.size):
            for x in range(self.size):
                if self.getItem(x, y) == None: continue # if nothing, do not draw
                text = font.render(str(self.getItem(x, y)), 1, (249, 246, 242) if self.getItem(x, y) >= 8 else (119, 110, 101))
                # draw square of particular item to screen w/ 1 thick border
                tileRect = pygame.Rect(x*squareLen+1, y*squareLen+1, squareLen-2, squareLen-2)
                pygame.draw.rect(screen, self.getTileColor(self.getItem(x, y)), tileRect) 
                # Center text onto tile
                textRect = text.get_rect()
                textRect.centerx = tileRect.centerx
                textRect.centery = tileRect.centery
                screen.blit(text, textRect)  # blit number to respective square

    def __eq__(self, other):
        """Define equality between two game states."""
        if self.size != other.size:
            return False  # Automatically different if different sizes
        for y in range(self.size): 
            for x in range(self.size):
                if self.getItem(x, y) != other.getItem(x, y): return False  # If any items different, false
        return True  # If all other comparisons passed, are equal

    def getItem(self, x, y):
        assert (x in range(0, self.size) and y in range(0, self.size))
        return self.data[y][x]

    def setItem(self, x, y, newVal):
        assert (x in range(0, self.size) and y in range(0, self.size))
        self.data[y][x] = newVal

    def getTileColor(self, number):
        # Adapted from https://github.com/gabrielecirulli/2048/blob/master/style/main.css
        tileColorDict = {2: 'eee4da', 4: 'ede0c8', 8: 'f2b179', 16: 'f59563', 32: 'f59563', 64: 'f65e3b', 128: 'edcf72', 256: 'edcc61', 512: 'edc850', 1024: 'edc53f', 2048: 'edc22e', 'super': '3c3a32'}
        hexString = tileColorDict[number] if number in tileColorDict else tileColorDict['super']
        return (int(hexString[0:2], 16), int(hexString[2:4], 16), int(hexString[4:6], 16))



class GameSession(object):
    def __init__(self, size):
        self.gameState = GameState(size)
        self.isGameOver = False

    def drawTo(self, screen):
        self.gameState.drawTo(screen)

    def nextMove(self, move):
        """Advance game to next move."""
        self.moveAllItemsInDir(move)
        self.checkIfGameOver()
        state = self.gameState
        isFull = all([state.getItem(x,y)!=None for x in range(self.gameState.size) for y in range(self.gameState.size)])
        if not isFull: self.addNumToRandomPoint(2)

    def moveAllItemsInDir(self, move):
        """Move all items in a particular direction."""
        lastState = GameState(self.gameState.size)

        while not self.gameState == lastState:  # Keep trying to move each item until none can be moved
            # Loop through each item in list
            lastState = copy.deepcopy(self.gameState)
            for y in range(self.gameState.size):
                for x in range(self.gameState.size):
                    if self.gameState.getItem(x, y) == None: continue
                    #Decide which direction to move each item depending on move
                    if move == Move.up and y>0:
                        self.shiftOneItemTo([x, y], [x, y-1])
                    elif move == Move.down and y<self.gameState.size-1:
                        self.shiftOneItemTo([x, y], [x, y+1])
                    elif move == Move.left and x>0:
                        self.shiftOneItemTo([x, y], [x-1, y])
                    elif move == Move.right and x<self.gameState.size-1:
                        self.shiftOneItemTo([x, y], [x+1, y])

    def shiftOneItemTo(self, startCoords, endCoords):
        """Shift a specific item at startCoords to endCoords.
        If endCoords has an item identical to at startCoords, add the two together. If none at endcoords, shift to there. Else, do nothing."""
        startVal = self.gameState.getItem(startCoords[0], startCoords[1])
        endVal = self.gameState.getItem(endCoords[0], endCoords[1])

        if endVal == None:
            self.gameState.setItem(endCoords[0], endCoords[1], startVal)
        elif startVal == endVal:
            self.gameState.setItem(endCoords[0], endCoords[1], startVal+endVal)
        else:
            return None
        self.gameState.setItem(startCoords[0], startCoords[1], None)

    def addNumToRandomPoint(self, val):
        """Add new number with value 'val' to array in random location when move is done"""
        while True:  # Keep selecting random points until one with nothing in it is found
            x = random.randint(0, self.gameState.size-1)
            y = random.randint(0, self.gameState.size-1)
            if self.gameState.getItem(x, y) == None:
                self.gameState.setItem(x, y, val)
                break
            else: continue

    def checkIfGameOver(self):
        """Use to update whether game is over or not."""
        self.isGameOver = True
        isEmpty = all([self.gameState.getItem(x,y)==None for x in range(self.gameState.size) for y in range(self.gameState.size)])
        # check if any movements are possible, if not, game is over
        movLs = [Move.up, Move.down, Move.left, Move.right]
        gameMoves = [copy.deepcopy(self) for i in range(len(movLs))]
        for i in range(len(movLs)): gameMoves[i].moveAllItemsInDir(movLs[i])
        if isEmpty or not all([self.gameState == x.gameState for x in gameMoves]):
            self.isGameOver = False



########################## Main module #############################



def main():
    pygame.init()
    screen = pygame.display.set_mode((squareLen*gameSize, squareLen*gameSize))
    pygame.display.set_caption('2048')

    gameSession = GameSession(gameSize)

    while not gameSession.isGameOver:
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(0, 0, squareLen*gameSize, squareLen*gameSize))  # clear the screen with black
        gameSession.drawTo(screen)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key in moveDict.keys():
                gameSession.nextMove(moveDict[event.key])
            elif event.type == pygame.QUIT:
                sys.exit()

        pygame.display.flip()


if __name__ == "__main__":
    main()
