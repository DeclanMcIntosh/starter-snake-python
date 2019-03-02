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

#Variables for diagnostic document

max_board_size = 20
max_health = 100
num_proximity_flags = 8
num_health_flags = 1
viewsize = 25# OLD VERSION FOR DEEP NETWORK -> 29 # must be odd
centerpoint = 19 # must be odd

class Snekgame(gym.Env):
    '''Snek environment for snek game snek
    '''
    def __init__(self, max_board_size=7):
        self.emptySpaceFloodFill = -1
        self.emptySpaceFloodFillCounted = -2
        self.diag_moves = 0
        self.diag_food = 0
        self.diag_kills = 0
        self.diag_snakes = 0
        self.diag_wl = 0
        self.csv_string = ""
        self.diag_id = ""
        self.currentGame = ""
        self.currentSnake = ""
        #stats
        self.wins = 0
        self.loses = 0
        self.totalSteps = 0
        self.averageFoodEaten = 0
        self.lastGameLength = 0
        self.wonQuestionMark = False
        self.onlineEnabled = False

        self.max_board_size=max_board_size
        #Diagnostic File
        self.diag = open("diagnostic.csv", "a+")
        #Snake Decided Moved
        self.move = 'left'
        self.newMoveFlag = False
        self.gameOverFlag = False
        self.currSafeMoves = []
        self.headButtSafeMoves = []
        self.winFlag = False
        #Snake Decided Moved

        # Initialize reward values
        self.init_wholesome_boi()

        ## Board Encoding defintion 
        #self.noGo           = 0
        #self.empty          = 1.0
        #self.food           = -0.4
        #self.ourHead        = -1
        #self.bodyNorth      = 0.7
        #self.bodySouth      = 0.6
        #self.bodyEast       = 0.5
        #self.bodyWest       = 0.4
        #self.headZeroHP     = 0.8 # 0.8 <= head <= 0.9
        #self.headMaxHP      = 0.9 # 0HP --------> max_health
        ## Board Encoding definition

        ## Board Encoding defintion 
        self.noGo           = -1.0
        self.empty          = 1.0
        self.food           = -0.2
        self.ourHead        = 0
        self.bodyNorth      = 0.2 #0.7
        self.bodySouth      = 0.2 #0.6
        self.bodyEast       = 0.2 #0.5
        self.bodyWest       = 0.2 #0.4
        self.headZeroHP     = 0.5  #0.9 # 0.8 <= head <= 0.9 headZeroHp < HeadMaxHP
        self.headMaxHP      = 0.5  #0.9 # 0HP --------> max_health
        ## Board Encoding definition

        self.boundsUpper = 1
        self.boundsLower = -1

        #Json data from server
        self.JsonServerData = None
        self.newJsonDataFlag = False

        #Previous state variables
        self.previousHP = max_health + 1      #used to determine whether snake has eaten
        self.previousNumSnakes = -1     #used to determine whether other snake has died

        #Required OpenAi gym things
            #Define observation and action space sizes
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(shape=((viewsize * viewsize) + num_health_flags + \
            num_proximity_flags,), dtype=np.float32, low=self.boundsLower, high=self.boundsUpper)

    def seed(self, seed=None):
        #we will never use this this never gets used by the keras-rl but needs to exist.
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        #print("step")
        self.totalSteps += 1

        self.diag_moves += 1
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

        print(noStuckMoves)

        if self.move not in noStuckMoves and len(noStuckMoves) > 0:
            self.move = choice(noStuckMoves)

        if self.move not in self.headButtSafeMoves and len(self.headButtSafeMoves) > 0:
            self.move = choice(self.headButtSafeMoves)
            badMove = True
        #print("Filtered Move " + self.move)
        #print(self.currSafeMoves)
        #Let other thread know a new move is avalible 
        self.newMoveFlag = True

        #Wait for new board state
        startWaitTime = time.time()
        while self.newJsonDataFlag == False and self.gameOverFlag == False:
            time.sleep(0.01)
            # LOCKUP NOT HERE print("waiting for new data")
            if time.time()-startWaitTime > 5 and self.onlineEnabled and self.JsonServerData != None:
                self.gameOverFlag = True 
                self.winFlag = False
                self.currentGame = ""
                self.currentSnake = ""
                break
        #print("got JSON for step")
        #Reset Flag
        self.newJsonDataFlag = False
        observation, reward, self.currSafeMoves, self.headButtSafeMoves = self.findObservation(self.JsonServerData)
        #print("found observation")
        if badMove:
            reward = -2

        if self.gameOverFlag and self.winFlag:
            reward = self.winReward + 3*int(self.JsonServerData["turn"])
            self.diag_wl += 1
            self.wins += 1
        
        if self.gameOverFlag and self.winFlag == False:
            reward = self.dieReward
            self.loses += 1

            # we return an observation of the state after action is taken
            # a reward for the action just taken, an16
            # a bool of if the episode is over
            # optionally we can include a dict of other diagnostics we may care about...
        #print("end step")
        #print(" ")
        #
        #print(reward)
        return observation, reward, self.gameOverFlag, {"needs" : "to be done"}

    def reset(self):
        #print(" ")
        #print("start reset")
        self.winFlag = False
        self.gameOverFlag = False
        self.gameLengthAvg = (self.totalSteps/ (self.wins + self.loses + 1))
        self.averageFoodEaten = (self.diag_food/ (self.wins + self.loses + 1))
        print("")
        print("Wins: <" + str(self.wins) + "> Losses: <" + str(self.loses) + "> Avg Game Len: <" + str(self.gameLengthAvg) + "> Avf Food Ate: <" + str(self.averageFoodEaten) + "> Win Rate: <" + str(self.wins * 100 / (self.wins + self.loses + 1)) + ">")  
        self.diag.write(self.diag_id + "," + str(self.diag_food) + "," + str(self.diag_snakes) + "," + str(self.diag_wl) + "," + str(self.diag_kills) + "," + str(self.diag_moves) + ",")

        self.diag_moves = 0
        self.diag_id = ""
        self.diag_kills = 0
        self.diag_snakes = 0
        self.diag_wl = 0
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
        #print("got json data for reset")
        self.newJsonDataFlag = False
        observation, reward, self.currSafeMoves, unused = self.findObservation(self.JsonServerData)
        #if self.wins > 0 or self.loses > 0:
        #    print("    Wins: " + str(self.wins) + "   Losses: " + str(self.loses) + "  Win %: " + str(100 * self.wins/(self.wins+ self.loses)) + "%")
        #print("end reset")

        self.diag_id = self.JsonServerData["game"]["id"]
        self.diag_snakes = len(self.JsonServerData["board"]["snakes"])
        #print("reset recived data")
        return observation

    def headonheadfilter(self, boardstate, safeMoves, head_x, head_y):
        boardsize = len(boardstate)
        headbuttSaveMoves = []
        w = 0  
        e = 0 
        ne = 0
        nw = 0
        n = 0 
        s = 0
        sw = 0
        se = 0
        if head_x - 2 >= 0:
            w = boardstate[head_x-2, head_y]
        if (head_x - 1 >= 0) and (head_y - 1 >= 0):
            nw = boardstate[head_x-1, head_y-1]
        if head_y - 2 >= 0:
            n = boardstate[head_x, head_y-2]
        if (head_x + 1 < boardsize) and (head_y - 1 >= 0):
            ne = boardstate[head_x+1, head_y-1]
        if (head_x + 2) < boardsize:
            e = boardstate[head_x+2, head_y]
        if (head_x + 1 < boardsize) and (head_y + 1 < boardsize):
            se = boardstate[head_x+1, head_y+1]
        if (head_y + 2) < boardsize:
            s = boardstate[head_x, head_y+2]
        if (head_x - 1 >= 0) and (head_y + 1 < boardsize):
            sw = boardstate[head_x-1, head_y+1]
        for move in safeMoves:
            if move == "up":
                if (n != self.headMaxHP) and (nw != self.headMaxHP) and (ne != self.headMaxHP):
                    headbuttSaveMoves.append("up")
            if move == "down":
                if (s != self.headMaxHP) and (sw != self.headMaxHP) and (se != self.headMaxHP):
                    headbuttSaveMoves.append("down")
            if move == "left":
                if (w != self.headMaxHP) and (nw != self.headMaxHP) and (sw != self.headMaxHP):
                    headbuttSaveMoves.append("left")
            if move == "right":
                if (e != self.headMaxHP) and (ne != self.headMaxHP) and (se != self.headMaxHP):
                     headbuttSaveMoves.append("right")

        return headbuttSaveMoves

    def findObservation(self, data):
        board = data["board"]
        rewardSet = False

        # A value where more positive is more good more negative is more bad, just a scalar
        reward = 0

        numSnakesAlive = len(board["snakes"])
        

        currentHP = data["you"]["health"]

        currentLength = len(data["you"]["body"])

        # if currentHP has increased, snake must have eaten
        if (currentHP >= self.previousHP):
            reward = self.eatReward
            self.diag_food += 1
            rewardSet = True
        
        # if number of snakes alive has decreased, a snake must have died (either directly
        # through this snake's actions, or through the butterfly effect)
        if (numSnakesAlive < self.previousNumSnakes):
            reward = self.killReward * (self.previousNumSnakes - numSnakesAlive)
            #print("killed")
            self.diag_kills += 1
            rewardSet = True
        
        board_state = np.full((self.max_board_size, self.max_board_size), fill_value=self.empty, dtype=np.float32) # numpy array of size we defined for self.observation_space 
        
        # Fill wall locations
        for row in range(0, board["height"]):
            for col in range(board["width"], self.max_board_size):
                board_state[row,col] = self.noGo

        for row in range(board["height"], self.max_board_size):
            for col in range(0, self.max_board_size):
                board_state[row,col] = self.noGo

        tails = []
        # Fill enemy snake body segment locations
        for enemy_snake in board["snakes"]:
            # grab each enemy snake (by the head)

            enemy_health = enemy_snake["health"]
            enemy_length = len(enemy_snake["body"])

            # calculate hp value to encode in head position
            enemy_head_val = self.headMaxHP

            if (enemy_length < currentLength):
                enemy_head_val *= -1

            # Fill enemy snake body segment locations
            unused, enemy_head_x, enemy_head_y, enemy_tail_x, enemy_tail_y = self.fillSnakeBodySegments(board_state, enemy_head_val, enemy_snake)
            if (enemy_snake["body"][enemy_length - 1] != enemy_snake["body"][enemy_length - 2]):
                # If tail is not overlapping with its body
                tails.append((enemy_tail_x, enemy_tail_y))

        # Fill our snake body segment locations
        diedOnWallFlag, head_x, head_y, tail_x, tail_y = self.fillSnakeBodySegments(board_state, self.ourHead, data["you"])

        # Fill food locations
        for xy_pair in board["food"]:
            if (board_state[xy_pair["x"], xy_pair["y"]] == 0):
                board_state[xy_pair["x"], xy_pair["y"]] = self.food
            # else:
            #     raise ValueError('Food occurred in place where something already exists!')

        # Hold simple boolean flags on whether there is danger or food to the snake head's 
        # left, right, up, or down
        # Ordering of proximity_flags: [no-go Up, no-go Down, no-go Left, no-go Right, 
        #                               food Up, food Down, food Left, food Right]
        # IMPORTANT: our own tail is treated as safe move
        proximity_flags = np.append(np.ones(4), np.zeros(4))
        # pre-make flags with no-go and no food
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
                if ((head_x,head_y + 1) == (tail_x, tail_y) and tail != secondLastBodySegment) or ((head_x,head_y + 1) in tails) or board_value == self.food or board_value == self.empty:
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
            
        headButtSafeMoves = self.headonheadfilter(board_state, safeMoves, head_x, head_y)
        #Update previous state variables
        self.previousHP = currentHP
        self.previousNumSnakes = numSnakesAlive

        #If nothing has been done, do nothing reward
        if rewardSet == False:
            reward = self.didNothingReward

        #Flatten the output and place in a current hp value
        #Place centered
        if head_x < 0:
            head_x = 0
        if head_y < 0:
            head_y = 0

        #New Centered Observation
        centeredView = np.full(shape=(37, 37), fill_value=self.noGo, dtype=np.float32)
        centeredViewFinal = np.full(shape=(viewsize, viewsize), fill_value=self.noGo, dtype=np.float32)
        observation = np.full(shape=((viewsize * viewsize) + num_health_flags + num_proximity_flags,), fill_value=self.noGo, dtype=np.float32)
        centeredView[centerpoint - head_x -1 : centerpoint - head_x + centerpoint - 1,centerpoint - head_y - 1 : centerpoint - head_y + centerpoint - 1] = board_state
        centeredViewFinal=centeredView[centerpoint - int((viewsize - 1)/2) -1: centerpoint + int((viewsize - 1)/2),centerpoint - int((viewsize - 1)/2) -1: centerpoint + int((viewsize - 1)/2)]
        observation[0: viewsize * viewsize] = np.ndarray.flatten(centeredViewFinal)
        observation[viewsize * viewsize] = currentHP
        observation[viewsize * viewsize + 1: len(observation)] = proximity_flags

        noStuckMoves = self.getSafeDirections(safeMoves, data)
        # Old observation

        #observation = np.full(shape=((self.max_board_size * self.max_board_size) + num_health_flags + num_proximity_flags,), fill_value=self.noGo, dtype=np.float32)
        #observation[0:(self.max_board_size * self.max_board_size)] = np.ndarray.flatten(board_state)
        #observation[(self.max_board_size * self.max_board_size)] = currentHP
        #observation[self.max_board_size * self.max_board_size + 1: len(observation)] = proximity_flags
        return observation, reward, safeMoves, headButtSafeMoves, noStuckMoves
    
    def endEnvi(self, win):
        self.gameOverFlag = True
        self.winFlag = win

    def sendNewData(self, data):
        self.JsonServerData = data
        self.newJsonDataFlag = True

    def getMove(self):
        if self.newMoveFlag:
            self.newMoveFlag = False
            return self.move
        return None

    def fillSnakeBodySegments(self, board_state, head_val, whole_snake):
        wallDeathFlag = False
        body_x = 0
        body_y = 0
        if (len(whole_snake["body"]) == 0):
            return None

        # get location of head
        head_location = whole_snake["body"][0]
        body_prev_x = head_location["x"]
        body_prev_y = head_location["y"]
        if head_location["x"] < 0 or head_location["x"] >= self.max_board_size or head_location["y"] < 0 or head_location["y"] >= self.max_board_size:
                wallDeathFlag = True

        # encode rest of body into board, where each body segment points to 
        # the direction of the previous body segment
        for i in range(1, len(whole_snake["body"])):
            body_x = whole_snake["body"][i]["x"]
            body_y = whole_snake["body"][i]["y"]

            # keep in mind, x is used to index the row number (increasing x means moving south), 
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

        # encode head position
        if head_location["x"] > 0 and head_location["x"] < self.max_board_size and head_location["y"] > 0 and head_location["y"] < self.max_board_size:
            board_state[head_location["x"], head_location["y"]] = head_val

        return wallDeathFlag, head_location["x"], head_location["y"], whole_snake["body"][len(whole_snake["body"]) - 1]["x"], whole_snake["body"][len(whole_snake["body"]) - 1]["y"]

    def start_flood_fill(self, matrix, start_x, start_y):
        accumulator, smallest_exit = self.flood_fill(matrix, start_x, start_y, 0, max_board_size*max_board_size)

        return accumulator > smallest_exit

    # body_part value must be greater than empty
    # food is not greater than empty
    def flood_fill(self, matrix, x, y, accumulator, smallest_exit):
        if (accumulator > smallest_exit):
            return accumulator, smallest_exit

        val = matrix[x,y]
        
        if (val == self.emptySpaceFloodFill or val == self.emptySpaceFloodFillCounted):
            if (val == self.emptySpaceFloodFill):
                matrix[x,y] = self.emptySpaceFloodFillCounted
                accumulator += 1

            if x > 0:
                accumulator, smallest_exit = self.flood_fill(matrix, x-1, y, accumulator, smallest_exit)
            if x < len(matrix[y]) - 1:
                accumulator, smallest_exit = self.flood_fill(matrix, x+1, y, accumulator, smallest_exit)
            if y > 0:
                accumulator, smallest_exit = self.flood_fill(matrix, x, y-1, accumulator, smallest_exit)
            if y < len(matrix) - 1:
                accumulator, smallest_exit = self.flood_fill(matrix, x, y+1, accumulator, smallest_exit)
            
        elif val > self.emptySpaceFloodFill and val < smallest_exit:
            smallest_exit = val
        
        return accumulator, smallest_exit

    def setCurrentGameParams(self, currentGame, currentSnake):
        self.currentGame = currentGame
        self.currentSnake = currentSnake

    def getCurrentGame(self):
        return self.currentGame

    def getCurrentSnake(self):
        return self.currentSnake

    # all around good boi. everyone's favourite
    def init_wholesome_boi(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = -0.1
        self.killReward         = 10
        self.winReward          = 250
        self.diedOnWallReward   = -250
        ## Reward definitions
    
    # that snek who's just a bit better :/
    def init_wholesome_pp(self):
        ## Reward definitions
        self.dieReward          = -100
        self.didNothingReward   = 5
        self.eatReward          = 5
        self.killReward         = 10
        self.winReward          = 250
        self.diedOnWallReward   = -100
        ## Reward definitions

    # might want to lay off the food. is the snek that makes people in elevators glance at snek capacity limit
    def init_absolute_unit(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = 5
        self.killReward         = 1
        self.winReward          = 250
        self.diedOnWallReward   = -250
        ## Reward definitions

    # name's snek, james snek. has licence to kill. 2/10; avoid encounters if possible
    def init_danger_noodle(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = 0
        self.killReward         = 30
        self.winReward          = 250
        self.diedOnWallReward   = -250
        ## Reward definitions

    # wholesome but just better fed
    def init_well_fed(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = 1
        self.killReward         = 10
        self.winReward          = 250
        self.diedOnWallReward   = -250
        ## Reward definitions
    
    # addicted to caffeine. needs to calm down asap
    def init_hyper_snek(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.5
        self.eatReward          = 0
        self.killReward         = 0
        self.winReward          = 250
        self.diedOnWallReward   = -250
        ## Reward definitions
    
    # cries when someone eats anything that used to be living. including plants.
    def init_pacifist(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = 1
        self.eatReward          = 1
        self.killReward         = -1
        self.winReward          = 250
        self.diedOnWallReward   = -250
        ## Reward definitions
    
    # legend says this snek is still running away. no one knows from what.
    def init_scaredy_snek(self):
        ## Reward definitions
        self.dieReward          = -500
        self.didNothingReward   = 0
        self.eatReward          = 0
        self.killReward         = 0
        self.winReward          = 250
        self.diedOnWallReward   = -500
        ## Reward definitions
    
    # everyone who has run across this snek is dead. RUN.
    def init_six_pool(self):
        ## Reward definitions
        self.dieReward          = -100
        self.didNothingReward   = 0
        self.eatReward          = 0
        self.killReward         = 150
        self.winReward          = 100
        self.diedOnWallReward   = -100
        ## Reward definitions

    def train_not_hit_walls(self):
        ## Reward definitions
        self.dieReward          = -100
        self.didNothingReward   = 5
        self.eatReward          = 5
        self.killReward         = 5
        self.winReward          = 250
        self.diedOnWallReward   = -100
        ## Reward definitions

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
        boardMap = [[]]
        if data != None:
            for x in range(0,len(data["board"]["height"])):
                for y in range(0,len(data["board"]["height"])):
                    boardMap[x][y] = data
            for snake in data["board"]["snakes"]:
                count = 1
                for element in snake["body"]:
                    boardMap[element['x']][element['y']] = len(snake["body"]) - 1
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