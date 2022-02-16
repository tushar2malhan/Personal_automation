import webbrowser as web
import os
import time
import pyautogui
from Protected import credentials
import requests
import datetime



class Think_palm():
    HEADS_URL = 'https://heads.thinkpalm.info/Home.aspx'
    TCUBE_URL = 'https://tcube.thinkpalm.info/user/projectlist'
            
    def __init__(self,username):
        self.username = username
    

    def navigate_to_image(self,image, clicks, off_x = 0, off_y = 0):
        
        """   Navigates to the image on the screen.
                move x for horizontal +500 move right , - 500 move left 
                and y for vertical  axis to move the cursor  + 10 move down , - 10 move up
                clicks = how many times to click
                
        """
        position = 0
        try:
            position = pyautogui.locateCenterOnScreen(image, confidence = .8)
        except:
            print(f'\n\n{image}\n Image not found or Image is corrupted')
        if position is None:
            print(f'{image} \nImage Not Found')
        else:
            pyautogui.moveTo(position, duration = .5)
            pyautogui.moveRel(off_x, off_y, duration = .2)
            pyautogui.click(clicks = clicks, interval = .1)
            return True
             

    def connect_fortclient(self):
        """ connect to fortclient """
        passwd = credentials.all_credentials.get('fortclient_password')
        os.startfile(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\FortiClient VPN\FortiClient VPN.lnk")
        time.sleep(5)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\passwd.png',1, 10)
        time.sleep(2)
        pyautogui.write(passwd)
        pyautogui.press('enter')
        try: pyautogui.click(pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\DesktPassTp!@3op\python\pics\connect_fortclient.png'))
        except:print('\nConnection Failed or You already Connected to Fortclient VPN')
        
        if pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\Desktop\python\pics\disconnect_blue.png') is not None:
            return('\n\nConnected to FortClient')
        pyautogui.click(pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\Desktop\python\pics\minimize_white.png'))


    def mark_attendance(self):
        """ Mark the attendance_request at EOD """
        time.sleep(15)
        try:
            response = requests.get(self.HEADS_URL)
            print('\n\nWelcome to Heads \t')
        except Exception:
            exit('\nError: Could not open Heads URL\n')
        web.open(self.HEADS_URL) if response.status_code == 200 else print('Check the URL \n')
        time.sleep(5)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\login_fotclient.png',2)     # login to HEADS
        time.sleep(15)
        pyautogui.click(x=1242, y=357)
        pyautogui.scroll(-2000)
        time.sleep(2)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\leave_Heads.png',2)         # click on Leave button in heads
        time.sleep(2)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\wfh_attendance.png',1)      # MAIN DROP DOWN FOR ALL QUERIES , NEEDS TO BE CLICKED FIRST , THEN DO SUB OPERATIONS
        time.sleep(2)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\attendance_request.png',1)   # we click on attendance request to mark the attendance
                                                                                                                                                                                            # time.sleep(2)       # just in case u missed 2 days , uncomment it | and mark iT
                                                                                                                                                                                            # navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\add_yellow.png',1)
        time.sleep(2)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\save_blue.png',1)                                            # save the attendance
        time.sleep(2)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\ok_blue.png',1)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\ok_light_blue.png',1)
        # time.sleep(4)
        # navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\wfh_attendance.png',1)      # MAIN DROP DOWN FOR ALL QUERIES , NEEDS TO BE CLICKED FIRST , THEN DO SUB OPERATIONS
        # time.sleep(4)
        # navigate_to_image(r'pics\wfh_attendance_list.png',1)                                   # here we check and conform our attendance
        print('\n\n Welcome to Connect fortclient \n\n')


    def tcube(self):
        """ Connect to TCube """
        time.sleep(3)
        print('\nOpening Timesheet in  Tcube')
        try:
            response = requests.get(self.TCUBE_URL)
            print('Welcome to Tcube \n')
            
        except Exception:
            exit('\nError: Could not open Tcube URL\n')
        
        web.open(self.TCUBE_URL) if response.status_code == 200 else print('Check the URL \n')
        time.sleep(5)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\login_blue_white.png',2)
        time.sleep(5)
        try:pyautogui.doubleClick(r'C:\Users\Tushar\Desktop\python\pics\timesheet_blue.png')
        except:self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\timesheet_blue.png',1)     # click on time sheet on both ocassions
        time.sleep(5)
        pyautogui.click()
        pyautogui.scroll(-200)
        time.sleep(3)
        print('Weekday is ',datetime.datetime.today().weekday() + 1 )
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\PQ_ENV_training_black.png',0,200 + ( (datetime.datetime.today().weekday()) * 70),-10  )
        pyautogui.click()
        pyautogui.write('8.5')
        time.sleep(3)
        pyautogui.scroll(-500)
        self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\save_blue_2.png',2)    # click on save button to save the attendance
        print('Done, Marked attendance in  Timesheet of Tcube as well')


    def main(self):
        """ Connect to fortclient twice 
        # If not connected at first time 
        and tcube at the end  """
        self.mark_attendance() if self.connect_fortclient() else print('\nIm not Sure whether Im connected to fortclient or not !\t'),
        print('Let me Check and connect it again')
        self.connect_fortclient(),self.mark_attendance()
        os.startfile(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\FortiClient VPN\FortiClient VPN.lnk")
        while True:
            time.sleep(1)
            print('Need to Disconnect from Fortclient inorder to access tcube')
            if self.navigate_to_image(r'C:\Users\Tushar\Desktop\python\pics\disconnect_blue.png',1):
                print('\n\nDisconnected from Fortclient')
                break
        time.sleep(10)
        self.tcube() 

person1 = Think_palm('Tushar')
person1.main()



