import numpy as np
import json
import glob, os
from random import randint
import time
from cheekyRunGamesScript import *

import gym
from gym import spaces
from gym.utils import seeding

max_board_size = 20 # must be even
centerd_view_size = 10 # must be even
max_health = 100

class Snekgame(gym.Env):
    '''Snek environment for snek game snek
    '''
    def __init__(self):
        #Diagnostic File
        self.diag = open("diagnostic.txt", "a+")
        #Snake Decided Moved
        self.move = 'left'
        self.newMoveFlag = False
        self.gameOverFlag = False
        self.currSaveMoves = []
        #Snake Decided Moved

        # Initialize reward values
        self.init_wholesome_boi()

        ## Board Encoding defintion 
        self.noGo           = 1.0
        self.empty          = 0
        self.food           = -0.25
        self.ourHead        = -1
        self.bodyNorth      = 0.7
        self.bodySouth      = 0.6
        self.bodyEast       = 0.5
        self.bodyWest       = 0.4
        self.headZeroHP     = 0.8 # 0.8 <= head <= 0.9
        self.headMaxHP      = 0.9 # 0HP --------> max_health
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
        self.observation_space = spaces.Box(shape=((max_board_size * max_board_size) + (centerd_view_size * centerd_view_size) + 1,), dtype=np.float32, low=self.boundsLower, high=self.boundsUpper)

    def seed(self, seed=None):
        #we will never use this this never gets used by the keras-rl but needs to exist.
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        if action == 0:
            self.move = 'left' 
        if action == 1:
            self.move = 'right' 
        if action == 2:
            self.move = 'up' 
        if action == 3:
            self.move = 'down' 
        
        badMove = False
        if self.move not in self.currSaveMoves and len(self.currSaveMoves) > 0:
            self.move = random.choice(self.currSaveMoves)
            badMove = True
            
        #Let other thread know a new move is avalible 
        self.newMoveFlag = True

        #Wait for new board state
        while self.newJsonDataFlag == False:
            time.sleep(0.01)

        #print("step recived data")
        
        #print(self.JsonServerData["game"]["id"])
        observation, reward, self.currSaveMoves = self.findObservation(self.JsonServerData)

        if badMove:
            reward = self.diedOnWallReward

        #Reset Flag
        self.newJsonDataFlag = False

            # we return an observation of the state after action is taken
            # a reward for the action just taken, an16
            # a bool of if the episode is over
            # optionally we can include a dict of other diagnostics we may care about...
        return observation, reward, self.gameOverFlag, {"needs" : "to be done"}

    def reset(self):
        waitStartTime = time.time()
        while self.newJsonDataFlag == False:
            time.sleep(0.01)
            if time.time() - waitStartTime > 25:
                #runAGameForNoCollisionTraining()
                waitStartTime = time.time()
        self.gameOverFlag = False
        self.newJsonDataFlag = False
        observation, reward, self.currSaveMoves = self.findObservation(self.JsonServerData)
        #print("reset recived data")
        return observation

    def findObservation(self, data):
        board = data["board"]
        rewardSet = False

        # A value where more positive is more good more negative is more bad, just a scalar
        reward = 0

        numSnakesAlive = len(board["snakes"])

        currentHP = data["you"]["health"]

        currentLength = len(data["you"]["body"])

        # if currentHP has increased, snake must have eaten
        if (currentHP > self.previousHP):
            reward = self.eatReward
            rewardSet = True
        
        # if number of snakes alive has decreased, a snake must have died (either directly
        # through this snake's actions, or through the butterfly effect)
        if (numSnakesAlive < self.previousNumSnakes):
            reward = self.killReward
            rewardSet = True
        
        board_state = np.zeros((max_board_size, max_board_size), dtype=np.float32) # numpy array of size we defined for self.observation_space 
        outputBoard = np.full((max_board_size*2, max_board_size*2), self.noGo, dtype=np.float32)
        centeredView = np.full((centerd_view_size, centerd_view_size), self.noGo, dtype=np.float32)
        
        # Fill wall locations
        for row in range(0, board["height"]):
            for col in range(board["width"], max_board_size):
                board_state[row,col] = self.noGo

        for row in range(board["height"], max_board_size):
            for col in range(0, max_board_size):
                board_state[row,col] = self.noGo

        # Fill enemy snake body segment locations
        for enemy_snake in board["snakes"]:
            # grab each enemy snake (by the head)

            enemy_health = enemy_snake["health"]
            enemy_length = len(enemy_snake["body"])

            # calculate hp value to encode in head position
            enemy_head_val = enemy_health / max_health * (self.headMaxHP-self.headZeroHP) + self.headZeroHP

            if (enemy_length < currentLength):
                enemy_head_val *= -1

            # Fill enemy snake body segment locations
            self.fillSnakeBodySegments(board_state, enemy_head_val, enemy_snake)

        # Fill our snake body segment locations
        diedOnWallFlag, head_x, head_y = self.fillSnakeBodySegments(board_state, self.ourHead, data["you"])

        # Fill food locations
        for xy_pair in board["food"]:
            if (board_state[xy_pair["x"], xy_pair["y"]] == 0):
                board_state[xy_pair["x"], xy_pair["y"]] = self.food
            # else:
            #     raise ValueError('Food occurred in place where something already exists!')

        #Update previous state variables
        self.previousHP = currentHP
        self.previousNumSnakes = numSnakesAlive

        #If nothing has been done, do nothing reward
        if rewardSet == False:
            reward = self.didNothingReward

        #Check if the game has been won or lost, and adjust reward accordingly.
        #This only adds to the turns reward as if you killed someone it might be worth.
        if self.gameOverFlag == True:
            if self.winFlag == True:
                reward += self.winReward
            else: 
                if diedOnWallFlag:
                    reward += self.diedOnWallReward
                else:
                    reward += self.dieReward 

        #Flatten the output and place in a current hp value
        #Place centered
        startingNum = int(max_board_size)
        endingNum = int(max_board_size + max_board_size)
        if head_x < 0:
            head_x = 0
        if head_y < 0:
            head_y = 0
        outputBoard[startingNum - int(head_x) : endingNum - int(head_x), startingNum - int(head_y) : endingNum - int(head_y)] = board_state
        centeredView[0:int(centerd_view_size),0:int(centerd_view_size)] = outputBoard[int(max_board_size-centerd_view_size/2):int(max_board_size+centerd_view_size/2),int(max_board_size-centerd_view_size/2):int(max_board_size+centerd_view_size/2)]
        #Print the board to a diagnostic file currently not working, cuts off inside of the arrays
        #self.diag.write(np.array2string(board_state, max_line_width=10000))

        boardStateFlat = np.ndarray.flatten(board_state)
        boatCenteredFlat = np.ndarray.flatten(centeredView)

        observation = np.zeros(shape=((max_board_size * max_board_size)+(centerd_view_size * centerd_view_size)+1,), dtype=np.float32)
        observation[0:(max_board_size * max_board_size)] = boardStateFlat
        observation[(max_board_size * max_board_size):(max_board_size * max_board_size)+(centerd_view_size * centerd_view_size)] = boatCenteredFlat
        observation[(max_board_size * max_board_size)+(centerd_view_size * centerd_view_size)] = currentHP

        #print(centeredView)

        safeMoves = []
        center = int(centerd_view_size/2)
        if centeredView[center + 1][center] == self.empty or centeredView[center + 1][center] == self.food:
            safeMoves.append('right')
        if centeredView[center - 1][center] == self.empty or centeredView[center - 1][center] == self.food:
            safeMoves.append('left')
        if centeredView[center][center + 1] == self.empty or centeredView[center][center + 1] == self.food:
            safeMoves.append('down')
        if centeredView[center][center - 1] == self.empty or centeredView[center][center - 1] == self.food:
            safeMoves.append('up')
        return observation, reward, safeMoves

    def endEnvi(self, win):
        self.winFlag = win
        self.gameOverFlag = True

    def sendNewData(self, data):
        self.JsonServerData = data
        self.newJsonDataFlag = True

    def getMove(self):
        if self.newMoveFlag:
            self.newMoveFlag = False
            return self.move
        else:
            return None

    def fillSnakeBodySegments(self, board_state, head_val, whole_snake):
        wallDeathFlag = False
        if (len(whole_snake["body"]) == 0):
            return None

        # get location of head
        head_location = whole_snake["body"][0]
        body_prev_x = head_location["x"]
        body_prev_y = head_location["y"]
        if head_location["x"] < 0 or board_state[head_location["x"]][0] == -1 or head_location["y"] < 0 or board_state[0][head_location["y"]] == -1:
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
        board_state[head_location["x"], head_location["y"]] = head_val

        return wallDeathFlag, head_location["x"], head_location["y"]

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
        self.dieReward          = -250
        self.didNothingReward   = 0
        self.eatReward          = 0
        self.killReward         = 10
        self.winReward          = 250
        self.diedOnWallReward   = -250
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
        self.dieReward          = -50
        self.didNothingReward   = 10
        self.eatReward          = 10
        self.killReward         = 1
        self.winReward          = 250
        self.diedOnWallReward   = -25
        ## Reward definitions