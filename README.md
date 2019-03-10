# keras-rl Battle Snake

## Overview

## Learning Setup

### Training data gathering
This project used two main learning situations, the first was a self play system where the main learning agent would play against 1-7 instances of past versions of itself. This allowed the agent to train through a huge amount of data quickly with relatively poor data to start off with. 

The second source of training data was running the snake against other snakes people had made publicly available. This was the prefered data in our testing as we had little time before the tournament to train and this data allowed the snake to learn from pre-existing metas rather than be required to develop it's own. 

### Data Representation
The data into the network was a square view of the game board centered around our head. Enemy snake heads were encoded with their health and their relative length. We also passed the snakes current health, immediate food flags and immediate danger flags. All body parts were encoded as the same.

We chose to pass a centered view as this was found to significantly increase the learning rate over a static view of the board.

### Reward Scheme

## Low Level Filters

## Peformance

## Build instuctions

This project is no longer mainatined, if you would like to use it as a starting point for one of your projects please email me at battleSnakeInfo@declanmcintosh.com and I would love to help you get started and provide you with some of our pre-trained models.

## The Amazing Event Organizers!

Email [battlesnake@sendwithus.com](mailto:battlesnake@sendwithus.com), or tweet [@send_with_us](http://twitter.com/send_with_us).
