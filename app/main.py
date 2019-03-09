# Designed for ofline (local) self-play with a training dummy,

import json
import os
import random
import bottle
import threading
import time
from LearningEnvironment import *
from LearningMain import *

from api import ping_response, start_response, move_response, end_response

#Flags for what kind of network we are training
boardSizeType = 19

envi = Snekgame(max_board_size=boardSizeType)
envi.init_just_win_aggresive()


@bottle.route('/')
def index():
    return '''

    Battlesnake documentation can be found at

       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>. 
       This snake is Kevin. 
       It's created with reinforcement learning algorithms powered by tensorflow, keras and keras-rl.
       :3

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
    color = "#00FF00"
    return start_response(color)


@bottle.post('/move')
def move():
    global envi
    data = bottle.request.json
    if data != None:
        # Send new data to envrionment
        envi.sendNewData(data)
        move = None
        noMoveTimeoutCounter = 0 
        # Wait for network to generate move or timeout.
        while move == None and noMoveTimeoutCounter < 9000:
            move = envi.getMove()
            time.sleep(0.0001)
            noMoveTimeoutCounter += 1
        if move == None:
            move = "left"
        return move_response(move)
    return move_response("left")


@bottle.post('/end')
def end():
    data = bottle.request.json
    wonGame = False
    snakeNames = []
    for snake in data["board"]["snakes"]:
        snakeNames.append(snake["name"])
    # Check if we are in the list of snakes at the termination of the game, if so
    # we have won!
    if len(data["board"]["snakes"]) == 1 and ("legless lizzard" in snakeNames \
        or "0" in snakeNames or data["you"]["name"] in snakeNames):
        wonGame = True
    envi.endEnvi(wonGame)
    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    # Create server thread
    threading.Thread(target=bottle.run, kwargs=dict(
        app=application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', 'You would like that wouldent you'), # You need to supply a port forwarded port.
        debug=os.getenv('DEBUG', False),
        quiet=True
        )
    ).start()
    # Create keras-rl management thread
    threading.Thread(target=startLearning, kwargs=dict(
        Env=envi, max_board_size=boardSizeType, loadFileNumber=23)
    ).start()