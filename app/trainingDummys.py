"""trainingDummys.py: Runs training dummys to play against main learning snake."""

__author__ = "Declan McIntosh, Robert Lee, Luke Evans"
__copyright__ = "Copyright 2019"
__license__ = "MIT"
__version__ = "1.0"

import numpy as np
import gym
from os import environ
import glob
from random import randint, choice
import random
import time

#Force keras to use GPU 2
environ["CUDA_VISIBLE_DEVICES"] = "1"

import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam, nadam
from rl.agents.dqn import DQNAgent
from rl.agents.sarsa import SARSAAgent
from rl.agents.cem  import CEMAgent
from keras.layers.advanced_activations import LeakyReLU

from rl.policy import BoltzmannQPolicy
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory
from rl.policy import GreedyQPolicy

max_board_size = 19

def startDummy(env, Comm, tryHard=False):
    
    nb_actions = env.action_space.n


    layer0Size = 4096
    layer1Size = 4096
    layer2Size = 4096
    layer3Size = 0
    layer4Size = 0
    layer5Size = 1

    # Next, we build a very simple model. 
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
    model.add(Dense(layer0Size))
    model.add(LeakyReLU(alpha=0.003))
    model.add(Dense(layer1Size))
    model.add(LeakyReLU(alpha=0.003))
    model.add(Dense(layer2Size))
    model.add(LeakyReLU(alpha=0.003))
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))

    #A little diagnosis of the model summary
    print(model.summary())

    # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
    # even the metrics!
    memory = SequentialMemory(limit=800000, window_length=1)
    policy = GreedyQPolicy()
    dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, policy=policy, enable_dueling_network=True)
    dqn.compile(nadam(lr=0.001), metrics=['mae']) 

    #Load Previous training 
    previousfileLength = 0
    #Start traing
    # Ctrl + C.
    # We train and store 
    load_file_number = 39
    loadFile = "Larger_Memeory_BOARDSIZE_" + str(max_board_size) + "_DQN_LAYERS_" + str(layer0Size) + "_" + str(layer1Size) + "_" + str(layer2Size) + "_" + str(layer3Size) + "_" + str(layer4Size) + "_" + str(layer5Size) +  "_SAVENUMBER_" + str(load_file_number) + ".h5f"
    dqn.load_weights(loadFile)
        
    while(True):
        data = None
        while data == None:
            data = Comm.getNewData()
        observation, notUsed, currSafeMoves, headButtSafeMoves, noStuckMoves, foodMoves = env.findObservation(data=data)
        action = dqn.forward(observation)
        if action == 0:
            moveChosen = 'left' 
        if action == 1:
            moveChosen = 'right' 
        if action == 2:
            moveChosen = 'up' 
        if action == 3:
            moveChosen = 'down' 
        if moveChosen not in currSafeMoves and len(currSafeMoves) > 0:
            moveChosen = choice(currSafeMoves)
        if moveChosen not in noStuckMoves and len(noStuckMoves) > 0:
            moveChosen = choice(noStuckMoves)
        if moveChosen not in headButtSafeMoves and len(headButtSafeMoves) > 0:
            moveChosen = choice(headButtSafeMoves)
        
        if moveChosen not in foodMoves and len(foodMoves) > 0:
            moveChosen = choice(foodMoves)


        Comm.giveNewMove(moveChosen)


def loadFromFile(dqn, tryhard, previousfileLength):
    '''
    Attempts to load agent random files untill an appropriate file is found
    '''
    files = glob.glob("*.h5f")
    files.sort()
    if tryhard == False:
        try:
            dqn.load_weights(random.choice(files))
            print("loaded new file!")
        except: 
            print("Invalid file re-trying")
            loadFromFile(dqn, tryhard, previousfileLength)
    if tryhard == True and len(files) > previousfileLength:
        dqn.load_weights(files[-1])
    return len(files)



class threadComms():
    def __init__(self):
        self.newMoveAvailibe = False
        self.newDataAvailible = False
        self.data = None
        self.move = None
        self.loadNewFileCommand = False

    def giveNewData(self, data):
        self.data = data
        self.newDataAvailible = True
    
    def getNewData(self):
        if self.newDataAvailible:
            self.newDataAvailible = False
            return self.data
        else:
            return None 
    
    def giveNewMove(self, move):
        self.move = move
        self.newMoveAvailibe = True

    def getNewMove(self):
        if self.newMoveAvailibe:
            self.newMoveAvailibe = False
            return self.move
        else:
            return None

    def assertLoadNewFile(self):
        self.loadNewFileCommand = True
    
    def unAssertLoadNewFile(self):
        self.loadNewFileCommand = False
    
    def checkLoadNewFileCommand(self):
        return self.loadNewFileCommand