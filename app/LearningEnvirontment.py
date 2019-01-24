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

        self.boundsUpper = 1
        self.boundsLower = -1

        #Required OpenAi gym things
            #a like size defintion for the action space, observationspace are required.
        self.action_space = spaces.Box(shape=(4,), dtype=np.float32, low=-1, high=1)
        self.observation_space = spaces.Box(shape=(17*17,), dtype=np.float32, low=self.boundsLower, high=self.boundsUpper)


    def seed(self, seed=None):
        #we will never use this this never gets used by the keras-rl but needs to exist.
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        oberservatioin = "TODO" # numpy array of size we defiend for self.obeservation_space 
        reward = "TODO" # A value where more positive is more good more negative is more bad, just a scalar
        done = "TODO" #True or false for the environement has terminated


            # we return an observation of the state after action is taken
            # a reward for the action just taken, and 
            # a bool of if the episode is over
            # optionally we can include a dict of other diagnostics we may care about...
        return oberservation, reward, done, {"needs" : "to be done"}

    def reset(self):
        observation = "TODO"
        # terminates the episode and starts a new episode, returns the first observation of that new episode as a np array.
        return observation
