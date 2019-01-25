import numpy as np
import gym

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
from rl.agents.dqn import DQNAgent

from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

ENV_NAME = 'CartPole-v0' #TODO remove

# Get the environment and extract the number of actions.
env = gym.make(ENV_NAME) #TODO change to our environement
np.random.seed(123) #TODO remove
env.seed(123) #TODO remove
nb_actions = env.action_space.n

# Next, we build a very simple model. #TODO make this a bigger boi of network, not absolute unit bit but bigger
model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape)) 
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(16))
model.add(Activation('relu'))
model.add(Dense(nb_actions))
model.add(Activation('linear'))

#A little diagnosis of the model summary
print(model.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,
               target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae']) #Adam is a really good optimizer from my reading so I think we can use this with possible edit of hyperparameters

#Start traing
# Ctrl + C.
dqn.fit(env, nb_steps=50000, visualize=True, verbose=2)

# After training is done, we save the final weights.
dqn.save_weights('dqn_SNEK_ALPHA_weights.h5f', overwrite=True)

# Finally, evaluate our algorithm for 5 episodes.
dqn.test(env, nb_episodes=5, visualize=True)