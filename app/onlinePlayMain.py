"""onlinePlayMain.py: Runs training games online"""

__author__ = "Declan McIntosh, Robert Lee, Luke Evans"
__copyright__ = "Copyright 2019"
__license__ = "MIT"
__version__ = "1.0"

import json
import os
import random
import bottle
import threading
import time
from LearningEnvironment import *
from LearningMain import *

from api import ping_response, start_response, move_response, end_response

#Create Environment
sizeType = 19
envi = Snekgame(max_board_size=sizeType)
envi.init_just_win_aggresive()
envi.enableOnline(True)

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
    data = bottle.request.json
    color = "#00FF00"
    # Training requires one games played sequentially one at a time this
    # filters unwanted games.
    if data != None:
        if envi.getCurrentGame() == "" and envi.getCurrentSnake() == "" and \
        data["board"]["width"] in [7, 11, 19] and data["board"]["height"] in [7, 11, 19]:
            envi.setCurrentGameParams(data["game"]["id"], data["you"]["id"])
    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json
    move = None
    counter = 0 
    if data != None:
        # Make sure we are only playing our current game
        if  data["game"]["id"] == envi.getCurrentGame() \
        and data["you"]["id"] == envi.getCurrentSnake():
            envi.sendNewData(data)
            while move == None and counter < 9000:
                move = envi.getMove()
                time.sleep(0.0001)
                counter += 1
            if counter >= 9000:
                return move_response("left")
        else:
            move = "left"
    else:
        move = "left"
    return move_response(move)


@bottle.post('/end')
def end():
    data = bottle.request.json
    won = False
    if  data != None:
        if data["game"]["id"] == envi.getCurrentGame() \
        and data["you"]["id"] == envi.getCurrentSnake():
            envi.setCurrentGameParams("", "")
            snakeNames = []
            for snake in data["board"]["snakes"]:
                snakeNames.append(snake["name"])
            if len(data["board"]["snakes"]) <= 1 and (data["you"]["name"] in snakeNames):
                won = True
            envi.endEnvi(won)
    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    # Start main server thread
    threading.Thread(target=bottle.run, kwargs=dict(
        app=application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '80'),
        debug=os.getenv('DEBUG', False),
        quiet=True
        )
    ).start()
    # Start main learning thread
    threading.Thread(target=startLearning, kwargs=dict(
        Env=envi, max_board_size=sizeType, loadFileNumber=38)
    ).start()