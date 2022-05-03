
import pyautogui as pt
import datetime
import webbrowser
from time import time, sleep
from datetime import datetime,timedelta



def multiple_clicks():
    # webbrowser.open('https://tinder.com/app/recs')
    sleep(10)
    c = 0
    while c <= 100:
        pt.click(pt.position())
        c += 1
        # print(c)
    # pt.hotkey('f5')
    # print('****************************')
    # sleep(7)

# while 1:
#     multiple_clicks()
