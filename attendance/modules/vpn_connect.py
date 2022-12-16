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

class Connect():


     def __init__(self,name):
          self.username = name


     def confirmation(self):
          ''' confirmation of the  global protect vpn connection '''
          pyautogui.press('win')
          time.sleep(1)
          pyautogui.write('globalProtect')
          time.sleep(1)
          pyautogui.press('enter')
          time.sleep(1)
         
          # import pdb;pdb.set_trace()

          if (pyautogui.locateCenterOnScreen(fr'{pics_dir}\\connected_global_vpn_2.png', confidence=0.7)) is  None: # if not image found  ? result == false; vpn == not connected
               print('\nNot Connected to global Protect vpn\n ')
               return False
         
          else:
               print("\n[*]\tSuccessfully Connected to Global Protect VPN \n")
               time.sleep(5)
               return  True


     def run(self):
          ''' 
          Open  and connect to globalProtect VPN 
          thus calling my number in the end  '''

          pyautogui.press('win')
          time.sleep(1)
          pyautogui.write('globalProtect')
          time.sleep(1)
          pyautogui.press('enter')
          time.sleep(1)
          try: pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\connect_blue_btn.png'))
          except:pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\connect_blue_white.png'))
          time.sleep(20)
          
          print('\n[*]\tClicking on the Requested Id\n',)
          # import pdb; pdb.set_trace()

          # pyautogui.click(x=393, y=368)
          time.sleep(3)
          # import pdb;pdb.set_trace()
          # print(pyautogui.locateCenterOnScreen(f'{pics_dir}\\tushar_riverbed_email.png',confidence = .8))
          # print(pyautogui.locateCenterOnScreen(f'{pics_dir}\\tushar_riverbed_email_2.png',confidence = .8))
          # try:
          if pyautogui.locateCenterOnScreen(f'{pics_dir}\\tushar_riverbed_email.png',confidence = .8):
               pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\tushar_riverbed_email.png',confidence = .8))
          elif pyautogui.locateCenterOnScreen(f'{pics_dir}\\tushar_riverbed_email_2.png',confidence = .8) :
               pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\tushar_riverbed_email_2.png',confidence = .8))
          else:
               pyautogui.click(x=645, y=394)   #  Second place id"s coordinates 
          time.sleep(5)
          # import pdb; pdb.set_trace()
          # print(pyautogui.locateCenterOnScreen(f'{pics_dir}\\sign_in_blue_2.png',confidence = .8))
          try:
               pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\sign_in_blue_2.png', confidence = .8   ))
          except:
               pyautogui.press('enter') 
          try:
               pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\yes.png', confidence = .8   ))
          except:
               pyautogui.press('enter')
          from find_new_builds import send_notification
          send_notification('You have 30 seconds to approve the request','Accept Connection from phone',10)
          time.sleep(40)
          print('Done ')
          print("\n[*]\tAccept Connection from Your Phone\n")
          return True 
          

     def main(self):
          ''' running the main program 
          for this file only * '''
          # self.confirmation()
          if not self.confirmation():  return self.run()
          # self.run()


if __name__ == '__main__':

     tushar = Connect(all_credentials['outlook']['username'])
     tushar.main()