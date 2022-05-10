import os,time,datetime,shutil,webbrowser,time,keyboard
from time import sleep
import pyautogui

import time
import sys 
import pyautogui
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from Protected import credentials
username = credentials.all_credentials['think_palm_username']
password = credentials.all_credentials['fortclient_password']


option = Options()

option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")

# REMOVE POP UP NOTIFICATIONS 
option.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 1 
})
path_to_chromedriver = r"C:\Users\Tushar\Downloads\chromedriver.exe"
class Mail():
     
     driver = webdriver.Chrome( chrome_options=option,executable_path=f"{path_to_chromedriver}"  )
    

     def gmail(self):
          """
          open ur pdf's from mail and download it in your local machine
          """
          url ='https://mail.google.com/mail/u/0/#inbox'

          webbrowser.open_new_tab(url)
          time.sleep(7)
          try:pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\search_mail_3.png')
          except:pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\search_mail_2.png')
          pyautogui.typewrite('Payslips')
          keyboard.press('enter')
          time.sleep(4)
          pyautogui.doubleClick(r'C:\Users\Tushar\Desktop\python\pics\pdf.png')
          time.sleep(2)
          try:pyautogui.moveRel(170, -59, duration=1.5),pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\download.png')
          except TypeError: pyautogui.moveRel(170, -59, duration=1.5),pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\download_2.png')
          time.sleep(2)
          pyautogui.click(r'C:\Users\Tushar\Desktop\python\pics\save.png')     
          time.sleep(5)


     def move_pdf_files(self):
          """  
               Move pdf files from downloads to DESTINATION dir
          """
          DESTINATION = r"C:\Users\Tushar\Documents\salary_slips_thinkPalm"
          MUSIC_DESTINATION = r"C:\Users\Tushar\Music"
          os.chdir(r'C:\Users\Tushar\Downloads')
          for each_file in (os.listdir()):
               if each_file.startswith(tuple(['Pay','payslips'])):
                    shutil.move(each_file,DESTINATION)
                    print('\nDone')
                    send_notification('PDF','Your Pdf for current month has been downloaded to the documents directory for ThinkPalm')
               elif each_file.endswith('mp3'):
                    shutil.move(each_file,MUSIC_DESTINATION)
                    send_notification('Music File',f'{each_file} Successfully Moved')
               else:
                    ...
          print('\nCouldn"t Find any file related to payslips Yet, Please check your mail')
     
     def outlook(self):
          self.driver.get('https://outlook.office.com/mail/')
          login = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "loginfmt")))
          login.send_keys(username)
          time.sleep(3)
          self.driver.find_element(By.ID,'idSIButton9').click()
          passwd = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "passwd")))
          passwd.send_keys(password)
          time.sleep(3)
          self.driver.find_element(By.ID,'idSIButton9').click()
          
          # checkbox and submit
          self.driver.find_element(By.XPATH,'/html/body/div/form/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div[2]/div/div[3]/div[1]/div/label/input').click()
          self.driver.find_element(By.ID,'idSIButton9').click()
          time.sleep(3)
          search_bar = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[1]/div/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/div[1]/div/div[3]/div/input')))
          search_bar.send_keys('Monthly pay slip')
          # search button
          self.driver.find_element(By.XPATH,'/html/body/div[3]/div/div[1]/div/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/div[1]/button/span/i').click() 
          time.sleep(2)
          # self.driver.find_element(By.XPATH('/html/body/div[3]/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div/div/div/div/div[2]/div/div')).
          

          # click on pay slip class = _1LpdCXJNhBFxJf0rAReTyO
          # download id = id__404


     def main(self):
          # self.gmail()
          self.outlook()
          # self.move_pdf_files()
          # exit()

if __name__ == '__main__':
     obj1 = Mail()
     obj1.main()