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
sizeType = 19


envi = Snekgame(max_board_size=sizeType)
envi.init_just_win_aggresive()


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
    data = bottle.request.json
    color = "#00FF00"
    envi.sendNewData(data)
    return start_response(color)


@bottle.post('/move')
def move():
    #print("move Request recived")
    global envi
    data = bottle.request.json
    if len(data['board']['snakes']) == 1:
        envi.endEnvi(win=True)
    envi.sendNewData(data)
    move = None
    while move == None:
        move = envi.getMove() 
    return move_response(move)


@bottle.post('/end')
def end():
    #print("end message recived")
    data = bottle.request.json
    if len(data['board']['snakes']) == 1:
        envi.endEnvi(win=True)
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
        port=os.getenv('PORT', '80'),
        debug=os.getenv('DEBUG', False),
        quiet=True
        )
    ).start()
    threading.Thread(target=startLearning, kwargs=dict(
        Env=envi, max_board_size=sizeType, loadFileNumber=-1)
    ).start()