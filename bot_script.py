
from AppOpener import open, close
import PIL
import time
import pyautogui # clicking and mouse
import cv2

import pytesseract # optical character recognition
import numpy as np #rng


pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

#TODO change all hardcoded pixel shit to relative coding? Or some sort of img recognition baseline file to run beforehand. 
# That can then save all the file locations.

#data_paths 
WHITE_DECK_PATH = r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\objectives\white.png"
BLUE_DECK_PATH = r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\objectives\blue.png"
BLACK_DECK_PATH = r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\objectives\black.png"
RED_DECK_PATH = r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\objectives\red.png"
GREEN_DECK_PATH = r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\objectives\green.png"

CHOOSE_ATTACKERS_PATH = r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\condition_checks\choose_attackers.png"

def click(coords:tuple, double=False, time_after=.3) -> None:
    '''clicks at specified location. double clicks if double=True'''

    pyautogui.moveTo(coords)
    time.sleep(.1)

    for _ in range(1+double):
        pyautogui.mouseDown()
        time.sleep(.01) 
        pyautogui.mouseUp()
        time.sleep(.01)

    time.sleep(time_after)

def press_spacebar() -> None:
    pyautogui.keyDown('space')
    time.sleep(.1)
    pyautogui.keyUp('space')

def in_main_menu() -> bool: 
    '''screenshot experience track level thing to determine if in main menu or not'''

    #play_bbox = [1694,990,1774,1029]
    # [182,47,246,69] - profile
    bbox = [1415,926,1445,955]   
    img = PIL.ImageGrab.grab(bbox) # screenshot 
    img = img.convert('L') # grayscale
    text = pytesseract.image_to_string(img)
    return len(text) > 0


def read_quest() -> str:
    '''reads first quest, returns objective'''

    objectives_master_list = ['white','black','green','red','blue', 
                                'lands','Attack', 'creatures', 'Kill']
    
    # TODO reroll functionality (separate func)

    quest1_text_bbox = [875,840,995,900]
    img = PIL.ImageGrab.grab(quest1_text_bbox) # screenshot of quest text
    #img.show()
    quest_text = pytesseract.image_to_string(img)
    #print(quest_text)
    objective = [x for x in quest_text.split() if x in objectives_master_list]

    if len(objective) > 1:
        objective = objective[np.random.randint(len(objective))] # randomly choose one of the two colors
    else:
        objective = objective[0]

    return objective

def reroll_quest() -> None:
    click((807,870)) # quest box
    click((1138,614))  # confirm

def choose_deck(objective) -> None:
    '''chooses deck based on objective. Must be on a screen with the deckboxes'''  # TODO could this use a img classifier

    template_dict = {'white': WHITE_DECK_PATH, 
                     'blue': BLUE_DECK_PATH,
                     'black': BLACK_DECK_PATH,
                     'red': RED_DECK_PATH,
                     'green': GREEN_DECK_PATH,
                     'lands': GREEN_DECK_PATH,
                     'creatures': GREEN_DECK_PATH,
                     'Attack': RED_DECK_PATH
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
                       'explorer': (1676, 628),
                       'historic': (1664, 582)}   
    sequence = [(1739, 996), # orange play   
                (1733, 142), # find match
                (1743, 285), # play (unranked)
                format_to_coord[format]] 
    for coord in sequence:
        click(coord)   

def start_game(approx_wait_time=180, interval = 5) -> bool:
    click((1735, 990)) # orange play button   
    for _ in range(int(approx_wait_time/interval)): # wait until loads, gonna need some error handling here too
            time.sleep(interval) # every interval secs check if the game has started
            playing = is_game_connected()
            if playing:
                keep_hand() # keep starting hand
                break
            else:
                continue
    return playing

def is_quest_complete() -> bool:
    '''checks if quest is complete'''
    quest1_text_bbox = [770,775,840,800]
    img = PIL.ImageGrab.grab(quest1_text_bbox) # screenshot of quest text
    img = img.convert('L')
    text = pytesseract.image_to_string(img)
    num,denom = text.split('/') # numerator and denom as strings
    return int(denom) - int(num) == 0


def restart_app() -> None:
    close("MTGA")
    open("MTG Arena")
    time.sleep(40) # wait for app to open


# TODO: change static wait times to image recognition. ie: waiting for main menu can be characterized by certain things.

###################### Pre & Post Game 
def is_game_connected() -> bool:
    '''checks if we have an opening hand'''
    bbox = [1076,856,1166,897]
    img = PIL.ImageGrab.grab(bbox) # screenshot 
    #img.show()
    text = pytesseract.image_to_string(img)
    return True if 'Keep' in text else False

def keep_hand() -> None:
    '''keep starting hand'''
    press_spacebar()

def is_game_over() -> bool:
    bbox = [1742,33,1884,65]
    img = PIL.ImageGrab.grab(bbox) # screenshot 
    #img.show()
    text = pytesseract.image_to_string(img)
    return ('Battlefield' in text)

def is_survey() -> bool:
    '''is it the end of game survey'''
    bbox = [915,417,1260,463]
    img = PIL.ImageGrab.grab(bbox)
    text = pytesseract.image_to_string(img)
    return 'fun in the match' in text

def is_game_over_agg() -> bool:
    out = False

    if is_survey():
        click((971,847)) # "skip"
        time.sleep(2)
        out = True

    if is_game_over():
        # click((1770,49)) click view battlefield ,  click((1770,49)) # click leave match
        click((945,547)) # click center screen to leave game
        time.sleep(np.random.randint(5,8)) # main menu load time 
        out = True

    return out

def is_reward() -> bool:
    bbox = [1685, 987, 1786, 1027]
    img = PIL.ImageGrab.grab(bbox) # screenshot 
    #img.show()
    text = pytesseract.image_to_string(img)
    print(text)
    return ('Claim' in text)

    
        
###################### Bot Game Behavior
def is_opponents_turn() -> bool:
    '''true if my turn, false if opponents turn'''
    # read bottom right for string "Opponents"
    turn_text_bbox = [1681,933,1881,964]  #TODO hardcoded
    img = PIL.ImageGrab.grab(turn_text_bbox) # screenshot 
    #img.show()
    img = img.convert('L') # convert to grayscale to help text recog
    #img.show()
    turn_text = pytesseract.image_to_string(img)
    #print(turn_text)
    return ("Opponent's" in turn_text)


def is_interact() -> bool:
    '''checks if opponent played interaction on bot turn'''
    resolve_bbox = [1719,931,1839,968]  #TODO hardcoded
    img = PIL.ImageGrab.grab(resolve_bbox) # screenshot 
    #img.show()
    img = img.convert('L') # convert to grayscale to help text recog
    turn_text = pytesseract.image_to_string(img)
    return ("Resolve" in turn_text)


def play_cards(passes=1) -> None:
    '''starting from the left, move through and try to play all cards in hand. repeats n times'''
    card_coords = [(563,1044), (733,1062), (900,1033), (1072,1017), (1237,1040), (1413,1060), (1569,1066) ]
    idxs = np.random.choice(range(len(card_coords)), size=len(card_coords), replace=False,
                                   p= [.05,.05,.25,.3,.25,.05,.05])
    card_coords = [card_coords[x] for x in idxs]
    for _ in range(passes):
        for card in card_coords:
            if is_opponents_turn() or is_choose_attackers():
                break
            click(card,double=True)
            pyautogui.keyDown('z')
            time.sleep(.02)
            pyautogui.keyUp('z')
            time.sleep(2)
            if is_interact(): 
                press_spacebar()

def is_choose_attackers() -> bool:
    bbox = [944,447,1066,470]   
    # sct = PIL.ImageGrab.grab(bbox) # screenshot 
    # sct = sct.convert('L') # grayscale
    # sct.save( r"C:\Users\Arnaud\projects\resources\card-game-bot-resources\condition_checks\choose_attackers.png")
    template = cv2.imread(CHOOSE_ATTACKERS_PATH) # img we want to match in current screen
    sct = PIL.ImageGrab.grab(bbox) # screenshot  
    sct = sct.convert('L')
    sct = np.array(sct) # transformed to numpy array for cv2
    sct = cv2.cvtColor(sct, cv2.COLOR_RGB2BGR) # convert to cv2 color space, RGB to BGR
    res = cv2.matchTemplate(sct, template, cv2.TM_CCOEFF_NORMED) # match scores
    threshold = 0.8
    # loc = np.sum(res >= threshold) 
    #print(res[0][0])
    return res[0][0] > threshold

######################################### Script    
def main() -> None:

    open("MTG Arena")
    
    while(not in_main_menu()): # wait for app to open
        time.sleep(10)

    objective = read_quest()
    if objective == 'Kill':
        reroll_quest()
        objective = read_quest() 
        if objective == 'Kill': # supremely unlucky, two kill quests in a row, pack it up, try again tomorrow
            close('MTGA')
            exit() # kill the script
    
    while ( (len(objective) > 0) ): # while there are still quests to complete
        queue('historic')
        choose_deck(objective)

        playing = start_game(approx_wait_time=180,interval=5) # start game and keep hand
        
        # TODO one last check here, 
        # #if playing still False after above iters then maybe a restart followed by a continue

        hand_bbox = [209,915,1657,1080]
        while(playing): 

            if is_game_over_agg():
                playing = False
                continue
            
            # sct of hand
            sct = PIL.ImageGrab.grab(hand_bbox)
            pixel_info =np.array(sct)
            msk = (pixel_info[:,:,0] < 70) & (pixel_info[:,:,1] > 200) & (pixel_info[:,:,2] >200) # turquoise rgb vals
            target_pixels = np.argwhere(msk)


            while (len(target_pixels) > 200):
                first_point = target_pixels[0]  # highest (from bottom of screen) point in sct with turquoise
                x_origin, y_origin = hand_bbox[0:2] 
                card_coord = (x_origin + first_point[1],y_origin + first_point[0]) # coords in full screen framework
                card_coord = card_coord + (-100, 100) # move cursor to center-ish area of card
                click(card_coord,double=True)
                pyautogui.moveTo((115,43))

                time.sleep(3)

                sct = PIL.ImageGrab.grab(hand_bbox)
                pixel_info =np.array(sct)
                msk = (pixel_info[:,:,0] < 70) & (pixel_info[:,:,1] > 200) & (pixel_info[:,:,2] >200) # turquoise rgb vals
                target_pixels = np.argwhere(msk)
            
            press_spacebar()

        # claim rewards
        while(is_reward()):
            click((1723, 1013)) # claim
            time.sleep(np.random.randint(1,2)) # wait for animations

        # check if quest is done
        if (is_quest_complete() is True): 
            restart_app() # reset the UI so a fresh quest is in the first position
            time.sleep(10)
            while(not in_main_menu()):
                time.sleep(10)
        objective = read_quest()

    close("MTGA")

main()