'''            Fortclient Connect        '''
import time 
import pyautogui 
import pyautogui as pt
from  credentials import all_credentials

def navigate_to_image(image, clicks, off_x = 0, off_y = 0):
     """   image is the image to be searched for, 
           clicks is the number of times to click, 
           off_x and off_y are the offset from the center of the image 
           x == right horizontal, y == vertical MOVE
     """
     try:
          position = pt.locateOnScreen(image, confidence = .8)
     except:
          return f'\n{image}\n Image not found or Image is corrupted'
     if position is None:
          print(f'{image} \nImage Not Found')
     else:
          pt.moveTo(position, duration = .5)
          pt.moveRel(off_x, off_y, duration = .2)
          pt.click(clicks = clicks, interval = .1)

pics_dir = all_credentials['pics_dir']

class FortClientConnect():

     def __init__(self,name):
          self.username = name

     def confirmation(self):
          ''' confirmation of the  global protect vpn connection '''
          pyautogui.press('win')
          time.sleep(1)
          pyautogui.write('fortiClient VPN')
          time.sleep(1)
          pyautogui.press('enter')
          time.sleep(3)
          image = (pyautogui.locateOnScreen(fr'{pics_dir}\\connect_fortclient.png'))

          print(image)
          pyautogui.moveTo(image, duration = .5)
          if image : # Yet to connect fortclient VPN
               print('\nNot Connected to fortclient vpn Yet , Ill Connect \n ')
               return False
          else:
               print("\n[*]Successfully Connected to fortclient  VPN \n")
               time.sleep(5)
               return  True


     def run(self):
          ''' 
          Open  and connect to globalProtect VPN 
          thus calling my number in the end  '''

          # pyautogui.press('win')
          # time.sleep(1)
          # pyautogui.write('fortclient vpn')
          # time.sleep(1)
          # pyautogui.press('enter')
          time.sleep(3)
          # pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\connect_fortclient.png'))
          
          pyautogui.doubleClick()

          pyautogui.press('left')
          pyautogui.press('enter')


          time.sleep(20)
          
          print("[*]\tConnected Successfully to fortclient VPN \t\n")

          return True
          

     def main(self):
          ''' running the main program 
          for this file only * '''
     
          if not self.confirmation():  return self.run() 
          self.confirmation()


if __name__ == '__main__':

     tushar = FortClientConnect(all_credentials['outlook']['username'])
     tushar.main()