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

    #randomize snakes: shuffle snakes and take eight of them, always including the base snake
    playingSnakes = ["http://192.168.0.10:80", "http://192.168.0.10:81"]
    for x in range(0,random.randint(0,7)):
        playingSnakes.append("http://192.168.0.10:82")

    #create the dict of snakes
    #the name is just the last number in the IP address
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
    snake = "http://192.168.0.10:80"

    #generate json data
    data = {}
    data["width"]    =    size
    data["height"]   =    size
    data["food"]     =    foodAmount
    data["snakes"]   =    [{"name": "wallsAreThreeScaryFiveMe", "url": snake}]

    #generate json file from data
    with open("snake-config.json", "w") as write_file:
        json.dump(data, write_file)
