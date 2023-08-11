
from AppOpener import open, close
import PIL
import time
import pyautogui # clicking and mouse
import cv2

import pytesseract # optical character recognition
import numpy as np


pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

#TODO change all hardcoded pixel shit to relative coding? Or some sort of img recognition baseline file to run beforehand. 
# That can then save all the file locations.

def click(coord, double=False, time_after=.3) -> None:
    '''clicks at specified location. double clicks if double=True'''

    pyautogui.moveTo(coord)

    for i in range(1+double):
        pyautogui.mouseDown()
        time.sleep(.01) # TODO rng uniform
        pyautogui.mouseUp()
        time.sleep(.01)

    time.sleep(time_after)

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

def choose_deck(objective) -> None:
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

    left_corner = min(zip(*loc[::-1])) # pinning the left-top corner of the template here gives best match? I think thats the interp.
    # min not working as intended, basically a random choice as far as logic is concerned but its late and it doesnt seem to matter
    x_correct = template.shape[1] # need to move the cursor from the left edge to the center 
    #pyautogui.moveTo(left_corner + (x_correct,0))# TODO: why does this work and not the half?
    click(left_corner + (x_correct,0))


def queue(format:str='bot_match') -> None:
    '''from main menu do a series of clicks to queue up for match in specified format.
        everything up until (not including) deck selection.''' 

    format_to_coord = {'bot_match': (1666, 696), 
                       'explorer': (1676, 628)}   
    sequence = [(1739, 996), # orange play   
                (1733, 142), # find match
                (1743, 285), # play (unranked)
                format_to_coord[format]] 
    for coord in sequence:
        click(coord)

def start_game() -> None:
    click(1735, 1005) # orange play button   

def is_quest_complete() -> bool:
    '''checks if quest is complete'''

    quest1_text_bbox = [770,775,840,800]
    img = PIL.ImageGrab.grab(quest1_text_bbox) # screenshot of quest text
    #img.show()
    text = pytesseract.image_to_string(img)
    num,denom = text.split('/') # numerator and denom as strings
    return int(denom) - int(num) == 0


def restart_app() -> None:
    close("MTGA")
    open("MTG Arena")
    time.sleep(60) # wait for app to open


# TODO: change static wait times to image recognition. ie: waiting for main menu can be characterized by certain things.

###################### Bot Game Behavior
def is_game_connected() -> bool:
    '''checks if we have an opening hand'''
    bbox = [1076,856,1166,897]
    img = PIL.ImageGrab.grab(bbox) # screenshot 
    #img.show()
    text = pytesseract.image_to_string(img)
    return True if 'Keep' in text else False

def keep_hand() -> None:
    '''keep starting hand'''
    pyautogui.press('space')

def is_game_over() -> bool:
    bbox = [1742,33,1884,65]
    img = PIL.ImageGrab.grab(bbox) # screenshot 
    #img.show()
    text = pytesseract.image_to_string(img)
    return ('Battlefield' in text)


def is_my_turn() -> bool:
    '''true if my turn, false if opponents turn'''
    # read bottom right for string "Opponents"
    turn_text_bbox = [1681,933,1881,964]  #TODO hardcoded
    img = PIL.ImageGrab.grab(turn_text_bbox) # screenshot 
    #img.show()
    img = img.convert('L') # convert to grayscale to help text recog
    #img.show()
    turn_text = pytesseract.image_to_string(img)
    #print(turn_text)
    return not ("Opponent's" in turn_text)

def is_interact() -> bool:
    '''checks if opponent played interaction'''
    pass

def play_land() -> None:
    '''play a land if possible'''
    pass

def play_spell() -> None:
    '''play a spell if possible'''
    pass

def resolve() -> None:
    '''resolves any interaction from opponent or random game actions'''
    pyautogui.press('space')

def combat_phase() -> None:
    '''the bots combat phase'''
    pyautogui.press('space') #all attack

def end_phase() -> None:
    '''end current phase and move to next phase'''
    pyautogui.press('space')

######################################### Script    
def main() -> None:

    open("MTG Arena")
    time.sleep(30) # wait for app to open

    objective = read_quest()
    while (len(objective) > 0): # while there are still quests to complete

        queue()
        choose_deck(objective)
        start_game()
        

        for _ in range(10): # wait until loads, gonna need some error handling here too
            time.sleep(12) # every 12 s check if the game has started
            playing = is_game_connected()
            if playing:
                keep_hand() # keep starting hand
                break
            else:
                pass

        # one last check here, if playing still False after above iters then maybe a restart followed by a continue

        while(playing): 
            # check if game ended, if game ended then break out of loop
            # whos turn
            # bot turn
            #   play a land
            #   play as many cards as possible
            #   all attack
            # opp turn
            #   press spacebar a ton
            pass 

        # TODO click through rewards and shit, totally forgot, does spacebar work?
        if (is_quest_complete() is True): 
            restart_app() # reset the UI so a fresh quest is in the first position
        objective = read_quest()

    close("MTGA")


def main_test():
    time.sleep(2)
    print(is_game_over())

main_test()