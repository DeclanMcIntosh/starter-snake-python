import json
import random
import os

def snakeConfigMaker():
    #delete previous file to avoid overwrite or append shenanigans
    if os.path.exists("snake-config.json"):
        os.remove("snake-config.json")
  
    #randomly select board size
    boardSizes = [7, 11, 19]
    size = random.choice(boardSizes)

    #randomly select food amount; range is currently 1 to double length of board
    foodAmount = random.randint(1, size*2)

    #shuffle snakes and take eight of them, always including the base snake
    allSnakes = ["http://96.54.234.28:80", "http://96.54.234.28:81", "http://96.54.234.28:82", "http://96.54.234.28:83", "http://96.54.234.28:84", 
                 "http://96.54.234.28:85", "http://96.54.234.28:86", "http://96.54.234.28:87", "http://96.54.234.28:88", "http://96.54.234.28:89", ]
    random.shuffle(allSnakes)
    playingSnakes = allSnakes[0:random.randint(1,8)]

    #create the dict of snakes
    snakes = []
    for snake in playingSnakes:
        thing = {}
        thing["name"] = snake[-1:]
        thing["url"]  = snake
        snakes.append(thing)

    #generate json data
    data = {}
    data["width"]    =    size
    data["height"]   =    size
    data["food"]     =    foodAmount
    data["snakes"]   =    snakes

    #generate json file from data
    with open("snake-config.json", "w") as write_file:
        json.dump(data, write_file)


#specialized version for only the base snake alone
#used for wall avoidance learning
def snakeConfigMakerNoHitWalls():
    #delete previous file to avoid overwrite or append shenanigans
    if os.path.exists("snake-config.json"):
        os.remove("snake-config.json")
  
     #randomly select board size
    boardSizes = [7, 11, 19]
    size = random.choice(boardSizes)

    #randomly select food amount; range is currently 1 to double length of board
    foodAmount = random.randint(1, size*2)

    #only using base snake
    snake = "http://96.54.234.28:80"

    #generate json data
    data = {}
    data["width"]    =    size
    data["height"]   =    size
    data["food"]     =    foodAmount
    data["snakes"]   =    [{"name": "wallsAreThreeScaryFiveMe", "url": snake}]

    #generate json file from data
    with open("snake-config.json", "w") as write_file:
        json.dump(data, write_file)
