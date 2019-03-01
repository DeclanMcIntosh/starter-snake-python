import json
import os
import random
import bottle
import threading
import time

from LearningEnvironment2 import *
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
    data = bottle.request.json
    color = "#00FF00"
    return start_response(color)


@bottle.post('/move')
def move():
    global oepnNewFileCounter
    #print("move Request recived")
    start = time.time()
    data = bottle.request.json
    traingSnakeDead = True #TODO TO USE THIS FOR OFLINE TRAINING CHANGE THIS REEEEE
    #if the snake we are traning is not in the game kill yourself
    for snake in data["board"]["snakes"]:
        if snake["name"] != data["you"]["name"]:
            traingSnakeDead = False
    if traingSnakeDead:
        print("mainSnakedead")
        return move_response("down")
    comm.giveNewData(data)
    sendMove = None
    while sendMove == None:
        sendMove = comm.getNewMove()
    oepnNewFileCounter += 1
    if oepnNewFileCounter > 17500:
        oepnNewFileCounter = 0
        comm.assertLoadNewFile()
    print("move made in " + str(time.time() - start))
    return move_response(sendMove)


@bottle.post('/end')
def end():
    data = bottle.request.json
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
    threading.Thread(target=startDummy, kwargs=dict(
        env = envi,
        Comm = comm,
        tryHard=True
        )
    ).start()