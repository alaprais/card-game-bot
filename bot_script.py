
from AppOpener import open, close
import PIL
import time
import pyautogui # clicking and mouse
import cv2

import pytesseract # optical character recognition
import numpy as np


pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


# Main Menu Functions
def read_quest() -> str:
    '''reads first quest and gives objective'''
    objectives_master_list = ['white','black','green','red','blue', 
                                'lands','Attack', 'creature', 'Kill']
    
    # TODO expand reroll functionality
    # if one is less than 750 gold, reroll to 500
    # For now re-roll "kill opponents creatures"

    #quest 1 Point(x=805, y=871)
    #quest 2 Point(x=510, y=866)
    #quest 3 Point(x=235, y=852)

    quest1_text_bbox = [875,840,995,900]
    img = PIL.ImageGrab.grab(quest1_text_bbox) # screenshot of quest text
    #img.show()
    quest_text = pytesseract.image_to_string(img)
    #print(quest_text)

    objective = [x for x in quest_text.split() if x in objectives_master_list]

    if len(objective) > 1:
        objective = objective[np.random.randint(len(objective))] # randomly choose one of the two colors
    return objective

def choose_deck(objective):
    '''chooses deck based on objective'''

    # from main menu do a series of clicks to queue up for bot match
            #"orange play button: Point(x=1739, y=996)"
            #"find match : Point(x=1733, y=142)"
            #"Play section : Point(x=1743, y=285)"
            #"Explorer Play Point(x=1676, y=628)"  ## or  ' Bot Match Point(x=1666, y=696) '
    sequence = [(1739, 996), # orange play
                (1733, 142), # find match
                (1743, 285), # play (unranked)
                (1666, 696)] # bot match
    for coord in sequence:
        pyautogui.moveTo(coord)
        pyautogui.mouseDown()
        time.sleep(.01)
        pyautogui.mouseUp()
        time.sleep(.5)

    # choose deck # TODO replace with a small classifier?
    template_dict = {'green': r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\objectives\green.png",
                     'blue' : 'oops'}
    # img = PIL.ImageGrab.grab() # screenshot of screen
    # img = np.array(img) # transformed to numpy array for cv2

    img = cv2.imread(r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\img_to_match.png")
    template = cv2.imread(template_dict[objective])

    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED) # matching

    # Specify a threshold
    threshold = 0.8
    # Store the coordinates of matched area in a numpy array
    loc = np.where(res >= threshold)
    print(loc)
    h, w = template.shape[0:2]
    # draw rectangle around matched area
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 255, 255),2)

    cv2.imshow("Image",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imshow("Template",template)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def is_quest_complete() -> bool:
    '''checks if quest is complete'''
    # top left Point(x=773, y=774)
    # top right Point(x=834, y=775)
    # bottom left Point(x=777, y=797)
    # bottom right Point(x=833, y=801)
    quest1_text_bbox = [770,775,840,800]
    img = PIL.ImageGrab.grab(quest1_text_bbox) # screenshot of quest text
    #img.show()
    text = pytesseract.image_to_string(img)
    num,denom = text.split('/') # numerator and denom as strings
    return int(denom) - int(num) == 0


def restart() -> None:
    pass




def main() -> None:
    # Launch Game
    # open("MTG Arena")
    # time.sleep(30) # wait for app to open

    time.sleep(2)
    #choose_deck(objective='green')
    print(is_quest_complete())

    # time.sleep(3)
    # objective = read_quest()
    # print(objective)
    # while (len(objective) > 0): # while there are stlll quests to complete

    #     choose_deck(objective='green')

    #     # TODO: GAME
    #     # in_game = False
    #     # while(in_game): # play a game
    #     #     pass

    #     objective = read_quest()

    #close("MTGA")

