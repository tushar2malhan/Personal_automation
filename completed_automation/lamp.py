import pyautogui , keyboard
import datetime,time,shutil,os

from PIL import ImageGrab,Image
import pytesseract as tess
tess.pytesseract.tesseract_cmd =r'D:\Program Files\Tesseract-OCR\tesseract.exe'

from win10toast import ToastNotifier
from BOT import speak,takeCommand



# for opening Mobile app
bluestack_cords=pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\Desktop\python\pics\bluestack.png')
result =   None

def delete_files_directory(dir):       
     """ directory of all screenshots to be deleted at the end of the day 
          # dir == directory """
     #    Delete the pics in the directory for the current day 
     dir = r'C:\Users\Tushar\Desktop\python\pics\temp'   
     for files in os.listdir(dir):
        print(files)
        path = os.path.join(dir, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)


def close_app():
     time.sleep(5)
     pyautogui.click(bluestack_cords)
     try:
          pyautogui.click(r"C:\Users\Tushar\Desktop\python\pics\cross.png")
     except:
          pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\crosss.png')
     pyautogui.click(r"C:\Users\Tushar\Pictures\Screenshots\close.png")


def power_button():
     """ check and REVERSE power button ON or OFF button    | will save the NEW screenshot as well , Chcek and create new val for power button """
     time.sleep(4)
     snapshot = ImageGrab.grab()
     snapshot.save(fr'C:\Users\Tushar\Desktop\python\pics\temp\sample_{datetime.datetime.today().day}.png')
     img = Image.open(fr'C:\Users\Tushar\Desktop\python\pics\temp\sample_{datetime.datetime.today().day}.png')
     text = tess.image_to_string(img).split('\n')
     # text = tess.image_to_string(img)
   
     for each_word in text:
          if each_word in ['Power Off','Off','Power Off -'] or each_word.endswith('Off') :
               global result
               result = True
     if result :
          speak('Turning the light on')
          print(1,'Turning the light on') 
          try:
               pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\off_btn.png')
          except TypeError:
               speak('soRRY , im not  able to find switch off button so cant click the switch Off button')
     else:
          print(2,'the switch is already on \n turning it off ')
          speak('the switch is already on \n turning it off ')
          try:
               pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\on_btn.png')
          except:
               speak('cant click the switch on button')
          

def lights():

     wipro_lights=r'C:\Users\Tushar\Desktop\python\pics\lights2.png'    # click wipro next smart home
     
     # if datetime.datetime.now().hour >= 19:
     #      speak('Its pretty late now , Lets turn on the lights')
     try:
          pyautogui.click(bluestack_cords)
     except :
          print('Changing the screen , i couldnt find the app')
     #  SHOW DESKTOP IF ANY ERROR OCCURS WHILE FINDING THE SCREEN
          pyautogui.click(x=1364, y=746)
          pyautogui.click(bluestack_cords)
     time.sleep(25)
     pyautogui.click(wipro_lights)
     time.sleep(15)
     
     pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\plug_lights.png') # turn plug
     time.sleep(10)
     
     # import pdb; pdb.set_trace()
     #    Switch on the power button if its off 7 PM   
     power_button()
     speak('Do you want to switch on the power button')
     user_input = takeCommand()
     if user_input  in ['yes', 'ok','alright','ok done','kardo','yes yes'] :
          pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\off_btn.png')
          speak('The power is switched on now')

     time.sleep(2)
     # #     minimize the app
     pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\minimize_blustack.png')  

     # speak('Deleting file for today as well')
     delete_files_directory(dir)

     # close the app
     # close_app()
     

   

if __name__ == '__main__':
     lights()


