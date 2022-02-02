import webbrowser as web
import os
import time
import pyautogui
from Protected import credentials


HEADS_URL = 'https://heads.thinkpalm.info/Home.aspx'

def navigate_to_image(image, clicks, off_x = 0, off_y = 0):
     """   Navigates to the image on the screen.
            move x (right) or y(vertical) axis to move cursor 
            clicks = how many times to click
     """
     try:
          position = pyautogui.locateCenterOnScreen(image, confidence = .8)
     except:
          return f'\n\n{image}\n Image not found or Image is corrupted'
     if position is None:
          print(f'{image} \nImage Not Found')
     else:
          pyautogui.moveTo(position, duration = .5)
          pyautogui.moveRel(off_x, off_y, duration = .2)
          pyautogui.click(clicks = clicks, interval = .1)


def connect_fortclient():
     """ connect to fortclient """
     passwd = credentials.all_credentials.get('fortclient_password')
     os.startfile(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\FortiClient VPN\FortiClient VPN.lnk")
     time.sleep(5)
     navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\passwd.png',1, 10)
     time.sleep(2)
     pyautogui.write(passwd)
     pyautogui.press('enter')
     try: pyautogui.click(pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\DesktPassTp!@3op\python\pics\connect_fortclient.png'))
     except:print('Connection Failed or You already pressed enter Key')
     
     if pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\Desktop\python\pics\disconnect_blue.png') is not None:
          return('\n\nConnected to FortClient')
     pyautogui.click(pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\Desktop\python\pics\minimize_white.png'))


def mark_attendance():
     """ Mark the attendance_request at EOD"""
     time.sleep(15)
     try:web.open(HEADS_URL)
     except web.Error:print('Error: Could not open  URL')
     time.sleep(5)
     navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\login_fotclient.png',2)     # login to HEADS
     time.sleep(15)
     pyautogui.click(x=1242, y=357)
     pyautogui.scroll(-2000)
     time.sleep(2)
     navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\leave_Heads.png',2)         # click on Leave button in heads
     time.sleep(2)
     navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\wfh_attendance.png',1)      # MAIN DROP DOWN FOR ALL QUERIES , NEEDS TO BE CLICKED FIRST , THEN DO SUB OPERATIONS
     time.sleep(2)
     navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\attendance_request.png',1)   # we click on attendance request to mark the attendance
                                                                                                                                                                                         # time.sleep(2)       # just in case u missed 2 days , uncomment it | and mark iT
                                                                                                                                                                                         # navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\add_yellow.png',1)
     time.sleep(2)
     navigate_to_image(r'pics\save_blue.png',1)                                            # save the attendance
     time.sleep(2)
     navigate_to_image(r'pics\ok_blue.png',1)
     navigate_to_image(r'pics\ok_light_blue.png',1)
     # time.sleep(4)
     # navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\wfh_attendance.png',1)      # MAIN DROP DOWN FOR ALL QUERIES , NEEDS TO BE CLICKED FIRST , THEN DO SUB OPERATIONS
     # time.sleep(4)
     # navigate_to_image(r'pics\wfh_attendance_list.png',1)                                   # here we check and conform our attendance


mark_attendance() if connect_fortclient() else print('\nLet me connect to fortclient first\t'),print('\nYour Connected to FortClient\nNow lets mark the attendance\n'),mark_attendance()
     