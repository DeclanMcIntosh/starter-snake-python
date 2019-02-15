from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

from random import randint

browser = webdriver.Chrome()

def addSpecificSnake(browser, name):
    selectSnake = browser.find_element_by_id('snakes-list')
    addTypedSnake = browser.find_element_by_id('add-snake-button')
    selectSnake.send_keys(name + "\n")
    clickOnSnake = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/main/section/div/div/form/div[4]/div/div[1]/div/a/b')))
    clickOnSnake.click()
    sleep(0.1)
    addTypedSnake.click()


def createNewGame():
    #Load the page
    browser.get(('https://play.battlesnake.io/g/new/'))
    #Wait for the page to load
    sleep(0.3)
    #Find the buttons and feilds we need
    addRandomSnake = browser.find_element_by_id('add-random-snake-button')
    selectBoardSize = Select(browser.find_element_by_id('id_board_size'))
    startGame = browser.find_element_by_xpath('/html/body/div[3]/main/section/div/div/form/button') # html body main section div div form 

    #chose board size
    boardSelect = randint(0,3)
    if boardSelect == 0:
        selectBoardSize.select_by_visible_text('Large - 19x19')
    if boardSelect == 1:
        selectBoardSize.select_by_visible_text('Medium - 11x11')
    if boardSelect == 2:
        selectBoardSize.select_by_visible_text('Small - 7x7')
    #Add Random snakes
    numSnakes = randint(2,8)
    ourSnakeNum = randint(0,numSnakes)
    for value in range(0, numSnakes):
        if value != ourSnakeNum:
            #Add Random Snake
            addRandomSnake.click()
            sleep(0.1)
        else:
            #Add Our Snake
            #addSpecificSnake(browser, "DeclanMcIntosh/trainingDummy")
            addSpecificSnake(browser, "DeclanMcIntosh/legless lizzard")

    #Hit Create button
    sleep(0.3)
    startGame.click()

