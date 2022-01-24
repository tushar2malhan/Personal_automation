import time
import pyautogui


# for opening Mobile app
def click_app(app):
    ''' click bluestack and click jio '''
    bluestack_cords = pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\Desktop\python\pics\bluestack.png')
    try:
        pyautogui.click(bluestack_cords)
    except:
        #       SHOW DESKTOP IF ANY ERROR OCCURS WHILE FINDING THE SCREEN
        print('Changing the screen , i couldnt find the app')
        pyautogui.click(x=1364, y=746)
        pyautogui.click(bluestack_cords)
    time.sleep(25)
    #           Click on APP in BLUE STACK
    pyautogui.click(pyautogui.locateCenterOnScreen(app))
    time.sleep(15)

# click_app(r'C:\Users\Tushar\Desktop\python\pics\jio_tv_pic.png')

