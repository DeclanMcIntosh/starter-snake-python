"""LearningMain.py: TODO Description of what this file does."""

__author__ = "Declan McIntosh, Robert Lee, Luke Evans"
__copyright__ = "Copyright 2019"
__license__ = "MIT"
__version__ = "1.0"

import numpy as np
import gym
from os import environ

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.layers.advanced_activations import LeakyReLU
from keras.optimizers import Adam, nadam
from rl.agents.cem  import CEMAgent
from rl.agents.dqn import DQNAgent
from rl.agents.sarsa import SARSAAgent

from rl.memory import SequentialMemory
from rl.policy import BoltzmannQPolicy
from rl.policy import EpsGreedyQPolicy
from rl.policy import GreedyQPolicy

def startLearning(Env, max_board_size=7, loadFileNumber=-1, gpuToUse=None, memoryAllocation=800000):
    # Set to use GPU explicitly
    if gpuToUse != None:
        environ["CUDA_VISIBLE_DEVICES"]=gpuToUse
    else:
        environ["CUDA_VISIBLE_DEVICES"]="0"

    env = Env
    nb_actions = env.action_space.n

    # Init size based on max_board_size
    if max_board_size not in [11, 7, 19]:
        raise EnvironmentError

    layer0Size = 4096
    layer1Size = 4096
    layer2Size = 4096
    layer3Size = 0
    layer4Size = 0
    layer5Size = 0

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

    # Finally, we configure and compile our agent.
    memory = SequentialMemory(limit=memoryAllocation, window_length=1)
    policy = BoltzmannQPolicy()
    dqn = DQNAgent(model=model, batch_size=32, nb_actions=nb_actions, memory=memory, policy=policy, enable_dueling_network=True, gamma=.97)
    dqn.compile(nadam(lr=0.01), metrics=['mae']) 


    # Here we load from a file an old agent save if specified.
    if loadFileNumber >= 0:
        loadFile = "Larger_Memeory_BOARDSIZE_" + str(max_board_size) + "_DQN_LAYERS_" + str(layer0Size) + "_" + str(layer1Size) + "_" + str(layer2Size) + "_" + str(layer3Size) + "_" + str(layer4Size) + "_" + str(layer5Size) +  "_SAVENUMBER_" + str(loadFileNumber) + ".h5f"
        dqn.load_weights(loadFile)

    saveFileNumberCounter = 0
    while True:
        dqn.fit(env, nb_steps=100010, visualize=False, verbose=1)
        saveFileNumberCounter+=1
        saveFile = "Larger_Memeory_BOARDSIZE_" + str(max_board_size) + "_DQN_LAYERS_" + str(layer0Size) + "_" + str(layer1Size) + "_" + str(layer2Size) + "_" + str(layer3Size) + "_" + str(layer4Size) + "_" + str(layer5Size) + "_SAVENUMBER_" + str(loadFileNumber + saveFileNumberCounter) + ".h5f"
        dqn.save_weights(saveFile, overwrite=True)