import os,time,datetime,shutil,webbrowser,time,keyboard
from time import sleep
import pyautogui
from os import path
from win10toast import ToastNotifier
from BOT import send_notification
from selenium import webdriver
from selenium.webdriver.common.by import By

class Mail():

     def mail(self):
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
          os.chdir(r'C:\Users\Tushar\Downloads')
          for each_file in (os.listdir()):
               if each_file.startswith('Pay'):
                    shutil.move(each_file,DESTINATION)
                    print('\nDone')
                    send_notification('PDF','Your Pdf for current month has been downloaded to the documents directory for ThinkPalm')
               else:
                    break
          print('\nCouldn"t Find any file related to payslips Yet, Please check your mail')
     
     
     def main(self):
          # self.mail()
          self.move_pdf_files()
          # exit()

if __name__ == '__main__':
     obj1 = Mail()
     obj1.main()