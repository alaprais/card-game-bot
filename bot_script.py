
from AppOpener import open, close
import PIL
import time
import pyautogui # clicking and mouse
import cv2

import pytesseract # optical character recognition
import numpy as np


pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def click(coord, double=False, time_after=.3) -> None:
    '''clicks at specified location. double clicks if double=True'''

    pyautogui.moveTo(coord)

    for i in range(1+double):
        pyautogui.mouseDown()
        time.sleep(.01) # TODO rng uniform
        pyautogui.mouseUp()
        time.sleep(.01)

    time.sleep(time_after)

# Main Menu Functions
def read_quest() -> str:
    '''reads first quest and returns objective'''

    objectives_master_list = ['white','black','green','red','blue', 
                                'lands','Attack', 'creature', 'Kill']
    # TODO reroll functionality (separate func)
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
    '''chooses deck based on objective. Must be on a screen with the deckboxes'''  # TODO could this use a img classifier

    template_dict = {'white': 'temp', 
                     'blue': 'temp',
                     'black': 'temp',
                     'red': 'temp',
                     'green': r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\objectives\green.png",
                     }
    
    template = cv2.imread(template_dict[objective]) # img we want to match in current screen
    sct = PIL.ImageGrab.grab() # screenshot 
    sct = np.array(sct) # transformed to numpy array for cv2
    sct = cv2.cvtColor(sct, cv2.COLOR_RGB2BGR) # convert to cv2 color space, RGB to BGR

    res = cv2.matchTemplate(sct, template, cv2.TM_CCOEFF_NORMED) # match scores
    threshold = 0.8
    loc = np.where(res >= threshold)
    print(loc)

    print(sct.shape)
    print(res.shape)

    # click on spot
    #pyautogui.moveTo(coord)

    #####
    # img = cv2.imread(r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\img_to_match.png")
    # template = cv2.imread(template_dict[objective])
    # res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED) # matching

    # # Specify a threshold
    # threshold = 0.8
    # # Store the coordinates of matched area in a numpy array
    # loc = np.where(res >= threshold)
    # print(loc)
    # h, w = template.shape[0:2]
    # # draw rectangle around matched area
    # for pt in zip(*loc[::-1]):
    #     cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 255, 255),2)

    # cv2.imshow("Image",img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # cv2.imshow("Template",template)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

def queue(format:str='bot_match') -> None:
    '''from main menu do a series of clicks to queue up for match in specified format ''' 

    format_to_coord = {'bot_match': (1666, 696), 
                       'explorer': (1676, 628)}
    sequence = [(1739, 996), # orange play   
                (1733, 142), # find match
                (1743, 285), # play (unranked)
                format_to_coord[format]] 
    
    for coord in sequence:
        click(coord)
    # choose deck
    # click play

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


def restart_app() -> None:
    close("MTGA")
    open("MTG Arena")


    
def main() -> None:
    # Launch Game
    # open("MTG Arena")
    # time.sleep(60) # wait for app to open
    time.sleep(2)
    #choose_deck('green')
    click((471, 423), double=True)
    # while (len(objective) > 0): # while there are stlll quests to complete

    #     choose_deck(objective='green')

    #     # TODO: GAME
    #     # in_game = False
    #     # while(in_game): # play a game
    #     #     pass

    #     objective = read_quest()

    #close("MTGA")



main()