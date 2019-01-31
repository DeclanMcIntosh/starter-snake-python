import numpy as np
import json
import glob, os
from random import randint

import gym
from gym import spaces
from gym.utils import seeding

max_board_size = 21
max_health = 100

class Snekgame(gym.Env):
    '''Snek environment for snek game snek
    '''
    def __init__(self):

        #Snake Decided Moved
        self.move = 'left'
        self.newMoveFlag = False
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
        self.previousReward = 0

        #Required OpenAi gym things
            #Define observation and action space sizes
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(shape=(19 * 19 + 1,), dtype=np.float32, low=self.boundsLower, high=self.boundsUpper)

    def seed(self, seed=None):
        #we will never use this this never gets used by the keras-rl but needs to exist.
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        
        self.newMoveFlag = True

        #TODO check what encoding is used by network to decode action
        self.move = 'Left' 


        while self.newJsonDataFlag == False:
            do = "Nothing, wait for new data..."
        
        data = self.JsonServerData
        board = data["board"]

        # A value where more positive is more good more negative is more bad, just a scalar
        reward = 0

        numSnakesAlive = len(board["snakes"])

        currentHP = data["you"]["health"]

        currentLength = len(data["you"]["body"])

        # if currentHP has increased, snake must have eaten
        if (currentHP > self.previousHP):
            reward += self.eatReward
        
        # if number of snakes alive has decreased, a snake must have died (either directly
        # through this snake's actions, or through the butterfly effect)
        if (numSnakesAlive < self.previousNumSnakes):
            reward += self.killReward
        
        board_state = np.zeros((max_board_size, max_board_size)) # numpy array of size we defined for self.observation_space 

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
        self.fillSnakeBodySegments(board_state, self.ourHead, data["you"]["body"])

        # Fill food locations
        for xy_pair in board["food"]:
            if (board_state[xy_pair["x"], xy_pair["y"]] == 0):
                board_state[xy_pair["x"], xy_pair["y"]] = self.food
            # else:
            #     raise ValueError('Food occurred in place where something already exists!')

        observation = "TODO" # flatten board_state matrix, and add HP flag

        done = "TODO" #True or false for the environement has terminated

        #TODO Manually kill snake if it runs into a no-go area

        #Update previous state variables
        self.previousHP = currentHP
        self.previousNumSnakes = numSnakesAlive
        self.previousReward = reward

        #Reset Flag
        self.newJsonDataFlag = False

            # we return an observation of the state after action is taken
            # a reward for the action just taken, and 
            # a bool of if the episode is over
            # optionally we can include a dict of other diagnostics we may care about...
        return observation, reward, done, {"needs" : "to be done"}

    def reset(self):
        while self.newJsonDataFlag == False:
            do = "Nothing, wait for new data..."
        observation = "TODO"
        return observation

    def sendNewData(self, data):
        self.JsonServerData = data
        self.newJsonDataFlag = True

    def getMove(self):
        if self.newMoveFlag:
            return self.move
            self.newMoveFlag = False
        else:
            return None

    def fillSnakeBodySegments(self, board_state, head_val, whole_snake):
        # get location of head
        head_location = whole_snake["body"][0]
        body_prev_x = head_location["x"]
        body_prev_y = head_location["y"]

        # encode head position
        board_state[body_prev_x, body_prev_y] = head_val

        # encode rest of body into board, where each body segment points to 
        # the direction of the previous body segment
        for i in range(1, len(whole_snake["body"])):
            body_x = whole_snake["body"][i]["x"]
            body_y = whole_snake["body"][i]["y"]

            # keep in mind, x is used to index the row number (increasing x means moving south), 
            # and y is used to index column number (increasing y means moving east)
            #  y-> 0 1 ... n
            # x:  ___________
            # 0   |         |
            # 1   |         |
            # ... |         |
            # n   |         |
            #     -----------
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

    # all around good boi. everyone's favourite
    def init_wholesome_boi(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = -0.1
        self.killReward         = 10
        self.winReward          = 250
        ## Reward definitions
    
    # that snek who's just a bit better :/
    def init_wholesome_pp(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = 0
        self.eatReward          = 0
        self.killReward         = 10
        self.winReward          = 250
        ## Reward definitions

    # might want to lay off the food. is the snek that makes people in elevators glance at snek capacity limit
    def init_absolute_unit(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = 5
        self.killReward         = 1
        self.winReward          = 250
        ## Reward definitions

    # name's snek, james snek. has licence to kill. 2/10; avoid encounters if possible
    def init_danger_noodle(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = 0
        self.killReward         = 30
        self.winReward          = 250
        ## Reward definitions

    # wholesome but just better fed
    def init_well_fed(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = 1
        self.killReward         = 10
        self.winReward          = 250
        ## Reward definitions
    
    # addicted to caffeine. needs to calm down asap
    def init_hyper_snek(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.5
        self.eatReward          = 0
        self.killReward         = 0
        self.winReward          = 250
        ## Reward definitions
    
    # cries when someone eats anything that used to be living. including plants.
    def init_pacifist(self):
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = 1
        self.eatReward          = 1
        self.killReward         = -1
        self.winReward          = 250
        ## Reward definitions
    
    # legend says this snek is still running away. no one knows from what.
    def init_scaredy_snek(self):
        ## Reward definitions
        self.dieReward          = -500
        self.didNothingReward   = 0
        self.eatReward          = 0
        self.killReward         = 0
        self.winReward          = 250
        ## Reward definitions
    
    # everyone who has run across this snek is dead. RUN.
    def init_six_pool(self):
        ## Reward definitions
        self.dieReward          = -100
        self.didNothingReward   = 0
        self.eatReward          = 0
        self.killReward         = 150
        self.winReward          = 100
        ## Reward definitions