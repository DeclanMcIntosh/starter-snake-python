import numpy as np
import gym

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam, nadam
from rl.agents.dqn import DQNAgent
from rl.agents.sarsa import SARSAAgent
from rl.agents.cem  import CEMAgent

from rl.policy import BoltzmannQPolicy
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

def startLearning(Env):
    # Get the environment and extract the number of actions.
    env = Env #gym.make(ENV_NAME) 
    nb_actions = env.action_space.n

    # Next, we build a very simple model. 
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape)) 
    #model.add(Dense(400))
    #model.add(Activation('relu'))
    model.add(Dense(256))
    model.add(Activation('relu'))
    #model.add(Dense(256))
    #model.add(Activation('relu'))
    model.add(Dense(128))
    model.add(Activation('relu'))
    #model.add(Dense(64))
    #model.add(Activation('relu'))
    model.add(Dense(32))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    #Load Previous training 
    model.load_weights(filepath="dqn_SNEK_ALPHA_NO_HIT_WALLS_weights_0_NotBrokenKeras2.1.6.h5f")


    #A little diagnosis of the model summary
    print(model.summary())

    # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
    # even the metrics!
    memory = SequentialMemory(limit=90000, window_length=1)
    policy = BoltzmannQPolicy()
    #policy = EpsGreedyQPolicy(eps=0.01)
    #dqn = SARSAAgent(model=model, nb_actions=nb_actions, policy=policy, nb_steps_warmup=1000)
    dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, policy=policy, enable_dueling_network=True)
    dqn.compile(nadam(lr=0.001), metrics=['mae']) 
    #Start traing
    # Ctrl + C.
    # We train and store 
    counter = 1
    while True:
        print("started fitting")
        dqn.fit(env, nb_steps=10000, visualize=False, verbose=1)
        dqn.save_weights('dqn_SNEK_ALPHA_NO_HIT_WALLS_weights_' + str(counter) + '_NotBrokenKeras2.1.6.h5f', overwrite=True)
        counter+=1

    # Finally, evaluate our algorithm for 5 episodes.
    #dqn.test(env, nb_episodes=5, visualize=True)