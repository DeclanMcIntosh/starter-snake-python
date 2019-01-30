import numpy as np
import json
import glob, os
from random import randint

import gym
from gym import spaces
from gym.utils import seeding



class Snekgame(gym.Env):
    '''Snek environement for snek game snek
    '''
    def __init__(self):

        #Snake Decided Moved
        self.move = 'left'
        self.newMoveFlag = False
        #Snake Decided Moved

        # Initialize reward values
        init_wholesole_boi()

        ## Board Encoding defintion 
        self.noGo = 1.0
        self.empty = 0
        self.food = -0.25
        self.ourHead = -1
        self.bodyNorth = 0.7
        self.bodySouth = 0.6
        self.bodyEast = 0.5
        self.bodyWest = 0.4
        ## Board Encoding definition

        self.boundsUpper = 1
        self.boundsLower = -1

        #Json data from server
        self.JsonServerData = None
        self.newJsonDataFlag = False

        #Previous state variables
        self.previousHP = 10000000      #used to determine whether snake has eaten
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

        reward = self.previousReward

        numSnakesAlive = len(board["snakes"])

        currentHP = data["you"]["health"]

        if (currentHP > self.previousHP)
            reward += self.eatReward
        
        if (numSnakesAlive < self.previousNumSnakes)
            reward += self.killReward
        
        #TODO do the stuff here after we have new data
        observation = "TODO" # numpy array of size we defiend for self.obeservation_space 
        reward = "TODO" # A value where more positive is more good more negative is more bad, just a scalar
        done = "TODO" #True or false for the environement has terminated

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

    # all around good boi. everyone's favourite
    def init_wholesome_boi() 
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = -0.1
        self.killReward         = 10
        self.winReward          = 250
        ## Reward definitions
    
    # that snek who's just a bit better :/
    def init_wholesome-pp() 
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = 0
        self.eatReward          = 0
        self.killReward         = 10
        self.winReward          = 250
        ## Reward definitions

    # might want to lay off the food. is the snek that makes people in elevators glance at snek capacity limit
    def init_absolute_unit() 
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = 5
        self.killReward         = 1
        self.winReward          = 250
        ## Reward definitions

    # name's snek, james snek. has licence to kill. 2/10; avoid encounters if possible
    def init_danger_noodle() 
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = 0
        self.killReward         = 30
        self.winReward          = 250
        ## Reward definitions

    # wholesome but just better fed
    def init_well_fed() 
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.1
        self.eatReward          = 1
        self.killReward         = 10
        self.winReward          = 250
        ## Reward definitions
    
    # addicted to caffeine. needs to calm down asap
    def init_hyper_snek() 
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = -0.5
        self.eatReward          = 0
        self.killReward         = 0
        self.winReward          = 250
        ## Reward definitions
    
    # cries when someone eats anything that used to be living. including plants.
    def init_pacifist()
        ## Reward definitions
        self.dieReward          = -250
        self.didNothingReward   = 1
        self.eatReward          = 1
        self.killReward         = -1
        self.winReward          = 250
        ## Reward definitions
    
    # legend says this snek is still running away. no one knows from what.
    def init_scaredy_snek()
        ## Reward definitions
        self.dieReward          = -500
        self.didNothingReward   = 0
        self.eatReward          = 0
        self.killReward         = 0
        self.winReward          = 250
        ## Reward definitions
    
    # everyone who has run across this snek is dead. RUN.
    def init_six_pool()
        ## Reward definitions
        self.dieReward          = -100
        self.didNothingReward   = 0
        self.eatReward          = 0
        self.killReward         = 150
        self.winReward          = 100
        ## Reward definitions