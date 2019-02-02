import pyautogui

from time import sleep

import random

'''
Make sure your on a 1080p screen 
and have chrome as the first thing on
your taskbar open to battlesnake.io/play
on windows 10 run this and 
it will make snek games happen 
'''

def openChrome():
    '''
    makes the open screen chrome, requires chome
    be the fist thing on task bar
    '''
    pyautogui.moveTo(x=525, y=1050)
    pyautogui.click()
    sleep(0.2)

def hitPlay():
    '''
    Hits play button on battle snake
    '''
    pyautogui.moveTo(x=115, y=78)
    pyautogui.click()
    sleep(1.5)

def createNewGame():
    '''
    starts to create new game from the play screen
    '''
    pyautogui.moveTo(x=1920/2, y=130)
    pyautogui.click()
    sleep(0.2)

def scaleChrome():
    '''
    starts to create new game from the play screen
    '''
    pyautogui.moveTo(x=1890, y=50)
    pyautogui.click()
    pyautogui.moveTo(x=1760, y=235)
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()

def setGameSize(size,foodAmount):
    '''
    Sets up a game for the width of the
    game (must be one of the turnament values),
    and the food amount(can be any value)
    '''
    if size not in ["small", "medium", "large"]:
        size = "small"
    
    if size == "small":
        #Set the board size
        pyautogui.moveTo(x=900,y=155)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(x=900,y=160)
        pyautogui.click()
        sleep(0.1)     

    if size == "medium":
        #Set the board size
        pyautogui.moveTo(x=900,y=155)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(x=900,y=170)
        pyautogui.click()
        sleep(0.1)  

    if size == "large":
        #Set the board size
        pyautogui.moveTo(x=900,y=155)
        pyautogui.click()
        sleep(0.1)
        pyautogui.moveTo(x=900,y=180)
        pyautogui.click()
        sleep(0.1)

    # Set the amount of food
    pyautogui.moveTo(x=890,y=180)
    pyautogui.click()
    pyautogui.press('backspace')
    pyautogui.press('backspace')
    for value in list(str(foodAmount)):
        pyautogui.press(value)

def assignSnakes():
    '''
    Choses random snakes and a random amount of snakes to play
    '''
    snakeNumbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    random.shuffle(snakeNumbers)
    snakeNumbers = snakeNumbers[0:random.randint(2,9)]
    pyautogui.moveTo(x=1920/2, y=215)
    for snake in snakeNumbers:
        print(snake)
        pyautogui.click()
        pyautogui.moveRel(xOffset=0, yOffset=((snake + 1)*12.9))
        pyautogui.click()
        pyautogui.moveRel(xOffset=0, yOffset=(-1*(snake + 1)*12.9))
        pyautogui.moveRel(xOffset=0, yOffset=60.8)
    pyautogui.moveRel(yOffset=((8-len(snakeNumbers))*34))
    pyautogui.click()

def resetForm():
    pyautogui.moveTo(x=1030, y=220)
    pyautogui.click()
    sleep(1.5)  

def assignForNoCollisionTraining():
    pyautogui.moveTo(x=1920/2, y=250)
    pyautogui.click()
    sleep(0.05)
    pyautogui.moveTo(x=1920/2, y=260)
    pyautogui.click()  
    sleep(0.05)
    pyautogui.moveTo(x=1920/2, y=555)
    pyautogui.click()  
    sleep(0.1)

def startup():
    openChrome()
    scaleChrome()

def runAGameForNoCollisionTraining():
    '''TODO make this detect when game is over and 
    then restart rather than wait a known period of time
    '''
    hitPlay()
    createNewGame()
    resetForm()
    sizes = ["small", "medium", "large"]
    random.shuffle(sizes)
    setGameSize(size=sizes[0], foodAmount=random.randint(3,50))
    assignForNoCollisionTraining()
    sleep(5)   

