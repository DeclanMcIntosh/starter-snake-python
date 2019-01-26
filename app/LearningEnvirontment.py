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
        #Snake Decided Moved

        ## Reward definitions
        self.dieReward = -250
        self.didNothingReward = -0.1
        self.eatReward = -0.1
        self.killReward = 10
        self.winReward = 250
        ## Reard definitions

        ## Board Encoding defintion 
        self.noGo = 1.0
        self.empty = 0
        self.food=-0.25
        self.ourHead = -1
        self.bodyNorth = 0.7
        self.bodySouth = 0.6
        self.bodyEast = 0.5
        self.bodyWest = 0.4
        ## Board Encoding definition

        self.boundsUpper = 1
        self.boundsLower = -1

        #Json data from server
        self.JsonSeverData = None
        self.newJsonDataFlag = False

        #Required OpenAi gym things
            #Define observation and action space sizes
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(shape=(19 * 19 + 1,), dtype=np.float32, low=self.boundsLower, high=self.boundsUpper)

    def seed(self, seed=None):
        #we will never use this this never gets used by the keras-rl but needs to exist.
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        
        while self.newJsonDataFlag == False:
            do = "Nothing, wait for new data..."
        
        #TODO do the stuff here after we have new data
        observation = "TODO" # numpy array of size we defiend for self.obeservation_space 
        reward = "TODO" # A value where more positive is more good more negative is more bad, just a scalar
        done = "TODO" #True or false for the environement has terminated

        #Reset Flag
        self.newJsonDataFlag = False

            # we return an observation of the state after action is taken
            # a reward for the action just taken, and 
            # a bool of if the episode is over
            # optionally we can include a dict of other diagnostics we may care about...
        return observation, reward, done, {"needs" : "to be done"}

    def reset(self):
        observation = "TODO"
        # terminates the episode and starts a new episode, returns the first observation of that new episode as a np array.
        return observation

    def sendNewData(self, data):
        self.JsonSeverData = data
        self.newJsonDataFlag = True

    def getMove(self):
        return 'left'
