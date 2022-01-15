import webbrowser,datetime,time,os,pyautogui
from BOT import speak
try:
     def check_in_out(checout_image):
          try:
               url='https://people.zoho.in/deqode/zp#selfservice/user/attendance'
               webbrowser.open_new_tab(url)
               print('Performing ',checout_image)
               time.sleep(35)
               pyautogui.click(checout_image)
          except:
               try:
                    pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\refresh.png')
                    pyautogui.moveTo(100,150)
                    time.sleep(15)
                    pyautogui.click(checout_image)
                    print('\nPerforming ',checout_image)
               except:
                    time.sleep(10)
                    pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\cross.png')
                    pyautogui.moveTo(200,150)
                    pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\refresh.png')
                    pyautogui.moveTo(200,150)
                    time.sleep(15)
                    pyautogui.click(checout_image)
                    print('\nPerforming ',checout_image ,' again')

     # at 10 am CHECK_IN
     [check_in_out(r'C:\Users\Tushar\Desktop\python\pics\checkin.png') if datetime.datetime.now().hour >=10 and datetime.datetime.now().hour < 12 else print(f'\nTime gone to checkin - between ( 10 - 12 AM) \t do it manually now\n '),time.sleep(5)]
     print('Done\n\n')
     # at  8 pm CHECK_OUT
     [check_in_out(r'C:\Users\Tushar\Desktop\python\pics\checkout.png') if datetime.datetime.now().hour >=20 else print(f'\nTime left to checkout , will be done at 8 pm now'),time.sleep(5) ]



     # print(datetime.datetime.now().hour)
except:
     speak('Going to do it one final time now')
     check_in_out(r'C:\Users\Tushar\Desktop\python\pics\checkin.png') if datetime.datetime.now().hour >=10 and datetime.datetime.now().hour < 12 else print(f'\nTime gone to checkin - between ( 10 - 12 AM) \t do it manually now\n '),time.sleep(5)
     [check_in_out(r'C:\Users\Tushar\Desktop\python\pics\checkout.png') if datetime.datetime.now().hour >=20 else print(f'Time left to checkout , will be done at 8 pm now'),time.sleep(5) ]

