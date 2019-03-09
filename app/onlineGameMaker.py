"""onlineGameMaker.py: TODO Description of what this file does."""

__author__ = "Declan McIntosh, Robert Lee, Luke Evans"
__copyright__ = "Copyright 2019"
__license__ = "MIT"
__version__ = "1.0"

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from time import sleep

from random import randint

#browser = webdriver.Chrome()


def addSpecificSnake(browser, name):
    selectSnake = browser.find_element_by_id('snakes-list')
    addTypedSnake = browser.find_element_by_id('add-snake-button')
    selectSnake.send_keys(name)
    clickOnSnake = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/main/section/div/div/div/div/form/div[5]/div/div[1]/div/a')))
    sleep(0.1)
    clickOnSnake.click()
    sleep(0.1)
    addTypedSnake.click()


def createNewGame():
    try:
        #chrome_options = Options()
        #chrome_options.add_argument("--window-size=1920,1080")
        #browser = webdriver.Chrome(chrome_options=chrome_options)

        #Load the page
        browser.get(('https://play.battlesnake.io/g/new/'))
        #Wait for the page to load
        sleep(0.5)
        #Find the buttons and feilds we need
        addRandomSnake = browser.find_element_by_id('add-random-snake-button')
        selectBoardSize = Select(browser.find_element_by_id('id_board_size'))

        startGame = browser.find_element_by_xpath('/html/body/div[3]/main/section/div/div/div/div/form/button') # html body main section div div form 

        #chose board size
        boardSelect = randint(0,3)
        if boardSelect == 0:
            selectBoardSize.select_by_visible_text('Large - 19x19')
            #selectBoardSize.select_by_visible_text('Small - 7x7')
        if boardSelect == 1:
            selectBoardSize.select_by_visible_text('Medium - 11x11')
        if boardSelect == 2:
            selectBoardSize.select_by_visible_text('Small - 7x7')
        #Add Random snakes
        if boardSelect == 1 or boardSelect == 0:
            numSnakes = randint(4,8)
        if boardSelect == 2 :
            numSnakes = randint(3,4)
        ourSnakeNum = randint(0,numSnakes-1)
        for value in range(0, numSnakes):
            if value != ourSnakeNum:
                #Add Random Snake
                sleep(0.1)
                addRandomSnake.click()
            else:
                sleep(0.1)
                #Add Our Snake
                #addSpecificSnake(browser, "DeclanMcIntosh/trainingDummy")
                addSpecificSnake(browser, "DeclanMcIntosh/legless_lizzard")

        #Hit Create button
        sleep(0.1)
        startGame.click()
    except Exception:
        pass



def runGames():
    while(True):
        createNewGame()
        sleep(15)

#runGames()

