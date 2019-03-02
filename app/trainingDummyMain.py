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
sizeType = 19

envi = Snekgame(max_board_size=sizeType)
envi.init_wholesome_pp()
envi.enableOnline(False)

comm = threadComms()
comm.assertLoadNewFile()
oepnNewFileCounter = 0

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
    color = "#FF00E8"
    return start_response(color)


@bottle.post('/move')
def move():
    global oepnNewFileCounter
    #print("move Request recived")
    start = time.time()
    data = bottle.request.json
    if data["board"]["width"] in [7, 11, 19] and data["board"]["height"] in [7, 11, 19]:
        comm.giveNewData(data)
        sendMove = None
        while sendMove == None:
            sendMove = comm.getNewMove()
        print("move made in " + str(time.time() - start))
        return move_response(sendMove)
    else:
        return move_response('left')


@bottle.post('/end')
def end():
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
    threading.Thread(target=startDummy, kwargs=dict(
        env = envi,
        Comm = comm,
        tryHard=True
        )
    ).start()