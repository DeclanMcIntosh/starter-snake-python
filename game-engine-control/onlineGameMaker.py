from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

browser = webdriver.Chrome()


def createNewGame():
    browser.get(('https://play.battlesnake.io/g/new/'))
    #find the buttons we need
    addRandomSnake = browser.find_element_by_id('add-random-snake-button')
    selectBoardSize = Select(browser.find_element_by_id('id_board_size'))
    startGame = browser.find_element_by_xpath('/html[@class=\'gr__play_battlesnake_io\']/body[@class=\'layout-horizontal menu-auto-hide\']/div[@class=\'content-wrapper\']/main[@class=\'content container\']/section[@class=\'page-content\']/div[@class=\'form-group card\']/div[@class=\'card-body\']/form/button[@class=\'btn btn-primary\']') # html body main section div div form 


    #chose board size
    selectBoardSize.select_by_visible_text('Large')

    #Add Random snake
    addRandomSnake.click()
    addRandomSnake.click()

    #Hit Create button
    startGame.click()

    #password.send_keys(passwordStr)
    sleep(100)


createNewGame()