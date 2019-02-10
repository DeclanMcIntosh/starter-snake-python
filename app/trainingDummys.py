import numpy as np
import gym
from os import environ
import glob
from random import randint, choice
import random
import time

#force keras to use cpu
#environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
environ["CUDA_VISIBLE_DEVICES"] = "1"

import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam, nadam
from rl.agents.dqn import DQNAgent
from rl.agents.sarsa import SARSAAgent
from rl.agents.cem  import CEMAgent

from rl.policy import BoltzmannQPolicy
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory
max_board_size = 19
previousNumSnakes = 0
previousHP = 0
num_proximity_flags = 8
num_health_flags = 1
## Board Encoding defintion 
noGo           = 1.0
empty          = 0
food           = -0.25
ourHead        = -1
bodyNorth      = 0.7
bodySouth      = 0.6
bodyEast       = 0.5
bodyWest       = 0.4
headZeroHP     = 0.8 # 0.8 <= head <= 0.9
headMaxHP      = 0.9 # 0HP --------> max_health
## Board Encoding definition

class player():
    def __init__(self, Env, max_board_size=7, memoryAllocation=800000, newObservation = False, data = None, moveChosen = None):

        self.env = Env
        nb_actions = self.env.action_space.n


        layer0Size = 256
        layer1Size = 128
        layer2Size = 64
        layer3Size = 64
        layer4Size = 32
        layer5Size = 16

        # Next, we build a very simple model. 
        model = Sequential()
        model.add(Flatten(input_shape=(1,) + self.env.observation_space.shape))
        model.add(Dense(layer0Size))
        model.add(Activation('relu'))
        model.add(Dense(layer1Size))
        model.add(Activation('relu'))
        model.add(Dense(layer2Size))
        model.add(Activation('relu'))
        model.add(Dense(layer3Size))
        model.add(Activation('relu'))
        model.add(Dense(layer4Size))
        model.add(Activation('relu'))
        model.add(Dense(layer5Size))
        model.add(Activation('relu'))
        model.add(Dense(nb_actions))
        model.add(Activation('linear'))


        #A little diagnosis of the model summary
        print(model.summary())

        # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
        # even the metrics!
        memory = SequentialMemory(limit=memoryAllocation, window_length=1)
        policy = BoltzmannQPolicy()
        self.dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, policy=policy, enable_dueling_network=True)
        self.dqn.compile(nadam(lr=0.001), metrics=['mae']) 

        self.loadFromFile()

        #Load Previous training 

        #Start traing
        # Ctrl + C.
        # We train and store 
        
    def getMove(self, data):
        #self.env.sendNewData(data=data)
        observation, notUsed, currSafeMoves = self.env.findObservation(data=data)
        action = self.dqn.forward(observation)
        if action == 0 and 'left' in currSafeMoves and len(currSafeMoves) > 0:
            moveChosen = 'left' 
        if action == 1 and 'left' in currSafeMoves and len(currSafeMoves) > 0:
            moveChosen = 'right' 
        if action == 2 and 'left' in currSafeMoves and len(currSafeMoves) > 0:
            moveChosen = 'up' 
        if action == 3 and 'left' in currSafeMoves and len(currSafeMoves) > 0:
            moveChosen = 'down' 
        if moveChosen == None and len(currSafeMoves) > 0:
            moveChosen = choice(currSafeMoves)
        if moveChosen == None:
            moveChosen = 'left'
        return moveChosen


    def loadFromFile(self):
        '''
        attempts to load agent random files untill an appropriate file is found
        '''
        files = glob.glob("*.h5f")
        try:
            self.dqn.load_weights(random.choice(files))
        except: 
            print("Invalid file re-trying")
            self.loadFromFile()
