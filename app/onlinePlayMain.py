import json
import os
import random
import bottle
import threading
import time
from onlineGameMaker import createNewGame
from LearningEnvironment import *
from LearningMain import *
from trainingDummys import *

from api import ping_response, start_response, move_response, end_response

#Flags for what kind of network we are training
sizeType = 19

#Main learning
envi = Snekgame(max_board_size=sizeType)
envi.init_just_win_aggresive()

#Training Dummys
envi0 = Snekgame(max_board_size=sizeType)
envi0.init_wholesome_pp()

comm = threadComms()


#Game parsing 
learningGame = None
learningSnakeID  = None


@bottle.route('/')
def index():
    return '''

    Battlesnake documentation can be found at

       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>. This snake is ##SNAKE_PERSONALITY_INSERT_HERE##, its created with reinforcement learning algorithms powered by tensorflow, keras and keras-rl. :3

    '''


@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.
    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    return ping_response()

@bottle.post('/start')
def start():
    global learningGame
    global learningSnakeID
    data = bottle.request.json
    color = "#00FF00"
    #If we are currently not learning a game
    if learningGame == None and learningSnakeID == None:
        learningGame = data["game"]["id"]
        learningSnakeID = data["you"]["id"]
    return start_response(color)


@bottle.post('/move')
def move():
    global learningGame
    global learningSnakeID
    global envi
    data = bottle.request.json
    if learningGame == data["game"]["id"] and learningSnakeID == data["you"]["id"]:
        envi.sendNewData(data)
        move = None
        counter = 0 
        while move == None and counter < 9000:
            move = envi.getMove()
            time.sleep(0.0001)
            counter += 1
        if counter >= 9000:
            move = 'left'
    else:
        comm.giveNewData(data)
        sendMove = None
        while sendMove == None:
            sendMove = comm.getNewMove()
        move = sendMove
    return move_response(move)


@bottle.post('/end')
def end():
    global learningGame
    global learningSnakeID
    data = bottle.request.json
    won = False
    snakeNames = []
    for snake in data["board"]["snakes"]:
        snakeNames.append(snake["name"])
    if len(data["board"]["snakes"]) == 1 and ("legless lizzard" in snakeNames or "0" in snakeNames):
        won = True
    envi.endEnvi(won)
    if learningGame == data["game"]["id"] and learningSnakeID == data["you"]["id"]:
        learningGame = None
        learningSnakeID = None
        createNewGame()
    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    threading.Thread(target=bottle.run, kwargs=dict(
        app=application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '80'),
        debug=os.getenv('DEBUG', False),
        quiet=True
        )
    ).start()
    threading.Thread(target=startLearning, kwargs=dict(
        Env=envi, max_board_size=sizeType, loadFileNumber=0)
    ).start()
    threading.Thread(target=startDummy, kwargs=dict(
        env = envi0,
        Comm = comm,
        tryHard = True
        )
    ).start()