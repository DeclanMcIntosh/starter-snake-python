import json
import os
import random
import bottle
import threading
import time
from LearningEnvironment import *
from trainingDummys import *

from api import ping_response, start_response, move_response, end_response

#Flags for what kind of network we are training
sizeType = 7


envi = Snekgame(max_board_size=sizeType)
envi.init_wholesome_pp()
envi0 = Snekgame(max_board_size=sizeType)
envi0.init_absolute_unit()


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
    #print("start request recived")
    color = "#00FF00"
    return start_response(color)


@bottle.post('/move')
def move():
    #print("move Request recived")
    global envi
    data = bottle.request.json
    envi.sendNewData(data)
    move = envi.getMove()
    while move == None:
        move = envi.getMove()   
    return move_response(move)


@bottle.post('/end')
def end():
    #print("end message recived")
    data = bottle.request.json
    if len(data['board']['snakes']) == 0:
        envi.endEnvi(win=False) #TODO change to True when training with multiple snakes
    else:
        envi.endEnvi(win=False)
    envi.sendNewData(data)
    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    threading.Thread(target=bottle.run, kwargs=dict(
        app=application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '82'),
        debug=os.getenv('DEBUG', False),
        quiet=True
        )
    ).start()
    threading.Thread(target=dummyRun, kwargs=dict(
        Env=envi, max_board_size=sizeType)
    ).start()