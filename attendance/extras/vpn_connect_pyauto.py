'''            Use it only if Your VPN connects on browser  because my vpn verification works Differently 😅 '''
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
          # print(pyautogui.locateCenterOnScreen(fr'{pics_dir}\\connected_global_vpn.png'))
          if (pyautogui.locateCenterOnScreen(fr'{pics_dir}\\connected_global_vpn.png')) is  None: # if not coodinates martch with image ? result == false
               print('\nNot Connected to global Protect vpn\n ')
               return False
          else:
               print("\nSuccessfully Connected to Global Protect VPN \n")
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
          pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\connect_blue_white.png'))
          time.sleep(15)
          
          print('\nClicking on the Requested Id',)
          # after password written we sign in 
          # pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\signin_blue.png.png'))
          time.sleep(2)
          # try:          pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\jjj_id_2_white.png'))
          # except: ...
          pyautogui.press('enter')
          time.sleep(2)
          pyautogui.click(708, 434)
           
          pyautogui.press('enter')
          # try:    pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\signin_blue.png.png'))
          # except: print("password already entered")
          time.sleep(2)
          print('Clicking on Your Number +72\tWaiting for 30 secs to click the checkbox')
          pyautogui.click(680, 467) 
          time.sleep(10)
          pyautogui.click(500, 467) 
          pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\check_box_black_white.png'))
          print('Checkbox clicked')
          time.sleep(2)
          pyautogui.press('enter')
          time.sleep(25)
          
          # click on the password field
          # print(pyautogui.locateCenterOnScreen(f'{pics_dir}\\type_password.png'))
          # navigate_to_image(f'{pics_dir}\\type_password.png',2)         
          # pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\type_password.png'))
          # print(pyautogui.locateCenterOnScreen(f'{pics_dir}\\type_password_2.png'))
          # navigate_to_image(f'{pics_dir}\\type_password_2.png',2)
          # pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\type_password_2.png'))
          
          # time.sleep(1)
          # pyautogui.write(all_credentials['globalProtect']['password']),print("Written the password 😁") 
          # pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\signin_blue.png'))
          # pyautogui.press('enter')
          # time.sleep(15)
          # print('Lets check if I can see your number ending with 72 ')
          # pyautogui.scroll(-1000)
          # time.sleep(2)
          # pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\72_num.png')) if (pyautogui.locateCenterOnScreen(f'{pics_dir}\\72_num.png')) is not None else print('\nSorry cant see your number ending with 72\n ')
          # pyautogui.click(pyautogui.locateCenterOnScreen(f'{pics_dir}\\72_num_2.png')) if (pyautogui.locateCenterOnScreen(f'{pics_dir}\\72_num_2.png')) is not None else print('\nSorry cant see your number ending with 72\n ')
          # pyautogui.click()
          # time.sleep(35)
          time.sleep(15)
          print("Connected Successfully to Global protect VPN \t")
          

     def main(self):
          ''' running the main program 
          for this file only * '''
          
          if not self.confirmation():  self.run()


if __name__ == '__main__':

     tushar = Connect(all_credentials['outlook']['username'])
     tushar.main()