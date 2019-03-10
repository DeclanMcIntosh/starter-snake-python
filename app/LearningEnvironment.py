"""LearningEnvironment.py: TODO Description of what LearningEnvironment.py does."""

__author__ = "Declan McIntosh, Robert Lee, Luke Evans"
__copyright__ = "Copyright 2019"
__license__ = "MIT"
__version__ = "1.0"

import numpy as np
import json
import glob
import os
from random import randint, choice
import time
from onlineGameMaker import *
import gym
from gym import spaces
from gym.utils import seeding

#Variables for diagnostic document

max_board_size = 20
max_health = 100
num_proximity_flags = 8
num_health_flags = 1
viewsize = 25 # OLD VERSION FOR DEEP NETWORK -> 29 # must be odd
centerpoint = 19 # must be odd

class Snekgame(gym.Env):
    ''' Snake Game Class

    Configure definitions and parameters for learning environment
    '''
    def __init__(self, max_board_size=7):
        self.emptySpaceFloodFill = -1
        self.emptySpaceFloodFillCounted = -2

        self.currentGame = ""
        self.currentSnake = ""

        # statistics
        self.wins = 0
        self.loses = 0
        self.totalSteps = 0
        self.averageFoodEaten = 0
        self.lastGameLength = 0
        self.wonQuestionMark = False
        self.onlineEnabled = False
        self.diag_food = 0

        self.max_board_size=max_board_size

        #Snake Move Decision
        self.move = 'left'
        self.newMoveFlag = False
        self.gameOverFlag = False
        self.currSafeMoves = []
        self.headButtSafeMoves = []
        self.winFlag = False
        #Snake Move Decision

        # Initialize reward values
        self.init_wholesome_boi()

        ## Board Encoding definition 
        self.noGo           = -1.0
        self.empty          = 1.0
        self.food           = -0.2
        self.ourHead        = 0
        self.bodyNorth      = 0.2
        self.bodySouth      = 0.2
        self.bodyEast       = 0.2
        self.bodyWest       = 0.2
        self.headZeroHP     = 0.5
        self.headMaxHP      = 0.5
        ## Board Encoding definition

        self.boundsUpper = 1
        self.boundsLower = -1

        #Json data from server
        self.JsonServerData = None
        self.newJsonDataFlag = False

        #Previous state variables
        # previousHP used to determine whether snake has eaten
        self.previousHP = max_health + 1    
        self.previousNumSnakes = -1     #used to determine whether other snake has died

        #Required OpenAi gym things
            #Define observation and action space sizes
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(shape=((viewsize * viewsize) + num_health_flags + \
            num_proximity_flags,), dtype=np.float32, low=self.boundsLower, high=self.boundsUpper)

    def seed(self, seed=None):
        # This never gets used by the keras-rl but needs to exist
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):

        self.totalSteps += 1

        if action == 0:
            self.move = 'left' 
        if action == 1:
            self.move = 'right' 
        if action == 2:
            self.move = 'up' 
        if action == 3:
            self.move = 'down' 
        
        badMove = False
        if self.move not in self.currSafeMoves and len(self.currSafeMoves) > 0:
            self.move = choice(self.currSafeMoves)
            badMove = True

        if self.move not in self.headButtSafeMoves and len(self.headButtSafeMoves) > 0:
            self.move = choice(self.headButtSafeMoves)
            badMove = True

        #Let other thread know a new move is avalible 
        self.newMoveFlag = True

        #Wait for new board state
        startWaitTime = time.time()
        while self.newJsonDataFlag == False and self.gameOverFlag == False:
            time.sleep(0.01)
            if time.time()-startWaitTime > 5 and self.onlineEnabled and self.JsonServerData != None:
                self.gameOverFlag = True 
                self.winFlag = False
                self.currentGame = ""
                self.currentSnake = ""
                break

        #Reset Flag
        self.newJsonDataFlag = False
        observation, reward, self.currSafeMoves, self.headButtSafeMoves = self.findObservation(self.JsonServerData)

        if badMove:
            reward = -2

        if self.gameOverFlag and self.winFlag:
            reward = self.winReward + 3*int(self.JsonServerData["turn"])
            self.wins += 1
        
        if self.gameOverFlag and self.winFlag == False:
            reward = self.dieReward
            self.loses += 1

            # we return an observation of the state after action is taken
            # a reward for the action just taken, an16
            # a bool of if the episode is over
            # optionally we can include a dict of other diagnostics we may care about...

        #TODO in return
        return observation, reward, self.gameOverFlag, {"needs" : "to be done"} 

    def reset(self):

        self.winFlag = False
        self.gameOverFlag = False
        self.gameLengthAvg = (self.totalSteps/ (self.wins + self.loses + 1))
        self.averageFoodEaten = (self.diag_food/ (self.wins + self.loses + 1))
        print("")
        print("Wins: <" + str(self.wins) + "> Losses: <" + str(self.loses) + "> Avg Game Len: <" + str(self.gameLengthAvg) + "> Avf Food Ate: <" + str(self.averageFoodEaten) + "> Win Rate: <" + str(self.wins * 100 / (self.wins + self.loses + 1)) + ">")

        self.setCurrentGameParams("", "")
        if self.onlineEnabled:
            createNewGame()
        startWaitTime = time.time()
        while self.newJsonDataFlag == False:
            time.sleep(0.01)
            # LOCUP NOT HERE print("wating for new game")
            if time.time() - startWaitTime > 5 and self.onlineEnabled:
                self.setCurrentGameParams("", "")
                createNewGame()
                startWaitTime = time.time()

        self.newJsonDataFlag = False
        observation, reward, self.currSafeMoves, unused = self.findObservation(self.JsonServerData)
 
        return observation

    def badHeadButtFilter(self, boardState, safeMoves, head_x, head_y):
        """ Filter out bad headbutt moves.

        The neural network has issues avoiding instant-death headbutt moves.
        @param the boardState array, an array of known safe moves, and the head location. 
        @return a list of moves that are both:
                (a) known to be safe and (b) can never be a headbutt with a larger snake.
        """
        boardsize = len(boardState)
        headbuttSafeMoves = []

        # compass directions on board
        w = 0  
        e = 0 
        ne = 0
        nw = 0
        n = 0 
        s = 0
        sw = 0
        se = 0
        # Ignore spaces outside the board array to avoid range issues
        if head_x - 2 >= 0:
            w = boardState[head_x-2, head_y]
        if (head_x - 1 >= 0) and (head_y - 1 >= 0):
            nw = boardState[head_x-1, head_y-1]
        if head_y - 2 >= 0:
            n = boardState[head_x, head_y-2]
        if (head_x + 1 < boardsize) and (head_y - 1 >= 0):
            ne = boardState[head_x+1, head_y-1]
        if (head_x + 2) < boardsize:
            e = boardState[head_x+2, head_y]
        if (head_x + 1 < boardsize) and (head_y + 1 < boardsize):
            se = boardState[head_x+1, head_y+1]
        if (head_y + 2) < boardsize:
            s = boardState[head_x, head_y+2]
        if (head_x - 1 >= 0) and (head_y + 1 < boardsize):
            sw = boardState[head_x-1, head_y+1]
        for move in safeMoves:
            if move == "up":
                if (n != self.headMaxHP) and (nw != self.headMaxHP) and (ne != self.headMaxHP):
                    headbuttSafeMoves.append("up")
            if move == "down":
                if (s != self.headMaxHP) and (sw != self.headMaxHP) and (se != self.headMaxHP):
                    headbuttSafeMoves.append("down")
            if move == "left":
                if (w != self.headMaxHP) and (nw != self.headMaxHP) and (sw != self.headMaxHP):
                    headbuttSafeMoves.append("left")
            if move == "right":
                if (e != self.headMaxHP) and (ne != self.headMaxHP) and (se != self.headMaxHP):
                     headbuttSafeMoves.append("right")
        return headbuttSafeMoves

    def findObservation(self, data):
        """ Parse "observation" data.
        @param: a dict of board state data from the JSON
        @return: the centred view "observation", total reward, and arrays of safeMoves, headButtSafeMoves, and noStuckMoves

        Performs the following:
            1. When the snake recieves a JSON, process into a boardState array
            2. Check for boardState changes that result in rewards
            3. Use the boardState array to produce a list of safe moves (ie. not instant death)
            4. Process the boardState into a centred view for the learning algorithm
            5. Call noStuckMoves to produce a list of moves that will not get the snake trapped
        """
        board = data["board"]
        rewardSet = False

        # A value where more positive is more good more negative is more bad, just a scalar
        reward = 0

        # Parse data for useful parameters
        numSnakesAlive = len(board["snakes"])
        currentHP = data["you"]["health"]
        currentLength = len(data["you"]["body"])

        # If currentHP has increased, snake must have eaten
        if (currentHP >= self.previousHP):
            reward += self.eatReward
            self.diag_food += 1
            rewardSet = True
        
        # If the number of snakes alive has decreased, a snake must have died 
        if (numSnakesAlive < self.previousNumSnakes):
            reward += self.killReward * (self.previousNumSnakes - numSnakesAlive)
            rewardSet = True
        
        # numpy array of size defined in self.observation_space 
        board_state = np.full((self.max_board_size, self.max_board_size), fill_value=self.empty, dtype=np.float32) 
        
        # Fill wall locations into the board
        for row in range(0, board["height"]):
            for col in range(board["width"], self.max_board_size):
                board_state[row,col] = self.noGo

        for row in range(board["height"], self.max_board_size):
            for col in range(0, self.max_board_size):
                board_state[row,col] = self.noGo

        tails = []

        # Fill enemy snakes into the board
        for enemy_snake in board["snakes"]:
            # Grab each enemy snake by the head
            enemy_length = len(enemy_snake["body"])

            # Calculate hp value to encode in head position
            enemy_head_val = self.headMaxHP

            # Smaller snakes are differentiated with negative head value
            if (enemy_length < currentLength):
                enemy_head_val *= -1

            # Fill enemy snake body segment locations into the board
            unused, enemy_head_x, enemy_head_y, enemy_tail_x, enemy_tail_y = self.fillSnakeBodySegments(board_state, enemy_head_val, enemy_snake)
            if (enemy_snake["body"][enemy_length - 1] != enemy_snake["body"][enemy_length - 2]):
                # If tail is not overlapping with its body
                tails.append((enemy_tail_x, enemy_tail_y))

        # Fill our snake into the board
        diedonWallFlag, head_x, head_y, tail_x, tail_y = self.fillSnakeBodySegments(board_state, self.ourHead, data["you"])

        # Fill food locations into the board
        for xy_pair in board["food"]:
            if (board_state[xy_pair["x"], xy_pair["y"]] == 0):
                board_state[xy_pair["x"], xy_pair["y"]] = self.food

        # Hold simple boolean flags on whether there is danger or food to the snake head's 
        # left, right, up, or down
        # Ordering of proximity_flags: [no-go Up, no-go Down, no-go Left, no-go Right, 
        #                               food Up, food Down, food Left, food Right]
        # IMPORTANT: our own tail is treated as safe move
        proximity_flags = np.append(np.ones(4), np.zeros(4))
        # Pre-make flags with no-go and no food
        safeMoves = []
        secondLastBodySegment = data["you"]["body"][currentLength - 2]
        tail = data["you"]["body"][currentLength - 1]
        if (head_x >= 0 and head_x < self.max_board_size and head_y >= 0 and head_y < self.max_board_size):
            # if snek is not dead
            noGo_index = 0
            food_index = 4
            if (head_y - 1) >= 0:
                board_value =  board_state[head_x, head_y - 1]
                # if up is not a wall
                if ((head_x,head_y - 1) == (tail_x, tail_y) and tail != secondLastBodySegment) or ((head_x,head_y - 1) in tails) or board_value == self.food or board_value == self.empty:
                    # if this is our own tail, food, empty, or other snake tails
                        proximity_flags[noGo_index] = self.empty
                        safeMoves.append('up')

                        proximity_flags[food_index] = (board_value == self.food) + 0
            
            if (head_y + 1) < self.max_board_size:
                board_value =  board_state[head_x, head_y + 1]
                # if down is not a wall
                if ((head_x, head_y + 1) == (tail_x, tail_y) and tail != secondLastBodySegment) or ((head_x, head_y + 1) in tails) or board_value == self.food or board_value == self.empty:
                    # if this is our own tail, food, empty, or other snake tails
                        proximity_flags[noGo_index + 1] = self.empty
                        safeMoves.append('down')

                        proximity_flags[food_index + 1] = (board_value == self.food) + 0

            if (head_x - 1) >= 0:
                board_value =  board_state[head_x - 1, head_y]
                # if left is not a wall
                if ((head_x - 1,head_y) == (tail_x, tail_y) and tail != secondLastBodySegment) or ((head_x - 1,head_y) in tails) or board_value == self.food or board_value == self.empty:
                    # if this is our own tail, food, empty, or other snake tails
                        proximity_flags[noGo_index + 2] = self.empty
                        safeMoves.append('left')

                        proximity_flags[food_index + 2] = (board_value == self.food) + 0

            if (head_x + 1) < self.max_board_size:
                board_value =  board_state[head_x + 1, head_y]
                # if right is not a wall
                if ((head_x + 1,head_y) == (tail_x, tail_y) and tail != secondLastBodySegment) or ((head_x + 1,head_y) in tails) or board_value == self.food or board_value == self.empty:
                    # if this is our own tail, food, empty, or other snake tails
                        proximity_flags[noGo_index + 3] = self.empty
                        safeMoves.append('right')

                        proximity_flags[food_index + 3] = (board_value == self.food) + 0
        
        
        # Generate a list of non-lethal-headbutt moves
        headButtSafeMoves = self.badHeadButtFilter(board_state, safeMoves, head_x, head_y)

        #Update previous state variables
        self.previousHP = currentHP
        self.previousNumSnakes = numSnakesAlive

        # If nothing has been done, do nothing reward
        if rewardSet == False:
            reward = self.didNothingReward

        # Flatten the output and place in a current hp value
        # Place centered
        if head_x < 0:
            head_x = 0
        if head_y < 0:
            head_y = 0

        # New Centered Observation for learning
        centeredView = np.full(shape=(37, 37), fill_value=self.noGo, dtype=np.float32)
        centeredViewFinal = np.full(shape=(viewsize, viewsize), fill_value=self.noGo, dtype=np.float32)
        observation = np.full(shape=((viewsize * viewsize) + num_health_flags + num_proximity_flags,), fill_value=self.noGo, dtype=np.float32)
        # Centre boardState on current head location
        centeredView[centerpoint - head_x - 1 : centerpoint - head_x + centerpoint - 1,centerpoint - head_y - 1 : centerpoint - head_y + centerpoint - 1] = board_state
        # Truncate centred view to limit input space for the learning algorithm
        centeredViewFinal=centeredView[centerpoint - int((viewsize - 1)/2) -1: centerpoint + int((viewsize - 1)/2),centerpoint - int((viewsize - 1)/2) -1: centerpoint + int((viewsize - 1)/2)]
        observation[0: viewsize * viewsize] = np.ndarray.flatten(centeredViewFinal)
        observation[viewsize * viewsize] = currentHP
        observation[viewsize * viewsize + 1: len(observation)] = proximity_flags

        # Create a list of moves that won't result in getting trapped
        noStuckMoves = self.getSafeDirections(safeMoves, data)

        return observation, reward, safeMoves, headButtSafeMoves, noStuckMoves
    
    def endEnvi(self, win):
        """ End environment and update flags for reward calculations
        """
        self.gameOverFlag = True
        self.winFlag = win

    def sendNewData(self, data):
        """ Pass JSON data from server

            @param: JSON data from the server, as a dict
            
            Update class data dict and new data flag
        """
        self.JsonServerData = data
        self.newJsonDataFlag = True

    def getMove(self):
        """ Initiates a new move

        Reset flag, call self.move
        """
        if self.newMoveFlag:
            self.newMoveFlag = False
            return self.move
        return None

    def fillSnakeBodySegments(self, board_state, head_val, whole_snake):
        """ Fill a given snake into a boardState

        @param: array of the board state, head value, dict of snake segments
        @return: flag if wall death occurred, xy values of snake head, arrays of x and y body segments
        """
        wallDeathFlag = False
        body_x = 0
        body_y = 0
        
        # If snake has no length, just abort
        if (len(whole_snake["body"]) == 0):
            return None

        # Get location of and fill snake head
        head_location = whole_snake["body"][0]
        body_prev_x = head_location["x"]
        body_prev_y = head_location["y"]
        if head_location["x"] < 0 or head_location["x"] >= self.max_board_size or head_location["y"] < 0 or head_location["y"] >= self.max_board_size:
                wallDeathFlag = True

        # Encode rest of body into board, where each body segment points to 
        # the direction of the previous body segment
        for i in range(1, len(whole_snake["body"])):
            body_x = whole_snake["body"][i]["x"]
            body_y = whole_snake["body"][i]["y"]

            # Keep in mind, x is used to index the row number (increasing x means moving south), 
            # and y is used to index column number (increasing y means moving east)
            #  y-> 0 1 ... n
            # x:  _____________
            # 0   |           |
            # 1   |           |
            # .   |           |
            # :   |           |
            # n   |           |
            #     -------------
            if (body_x == body_prev_x):
                # x value unchanged, so body segment must differ in y
                board_state[body_x, body_y] = \
                    self.bodyWest if (body_y > body_prev_y) else self.bodyEast
            else:
                # body segment must differ in x
                board_state[body_x,body_y] = \
                    self.bodyNorth if (body_x > body_prev_x) else self.bodySouth

            body_prev_x = body_x
            body_prev_y = body_y

        # Encode head position
        if head_location["x"] > 0 and head_location["x"] < self.max_board_size and head_location["y"] > 0 and head_location["y"] < self.max_board_size:
            board_state[head_location["x"], head_location["y"]] = head_val

        return wallDeathFlag, head_location["x"], head_location["y"], whole_snake["body"][len(whole_snake["body"]) - 1]["x"], whole_snake["body"][len(whole_snake["body"]) - 1]["y"]

    def start_flood_fill(self, matrix, start_x, start_y):
        """ Wrapper function to call recursive flood-fill algorithm
        Very rough heuristic to estimate if there is an exit for a particular move direction.
        1. Finds the number of empty or food spots in a particular direction that is enclosed by snake bodies.
        2. Determines if there is a body element on the edge of this area that will free up in a smaller number of
           moves than the total number of open/food spots found in part 1
        
        LIMITATIONS: does not account for dead ends, impossible to reach areas, and snake wrapping. This 
                     will not filter out dead ends where the opening spot will be impossible to reach as 
                     our own snake body will block it.
        @param  matrix      contains the board to which flood-fill is applied. This matrix is encoded as follows:
                            - Any food or empty spot is encoded as self.emptySpaceFloodFill
                            - Any snake is encoded with the number of spaces (ignoring eating) left until
                              that particular board location frees up. (i.e., tail is 0, as the space will free up
                              during this move. Head is encoded as length-of-snake - 1, as it will take that many steps 
                              until the space frees up)
        @param  start_x     the x-coordinate where flood-fill is used
        @param  start_y     the y-coordinate where flood-fill is used
        @return             Returns true if there is a potential opening, false otherwise
        """
        accumulator, smallest_exit = self.flood_fill(matrix, start_x, start_y, accumulator=0, smallest_exit=100)
        return accumulator > smallest_exit

    def flood_fill(self, matrix, x, y, accumulator, smallest_exit):
        """ 
        Recursive function that implements flood-fill to determine whether there is a possible exit 
        for a particular move direction. See `start_flood_fill` for more detailed implementation description

        @param  matrix    contains the board to which flood-fill is applied. This matrix is encoded as follows:
                            - Any food or empty spot is encoded as self.emptySpaceFloodFill
                            - Any snake is encoded with the number of spaces (ignoring eating) left until
                              that particular board location frees up. (i.e., tail is 0, as the space will free up
                              during this move. Head is encoded as length-of-snake - 1, as it will take that many steps 
                              until the space frees up)
        @param  x               the x-coordinate where flood-fill is used
        @param  y               the y-coordinate where flood-fill is used
        @param  accumulator     current number of empty/food spaces counted
        @param  smallest_exit   smallest exit on perimeter of flood-fill space
        @return accumulator     new accumulator value
        @return smallest_exit   new smallest exit value
        """
        if (accumulator > smallest_exit) or accumulator > self.max_board_size*self.max_board_size:
            # stop recursion when number of empty/food spaces surpasses the smallest exit on perimeter
            return accumulator, smallest_exit

        # get value of board at (x,y)
        val = matrix[x][y]
        
        if (val == self.emptySpaceFloodFill):
            # if this space has not been encountered before

            # flag it as encountered
            matrix[x][y] = self.emptySpaceFloodFillCounted 
            # add to accumulator
            accumulator += 1

            if x > 0: 
                # check x-1 direction
                accumulator, smallest_exit = self.flood_fill(matrix, x-1, y, accumulator, smallest_exit)
            if x < len(matrix[y]) - 1:
                # check x+1 direction
                accumulator, smallest_exit = self.flood_fill(matrix, x+1, y, accumulator, smallest_exit)
            if y > 0:
                # check y-1 direction
                accumulator, smallest_exit = self.flood_fill(matrix, x, y-1, accumulator, smallest_exit)
            if y < len(matrix) - 1:
                # check y+1 direction
                accumulator, smallest_exit = self.flood_fill(matrix, x, y+1, accumulator, smallest_exit)
            
        elif val > self.emptySpaceFloodFill and val < smallest_exit:
            # if this is a snake body part and is smaller than the smallest perimeter value 
            # encountered so far, update smallest perimeter value 
            smallest_exit = val
        
        return accumulator, smallest_exit

    def setCurrentGameParams(self, currentGame, currentSnake):
        self.currentGame = currentGame
        self.currentSnake = currentSnake

    def getCurrentGame(self):
        return self.currentGame

    def getCurrentSnake(self):
        return self.currentSnake

    # Basic reward structure
    def init_wholesome_boi(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = -0.1
        self.killReward         = 10
        self.winReward          = 250
        self.diedOnWallReward   = -250
        ## Reward definitions

    # Adjusted optimized reward structure
    def init_just_win_aggresive(self):
        ## Reward definitions
        self.dieReward          = -10
        self.didNothingReward   = -0.5
        self.eatReward          = 50
        self.killReward         = 0
        self.winReward          = 50
        self.diedOnWallReward   = -10
        ## Reward definitions

    def enableOnline(self, state):
        self.onlineEnabled = state

    def getSafeDirections(self, safeMoves, data):
        boardMap = [[self.emptySpaceFloodFill for col in range(0,data["board"]["height"])] for row in range(0,data["board"]["height"])]
        if data != None:
            for snake in data["board"]["snakes"]:
                count = 1
                for element in snake["body"]:
                    if boardMap[element['x']][element['y']] < len(snake["body"]) - count:
                        boardMap[element['x']][element['y']] = len(snake["body"]) - count
                    count+=1
            noStuckMoves = []
            headPos = data["you"]["body"][0]
            head_x = headPos['x']
            head_y = headPos['y']
            if 'left' in safeMoves:
                if self.start_flood_fill(boardMap, head_x-1, head_y):
                    noStuckMoves.append('left')
            if 'right' in safeMoves:
                if self.start_flood_fill(boardMap, head_x+1, head_y):
                    noStuckMoves.append('right')
            if 'up' in safeMoves:
                if self.start_flood_fill(boardMap, head_x, head_y-1):
                    noStuckMoves.append('up')
            if 'down' in safeMoves:
                if self.start_flood_fill(boardMap, head_x, head_y+1):
                    noStuckMoves.append('down')
            return noStuckMoves
        else: 
            return safeMoves