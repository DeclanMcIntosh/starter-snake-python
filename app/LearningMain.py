import numpy as np
import gym
from os import environ

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

def startLearning(Env, max_board_size=7, loadFileNumber=None, gpuToUse=None, memoryAllocation=800000):
    # Get the environment and extract the number of actions.
    if loadFileNumber != None:
        load_file_number = loadFileNumber #-1 loads no starting file
    else:
        load_file_number = -1
    # Set used GPU 
    if gpuToUse != None:
        environ["CUDA_VISIBLE_DEVICES"]=gpuToUse
    else:
        environ["CUDA_VISIBLE_DEVICES"]="0"


    env = Env
    nb_actions = env.action_space.n

    layer0Size = 0
    layer1Size = 0
    layer2Size = 0
    layer3Size = 0
    layer4Size = 0
    layer5Size = 0

    # Init size based on max_board_size
    if max_board_size not in [11, 7, 19]:
        raise EnvironmentError

    # 49 + 5 inputs
    if max_board_size == 7:
        layer0Size = 64
        layer1Size = 64
        layer2Size = 32
        layer3Size = 32
        layer4Size = 16
        layer5Size = 16

    # 121 + 5 inputs
    if max_board_size == 11:
        layer0Size = 128
        layer1Size = 64
        layer2Size = 64
        layer3Size = 32
        layer4Size = 32
        layer5Size = 16

    # 361 + 5 inputs
    if max_board_size == 19:
        layer0Size = 256
        layer1Size = 128
        layer2Size = 64
        layer3Size = 64
        layer4Size = 32
        layer5Size = 16

    # Next, we build a very simple model. 
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
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
    dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, policy=policy, enable_dueling_network=True)
    dqn.compile(nadam(lr=0.001), metrics=['mae']) 

    if load_file_number >= 0:
        loadFile = "BOARDSIZE_" + str(max_board_size) + "_DQN_LAYERS_" + str(layer0Size) + "_" + str(layer1Size) + "_" + str(layer2Size) + "_" + str(layer3Size) + "_" + str(layer4Size) + "_" + str(layer5Size) +  "_SAVENUMBER_" + str(load_file_number) + ".h5f"
        dqn.load_weights(loadFile)

    #Load Previous training 

    #Start traing
    # Ctrl + C.
    # We train and store 

    counter = 0
    while True:
        dqn.fit(env, nb_steps=10000, visualize=False, verbose=1)
        counter+=1
        saveFile = "BOARDSIZE_" + str(max_board_size) + "_DQN_LAYERS_" + str(layer0Size) + "_" + str(layer1Size) + "_" + str(layer2Size) + "_" + str(layer3Size) + "_" + str(layer4Size) + "_" + str(layer5Size) + "_SAVENUMBER_" + str(load_file_number + counter) + ".h5f"
        dqn.save_weights(saveFile, overwrite=True)


