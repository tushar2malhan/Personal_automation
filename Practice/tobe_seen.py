
import os
from gtts import gTTS
import speech_recognition as sr


para = '''
Calculate the mean score of all users.                                            # sum([ i['age'] for i in Student.objects.all().values('age')  ])/2   
Find the user with the highest score.                                             # Student.objects.order_by('-age')[:1].values('age')[0]    
Find if there is any user with score less than 2 (return True/False)              #  User.objects.filter(age__lt=20).exists()           |  [True if Student.objects.filter(age__lt=20) else False]     | 
Find all the users which have score exactly equal to the mean score.              # Student.objects.filter(age=sum([ i['age'] for i in Student.objects.all().values('age') ])//2)
Change the score value of all users in a single query to 100 (one hundred)        #
Find all the users which don't have score 10 or 20                                # Student.objects.exclude(age__in=[10,20,31])
Print a list of all the score values from all users excluding the first 10 users. # Student.objects.exclude(id__in=[i for i in range(10)]).values('age')
'''
# d={}
# words=para.split()
# for i in words:
#      if i not in d:
#           d[i] =0
#      else:
#           d[i] += 1

# # print(d)


# L=[1,2,4,5,0,6,0]
# def solve(L):
#      ''' Move all 0s to RHS '''
#      if len(L) == 0:
#           return L
#      k=0
#      for i in range(len(L)):
#           if L[i] !=0:
#                L[k] = L[i]
#                k+=1
#                print(L[i])
#      while k < len(L):
#             L[k] = 0
#             k+=1
    #  for o in range(k,len(L)):
    #       L[o] =0
#      return L 
# print(solve(L))


# print(    sorted(d.items() , key = lambda kv:(kv[1],kv[0])) )


# def hi(func):
#      print('hello this is the decorator ')
#      def wrapper(a):
#           print(f' calling {a} from inside the wrapper')
#           # return a+'hi'
#           return a   # this  refers to line 58 , where it gets called accordingly
#      return wrapper

# @hi
# def call(val):
#      print(val+'malhan')

# call('tushar')

# def input_name(func):
#      def wrapper(name):
#           name = input('Enter your name: ')
#           if name:
#                print(func(name))        # this will call decorated function,otherwise it has not meaning
#                return 'hi ' + name      
#           else:
#                return 'Please enter your name'
#      return wrapper

# @input_name
# def say(name):
#      return 'hi'+name
# print(say('malhan'))

# from chatterbot import ChatBot
# from chatterbot.trainers import ListTrainer
# from chatterbot.trainers import CHatterBotCorpus Trainer

# logic_adapters = (['chatterbot.logic.Mathematical Evalution',
# 'chatterbot.logic.BestMatch'])


# smalltalk = ['hi','hai','how do you do',
# 'hello','hai','hey','hi','how are you','hey buddy','you are great','your great','hay','ok'
# ]


# talk1= ['best thing ever to take place ']

# list_trainer= List Trainer (my_bot)
# for item in (smalltalk,talk1):
#      list_trainer.train(item)


# corpus_trainer = ChatterBotCorpus Trainer(my_bot)
# corpus_trainer.train('chatterbot.corpus.english')

# print(my_bot.get_response('hello'))

# from gtts import gTTS
# voice = ''

# while True:
#      e = sr.Recognizer()
#      with sr.Microphone() as source:
#           try:
#                audio = e. listen(source)
#                text = e.recognize_google(audio)
#                print(text)
#                if text == "stop":
#                     break
#                text = e.recognize_google(audio)
#                voice = voice+str(text)

#           except:
#                 print("say something")

# we = gTTS(text=voice, Lang='en', slow=False)
# we.save("A.wav")

# from GoogleNews import GoogleNews
# googlenews = GoogleNews( )
# googlenews = GoogleNews(period='/7d' )
# googlenews.search( 'IND' )
# result=googlenews.result( )

# for x in result:
#      print("-"*50)
#      print("Title--", x['title'])
#      print("Date/Time--", x['date'])
#      print("Description--", x['desc'])

#      print("Link--", x['link'])


""" #############################################################################################################################################################################"""
#                                 Shorter version of above code               
#                 just provide the class name and ask driver to find element by respective type and add the functionality inside get_values()

# no big functions , one main function  |  inside class 
# no comments for prod 

from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from openpyxl import Workbook  ,load_workbook
wb = Workbook()  
url="https://www.mercadona.es/"
postalcode='08013'

def web_scrap_automation(url,postcode,*classnames):
     driver = webdriver.Chrome(executable_path=r"C:\Users\Tushar\Downloads\chromedriver.exe")
     driver.get(url)
     print('\t\t',driver.title)
     
     def get_values(sheet_num,sheet_name,driver,*innerclasses):     # here innerclasses refers to each element we sent when outer func is called 
               sheet = wb.create_sheet(sheet_num)
               sheet.title = sheet_name 
               
               #   get the Name
               sheet[f'A{1}']="PRODUCTS"
               name_tag= driver.find_elements_by_class_name(innerclasses[0])
               for name in range(len(name_tag)):
                    sheet[f'A{name+2}']=name_tag[name].text
                    print(name_tag[name].text)

               
               #   get the Price
               sheet[f'B{1}']="PRICES"
               price_tag=driver.find_elements_by_class_name(innerclasses[1])
               for price in range(len(price_tag)):
                    sheet[f'B{price+2}']= price_tag[price].text
                    print(price_tag[price].text)

               #  getting the image link
               images = driver.find_elements_by_xpath(innerclasses[2]) 
               sheet[f'C{1}']="IMAGES"
               for image in range(len(images)):
                    sheet[f'C{image+2}']=images[image].get_attribute('src')
                    print(images[image].get_attribute('src'))

               # get the weight
               weights =driver.find_elements_by_class_name(innerclasses[3]) 
               sheet[f'D{1}']="WEIGHT"
               for weight in range(len(weights)):
                    sheet[f'D{weight+2}'] = weights[weight].text
                    print(weights[weight].text)
               print()
                    
               print(f'\n\nDone , Data extracted and saved in your excel for the {sheet_name}')

     try:
          #              convert to english language
          l0=driver.find_element_by_xpath("/html/body/div[1]/nav/div[2]/div/i")
          l0.click()
          l1=driver.find_element_by_xpath("/html/body/div[1]/nav/div[2]/div/ul/li[6]/button")
          l1.click()
          
          search_bar = driver.find_element_by_xpath('//*[@id="root"]/header/div/div/form/div/input')
          
          #                   give the postcode
          try:
               search_bar.send_keys(postcode)      
               search_bar.send_keys(Keys.RETURN)
               l2=driver.find_element_by_xpath('//*[@id="root"]/header/div/div/form/input')
               l2.click()
               accept= driver.find_element_by_xpath('//*[@id="root"]/div[1]/div/div/button[2]')
               accept.click()
          except:
               print('No way to pass postal code on the webpage')

          time.sleep(10)
          #                        DYNAMIC FROM HERE 

          get_values('sheet_1','LANDING_PAGE',driver,*classnames)
          print('\n\n')
     
          # #                      View the products from inside 
          product_button = driver.find_element_by_class_name('banner-item__button')
          product_button.click()
          time.sleep(10)

          get_values('sheet_2','INNER_PAGE',driver,*classnames)
          print('\n\n')

          driver.close()      
          filename = fr"C:\Users\DELL\Desktop\excel\file_{postalcode}.xlsx"                                                           
          wb.save(filename)                                                          # saving file to the excel 
          wb.remove(wb['Sheet'])
          wb.save(filename)  

     except Exception as e:
          print(f'Issue in the postal code ❌{postalcode}❌, check and verify it again')
          print(e)

# web_scrap_automation(url,postalcode,'product-cell__description-name','product-price__unit-price',"//div[@class='product-cell__image-wrapper']/img","product-price__extra-price",None)

""" #############################################################################################################################################################################""" 


#   HERE IF WE CAN COMMENT 2 FN CALL , WE CAN WEB SCRAPE ALMOST EVERY SITE 
######################################################################################################################################################

#    ubuntu multiple commands at once

# !wsl && cd /mnt/c/Users/DELL/Desktop/PYTHON/test/RealTimeObjectDetection/Tensorflow && git clone https://github.com/tensorflow/models

######################################################################################################################################################

     # Access variables from function

# global a : print(a)      
# create global variable  , use the same variable for the function , to call the global variable 
# inisde func => func.a =1  , when func called , print(func.a)

# use it to create global and local variables inisde function
# globals()             # will return all global variables 
# x = globals()['a']    # will return specific global variable outside the function which is a


########################################################################
#                        find and change words in a list of strings via indexing

# ' '.join([ followers[i-1] for i,word in enumerate(followers) if word == 'Followers'])


########################################################################

#                    change text from file 

# os.chdir(r'C:\Users\DELL\Desktop\personal\no_specs')
# list_files=[file for file in os.listdir() if file.endswith('txt') ] 
# # print(list_files)

# for file in list_files:
#      with open(file,'r+')as f:             # first read the file 
                                             
#           line = f.read()                  # create a new line with changes
#           change=(line.replace(''.join(line.split(' ')[0]) ,'0'))

# for file in list_files:
#      with open(file,'r+')as f:
#           ...
#           f.write(change)                   # perform

########                                      ###############################
# os.chdir(r'C:\Users\DELL\Desktop\personal\no_specs')
# list_files=[file for file in os.listdir() if file.endswith('txt') ] 
# # print(list_files)

# for file in list_files:
#      with open(file,'r+')as f:
#           line = f.read().split(' ')
#           # change 
#           line[0] ='0'
#           # print(line)
#           change =(' '.join(line))
#           # print(change)


# for file in list_files:
#      with open(file,'r+')as f:
#           ...
#           f.write(change)

########                                      ###############################
#           change text from file 
# os.chdir(r"C:\Users\DELL\Desktop\personal\specs")
# list_files=[file for file in os.listdir() if file.endswith('txt') and not file.startswith('classes') ] 
# # print(list_files)

# for file in list_files:
#      with open(file,'r+')as f:             # first read the file 
                                             
#           line = f.read().split('\n')                  # create a new line with changes
#           change= line[0].split(' ')
#           change[0] = '0' if change[0] == '15' else '1'
#           fchange =(' '.join(change))
#           # f.write(change)
         
# # for file in list_files:
#      with open(file,'r+')as f:
#           ...
#           print(fchange)
#           f.write(fchange)                  # perform


########################################################################
#                   Pass List Iterables in startswith ()
#       print( 1 if     ask.startswith( ('7','8','9') )     else 0 )
########################################################################
#                   flatten_dict


# def flatten_dict(dd, separator ='_', prefix =''):
#     return { prefix + separator + k if prefix else k : v
#              for kk, vv in dd.items()
#                     for k, v in flatten_dict(vv, separator, kk).items()
#              }           if isinstance(dd, dict) else { prefix : dd }

# initialising_dictionary
# ini_dict = {
#      'geeks1': {'Geeks1': {'for1': 7}},
#      'for2': {'geeks2': {'Geeks2': 3}},
#      'Geeks3': {'for3': {'for3': 1, 'geeks3': 4}}}

##################################################################################
#    EXTRACT PARTICULAR LINES FROM LIST      AS TXT FILE    from HTML file


# with open('part1.txt','r+') as f:
#      lines = f.readlines()
#      # print(lines.index('subhead1-r product-cell__description-name'))                   # what line we need to add index
#      # c=0
#      for num , line in enumerate(lines):
#           if 'subhead1-r product-cell__description-name' in line:                       # if that line exists
#                # c+=1
#                print(lines[num+1].split('data-test="product-cell-name">')[1].split('</h4>')[0])        # print and extract values from list 
#      # print(c)
##################################################################################
              
#        list_files=[file for file in os.listdir() if file.endswith('.jpg') and 'no' in file ] 
#          f.write(line.replace(''.join(line.split(' ')[0]) ,'0'))

#          Move files from one directory to another
# import shutil, os
# files = ['file1.txt', 'file2.txt', 'file3.txt']
# for f in files:
#     shutil.move(f, 'dest_folder')


'''  get specific files from a directory and move to another directory '''

# def get_all_jpg_files():
#     import os
#     os.chdir(r'C:\Users\Tushar\Desktop\Personal\personal\images\specs')
#     import glob
#     jpg_files = glob.glob('*.jpg')
# #     print(jpg_files) 
#     import shutil
#     # C:\Users\Tushar\Desktop\Personal\personal\all_images
#     for i in jpg_files:
#      #    os.rename(i,i.replace(' ','_'))
#      #    print(i)
#         shutil.move(i, r'C:\Users\Tushar\Desktop\Personal\personal\all_images')

# get_all_jpg_files()

##################################################################################
#         CONVERT FILE EXTENSION 
# from PIL import Image
# import os
  
# # importing the image 
# im = Image.open("geeksforgeeks.png")

  
# # converting to jpg
# rgb_im = im.convert("RGB")
  
# # exporting the image
# rgb_im.save("geeksforgeeks_jpg.jpg")


#         FOR MULTIPLE FILES
# from PIL import Image
# import os
# import os,shutil
# os.chdir(r'C:\Users\DELL\Desktop\JPEG I mages')
# old_l=os.listdir()
# for file in old_l:
#      name=file.split('.')[0]
#      im = Image.open(file)
#      rgb_im = im.convert("RGB")  
#      rgb_im.save(name+'.jpg')
#      os.remove(file)

################################################################

#                       EXTRACT TEXT AND READ IT FROM PDF FILES 
# import pyttsx3,PyPDF2

# book = open(r"D:\Work\statements\M1797 _Apr 2021.pdf", 'rb')
# pdfReader = PyPDF2.PdfFileReader(book)
# pages = pdfReader.numPages

# speaker = pyttsx3.init()
# # print(pages)
# for num in range(pages):
#      page = pdfReader.getPage(num)
#      text = page.extractText()
#      speaker.say(text)
#      speaker.runAndWait() 
#      #print(1,text)    

################################################################
#               NESTED LOOP PRACTICE

# real life example of nexted loop  CLOCK 
# for hour in range(1,25):
#      for minute in range(1,61):  # 60 sec > 1 min > 60 min ? 3600 hour 
#           for second in range(1, 61):
#                import time ; time.sleep(1)
#                print(second)
#           print()
#           print(f'{minute} minute done')
#           print()
#      print()
#      print(f'{hour} hour done')
#      print()


# matlab i ek SAATH SAATH badh , each j iteration stores i'th iteration  (1, 22, 333, 4444 ....)
#         for j in range(i) 
# with i here j will be keep on Increasing  | 
# because range starts from i so j == (0,4)  , i == 1  j == (1,4)   ,i == 2 j ==(2,4)

# means NEGATIVE loop for inner iteration as it starts from (1,10) then j == (2,10) (3,10) ...
#         for j in range(i+1,10)             | for j in range(i-1)  == positive loop


##################################################################################

#                   Review of classes 
# class variables                = shared by all instances 
# class initilization (__init__) = multiple variables with different arguments  (multple children having different names or abilities)


'''                     DUNDER METHODS IN DETAIL       27-04-2022     '''

class check():
    '''These magic dunder methods are made for the object's funcationality only 
    suppose __getitem__ => a[0] 
            __len__     => len(a) 
            __call__    => a() '''
    def __init__(self,item) -> None:
        self.a = 123456789
        self.b = 2
        self.c = 3
        self.item = item
        # print(self.item)
    
    def __getitem__(self, index):
        ''' suppose  a is the object of class check and
        we want to get the value of a[0] 
        we can use this method to get the value of a[0]
        else it cant subscribe to the object of class  check and throw error
        print(a[0])'''
        return self.item[index]


    def __len__(self):
        ''' when u call object with len() method it will return the length of the object
        called from here 
        print(len(a))'''
        return len(['1',2,3])


    def __call__(self):
        ''' a()   like a function '''
        print(self.a)
        print(self.b)
        print(self.c)
    

    def __str__(self):
        ''' preference given first when object is printed as compared to __repr__
        print(a)'''
        return 'this is a string'


    def __repr__(self):
        '''print(a)'''
        return 'this is a repr'
    

    def __del__(self):
        ''' when object is deleted 
        if not   del a   >>>  print(a) >> will give __str__ + __del__  print() function'''
        # print('object deleted')


    def __add__(self, other):
        '''  
        where 2 objects a and b item and other gets added  
        print(a+b)  
        '''
        return self.item + other.item
    

    def __mul__(self,other):
        return self.item * 2 + other.item *2


# a = check('item')
# difference between __call__ and __str__
# __call__ is used to call the object
# __str__ is used to print the object

# a()                        # this will call the __call__ method
# print(len(a))              # this will call the __len__ method 
# print(a)                   # if __str__ then this will call the __str__ method else repr
# del a                      # call __del__ method when object is deleted

# b = check('2 item')          # b object created to add a(item) and b(2 item)
# print(a+b)                   # this is how it will add 2 objects values together
# print(a*b)                    # same case to multiply 2 objects values together



################################################################## PROBLEMS  ##############################################################################


#           assign 3 iterations from letters to each number in range(2,10)

letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def assign():
     for i in range(len(letters)):
          print(letters[i],end='\n'if i % 3 == 0 and i !=0  else '  ')
          
# assign()
################################################################## TRICKY ##########################################################

# send  unknown message on whatsapp
# API = 'https://api.whatsapp.com/send?phone=917984309091&text=hello'
# https://api.whatsapp.com/send?phone=+917814891872

############################################################################################################################
#                        Multiple Expressions in if else in one line 

# mark_attendance() if connect_fortclient() else print('\nLet me connect to fortclient first\t'),print('\nYour Connected to FortClient\nNow lets mark the attendance\n'),mark_attendance()
     
#                        Check if name endswith with values given in list 

#  if  kingdom_name.endswith (tuple(i for i in [ 'a', 'e', 'i', 'o', 'u'] ))


############################################################################################################################
#                                                   GIT   HELP

#         Add git ignoring credentials file                                                                                                                   

# use gitignore to ignore the credentials file
# inside .gitignore > /dir/main_dir/          

# git add . 
# git commit -m "" 
# git push origin           >>> will ignore all  the directory or file

# SO WHEN U PUT FILE IN GITIGNORE , YOU WONT SEE THE FILE IN GIT STATUS   {  no relative path allowed , only absolute path }
# git rm --cached <foldername>   incase folder dosent show up in repository

############################################################################################################################
# git checkout -- filename.py      [ before git add . ]     >>> undo the latest changes you just did !     ( or do . to undo all changes in all files )
# git revert  hashcode             [ after git commit ]     >>> undo the changes and with the current changes in ur files , it will bring back old changes
#                                                              ( like with my new updated code in fortclient it brought back old README.MD file which was deleted )
#                     ** SENSITIVE COMMAND **
# git reset --hard hashcode        [ after git commit ]     >>> will forceibly make your directory take back in time  with that git commit ,so all the current commits and files will be lost  permanently

############################################################################################################################


# Dated             19-01-2022 
#          web scrap data from social media like instal, db , linkedin and twitter
# Get profile pic , username , followers and posts if valid Username Persists

#                   18-03-2022
import time
import sys 
import pyautogui
from selenium import webdriver
# from completed_automation.Protected import credentials 

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

option = Options()

option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")

# REMOVE POP UP NOTIFICATIONS 
option.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 1 
})


# linkedin_email = credentials.all_credentials['linked_email']
# linkedin_password = credentials.all_credentials.get('linked_password')


def user_information(username):
    u_input = input("Which Social Media account  would you require information for ?: \n\n\
    \t Instagram \t Facebook \t Twitter \t Linkedin \n").lower().strip()

    
    """ Display user information from
    their social media accounts """
   
    driver = webdriver.Chrome(
    chrome_options=option,executable_path=r"C:\Users\Tushar\Downloads\chromedriver.exe")
    
    def block_page():
            ' WANNA Block any FB page ?  '
            
            #               3 button Option
            ''' Since element is not interactable, we use driver.execute_script() to click the button '''
            print()
            print(1)
            try:
                print('Clicked 3 button Options')
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[3]/div/div/div/div[2]/div/div/div[3]/div/div/div[1]"))))
            except Exception as e:
                print(e)
                ...
                print('1 not respond')
            time.sleep(2)

          
            #                  Report Page     :->     As page will be not be clickable sometimes , we start with 1 step from except Block !
            print(2)
            try:
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[6]/div[2]/div/div/span"))))
                print('Report Page')
            except Exception as e:
                print('try to click  2 button again with 1 button ')
                WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[3]/div/div/div/div[2]/div/div/div[3]/div/div/div[1]'))).click()
                WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[6]/div[2]/div/div/span'))).click()
                print('\n\n ',e)
            time.sleep(2)
          
          
            #                  Fake Page
            print(3)
            try:
                # driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div/div[2]/div/div/div[4]/div/div/div/div[1]/div/div[1]/div/div/div/div/span').click()
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div/div[2]/div/div/div[4]/div/div/div/div[1]/div/div[1]/div/div/div/div/span"))))
                print('Fake Page')
            except:driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[3]/div/div[2]/div/div/div[6]/div/div/div/div[1]/div').click()
            time.sleep(2)
           
           
            #               Something Suspecious          
            try:
                print('Called Suspecious Button ')
                # driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div/div[2]/div/div/div[2]/div/div/div/div[1]/div/div[1]/div/div/div/div/span').click()
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div/div[2]/div/div/div[2]/div/div/div/div[1]/div/div[1]/div/div/div/div/span"))))
            except: driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div/div[2]/div/div/div[4]/div/div/div/div[1]/div/div[1]/div/div/div/div/span').click()
            time.sleep(2)
           
           
            #               Submit
            print(4)
            try:
                print('Submitted')
                # driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div[2]/div/div/div/div/div[1]/div/span/span').click()
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div[2]/div/div/div/div/div[1]/div/span/span"))))
            except:driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div[2]/div/div/div/div/div[1]/div/span').click()
            time.sleep(2)
            
            
            #               Done
            print(5)
            try:
                print('DONE ')
                # driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div[2]/div/div/div/div/div[1]/div/span/span').click()
                driver.execute_script("arguments[0].click();", WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div[2]/div/div/div/div/div[1]/div/span/span"))))
            except: driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div[4]/div[2]/div/div/div/div').click()
            time.sleep(2)
       

    try:
        if u_input.startswith('i'):
            print('Instagram\n')
            url = f"https://www.instagram.com/{username}/"
            driver.get(url)
            name = driver.title
            try:
                name = driver.find_element(By.CLASS_NAME,'XBGH5').text
            except:
                name = driver.find_element(By.XPATH ,'//*[@id="react-root"]/section/main/div/header/section/div[1]/h2').text
                name = driver.find_element(By.CLASS_NAME,'_2s25').text
            try:
                profile_pic = driver.find_element(By.CLASS_NAME, "be6sR").get_attribute('src')
            except:
                profile_pic =driver.find_element(By.CLASS_NAME, "_6q-tv").get_attribute('src')
            try:
                total_posts = driver.find_element(By.CLASS_NAME, "g47SY").text
            except:
                print('Couldnt fetch the total posts of the User from Instagram')
            try:
                followers = driver.find_element(By.CLASS_NAME, "_81NM2").text
            except:
                followers = driver.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').text
            # data[f'total_posts_of_{username}'] = total_posts
            # data[f'followers_of_{username}'] = followers
            
            # print(f'Profile pic URL is \t',profile_pic,end='\n\n')
            print(f'Total posts are \t',total_posts,end='\n\n')
           
        
        elif u_input.startswith('f'):
            print('Facebook\n')
        
            url = f"https://www.facebook.com/"
            driver.get(url)
            
            """ here we try to find element by class name by looking at page source and we get attribute
                 we make some time with sleep so that it doesn't break the code'
                 xlink:href  is the attribute of the image we want from FB 
                 IF U DONT FIND UR USERNAME HERE , TRY USING name.sername
                 name = driver.title """
           
            """ LOGGED IN FIRST """
            # login button
            time.sleep(5)
            try:driver.find_element(By.XPATH,('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[2]/div/div/div/div[2]/div/div[1]/div/a/div/div[1]')).click()
            except: ...
            driver.find_element(By.ID,'email').send_keys(credentials.all_credentials['fb_email'])
            driver.find_element(By.ID,'pass').send_keys(credentials.all_credentials['fb_password']+Keys.ENTER)
            
            try:driver.find_element(By.CLASS_NAME,'_6ltg').click()
            except:print(' logged in ')

            
            
            ''' SEATCH BOX FOR USERNAMES '''
            # time.sleep(10)
            # search_box = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div/label/input')
            # search_box.click()
            # search_box.send_keys(username)
            # search_box.send_keys(Keys.RETURN)
            

            # NOW LOGEGD IN WITH USERNAME SUCCESSFULLY
            url = f"https://www.facebook.com/{username}"
            driver.get(url)

            ''' Blocking the page '''
            driver.minimize_window()
            def recursive_attack_on_a_page():
                try:
                    while 1:
                        try:block_page() if u_input.startswith('f') else 'break'
                        except:block_page() 
                except:
                    while 1:
                        try:block_page() if u_input.startswith('f') else 'break'
                        except:block_page() 
           
            try:recursive_attack_on_a_page()
            except:recursive_attack_on_a_page()
   


            name = driver.title         # .split('Facebook')[0].split('|')[0]
            time.sleep(10)

            profile_pic = [i.get_attribute('xlink:href') for i in driver.find_elements(By.TAG_NAME,"image")]
            time.sleep(2)
            if profile_pic == []:
                profile_pic = driver.find_element(By.CLASS_NAME,'_2dgj').get_attribute('href')
               
            try:
                # this for a PAGE in fb, u get number of followers from the page
                followers_of_page =[i.text for i in driver.find_elements_by_css_selector('.'+'.'.join('d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh jq4qci2q a3bd9o3v b1v8xokw oo9gr5id'.split(' '))) if i.text.endswith('like this')]
                if followers_of_page :
                    print('Total followers of page are ',''.join(   followers_of_page     ))
                    followers = followers_of_page[0].split(' ')[0]
                else:
                    # this for a General User whose profile is not locked in fb, u get number of followers from the page
                    print('\n Not a Page')
                    followers =  driver.find_element(By.CSS_SELECTOR,'.'+'.'.join('d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh e9vueds3 j5wam9gi b1v8xokw m9osqain'.split(' ')) ).text                                     
                    if followers.isdigit():
                        int(followers)
                        print("General User\n")
                    else:
                        raise Exception
            except:
                # this for a CELEBS PAGE, u get number of followers from the page
                followers = driver.find_element(By.CSS_SELECTOR,'.'+'.'.join('oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 oo9gr5id lrazzd5p'.split(' '))).text
                if followers.split(' ')[0].split('M')[0].isdigit():
                    print("\n\t But Its a Celebs Page \n ")
                else:
                    # profile hidden , cant do anything
                    followers = 'Hidden'
                    print('Profile is locked\nCant show friends as profile is Locked OR Profile is Public ,\n You need to make them friend first')

          
        elif u_input.startswith('t'):
            """
            SO u wanna get element having multiple classes ? 
                - Followers classname refers to the element having multiple classes.which refers
            to a single element, hence we used CSS selector or can use xpath
            where we need to join classes with . DOT .  
            but not for XPATH - was not working properly
            """
            print('Twitter\n')
            url = f"https://www.twitter.com/{username}/"
            driver.get(url)
            time.sleep(7)
            followers_class_name = '.'+ '.'.join('css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0'.split(' '))  
            total_words_list = [total_followers.text for total_followers in driver.find_elements_by_css_selector(followers_class_name)]
            time.sleep(5)
            followers =' '.join([ total_words_list[i-1] for i,word in enumerate(total_words_list) if word == 'Followers'])
            name = total_words_list[10] if not '' else total_words_list[11]

            if name is  None or name == '':
                print('\nCan fetch the name\n')
            time.sleep(5)
            profile_pic = driver.find_element(By.CLASS_NAME,'css-9pa8cd').get_attribute('src')
            # data[f'followers_of_{username}'] = followers

        elif u_input.startswith('l'):
            """ here we have to signin first and
            then click on url to search the name in the linkedin """
            print('Linkedin\n')
            # url = f"https://www.linkedin.com/"   
            url = f'https://www.linkedin.com/in/{username}/' 
            driver.get(url)
            time.sleep(5)
            driver.find_element(By.CSS_SELECTOR,'.authwall-join-form__form-toggle--bottom.form-toggle').click()
            
            time.sleep(3)
            driver.find_element(By.ID,'session_key').send_keys(linkedin_email)
            driver.find_element(By.ID,'session_password').send_keys(linkedin_password)
            driver.find_element(By.CLASS_NAME,'sign-in-form__submit-button').click()
            time.sleep(10)
            pyautogui.click(pyautogui.locateOnScreen(r'C:\Users\Tushar\Desktop\cloud_next\images\linkedin_in_url_white.png',confidence = .8))
            pyautogui.write(url)
            pyautogui.press('enter')
            time.sleep(15)
            followers = driver.find_element(By.CLASS_NAME,'t-bold').text
            name = driver.find_element(By.CLASS_NAME,'pv-text-details__left-panel').text
            profile_pic = driver.find_element(By.ID,'ember33').get_attribute('src')
            # data[f'followers_of_{username}'] = followers
            time.sleep(50)
        
        else:sys.exit("Invalid input")
        try:
            print(f'Username is \t\t',name,end='\n\n')
            print(f'Profile pic URL is \t',profile_pic,end='\n\n')
            print(f'Total Followers are \t\t',followers,end='\n\n')
         
        except:
            print('\tCant return name and profile URL')
      
        driver.close()
        return name
    
    except :
        print(f'{username}\t Check The Username Again\n ')
        return(f'\n\n Issue with User named -> {username} for getting the information for {u_input}')


names = [ 
        'tusharmalhan',
        # 'vindiesel',
        # 'rahul.vij.127',
        ]
# [user_information(name) for name in names]










                             
#    JUST PASS IN THE CORRECT USERNAME for the socialmedia account AND IT WILL FETCH THE INFORMATION

############################################################################################################################
#                                            CSV basic operations


# from csv import writer
# with open('posts.csv', 'w') as csv_file:
#     csv_writer = writer(csv_file)
#     headers = ['Title', 'Link', 'Date']
#     list_data=['03','Smith','Science']
#     list_of_dicts=[
#         {'ID':1,'NAME':'William','RANK':5532,'ARTICLE':1,'COUNTRY':'UAE'},
#         {'ID':6,'NAME':'William','RANK':5532,'ARTICLE':1,'COUNTRY':'UAE'}
#         ]
    # a=([(k,v) for k,v in dict.items()])  
          

    #        - This will set the headers
    # csv_writer.writerow(headers)   
    #      
    #        - This will add the data
    # csv_writer.writerow(list_data)         
    #      
    #       - If you comment and use writerow
    #       - it will Write new data to the file
    # csv_writer.writerow(list_data[0])
    #       
    #       - List of tuples will be entered in each row 
    #       - Do the loop and write the row automatically!
    # keys = ([  keys for keys in list_of_dicts[0] ])
    # print(keys)
    # csv_writer.writerow(keys)

    #       - ADD multiple values to the file
    # for values in list_of_dicts:
    #     csv_writer.writerow(values.values())



    #       - OR
    # from csv import DictWriter

    #       - Field name needs to be matched
    # field_names = ['ID','NAME','RANK','ARTICLE','COUNTRY']
    # dict_object = DictWriter(csv_file, fieldnames=field_names)

    #       - This will write the headers, no need to pass anything
    #       - will pick it from dict_object['fieldnames']
    # dict_object.writeheader()
    # dict_object.writerow(dict)
############################################################################################################################
#                                                Excel file basic operations


'''
POINTS 
 - IF FILE IS OPENED , THEN IT WILL NOT SAVE THE FILE , ERROR 
 - For each specific column , seperate for loop will run , which make sures to get data for each 
 specific column first.
'''

#                               Save  data in excel file even if file does not exists

# from openpyxl import Workbook

#                                Can work with multiple sheets at Once
# wb = Workbook()
# wb['Sheet'].title = "Report of Automation"               # 1 way to change title of sheet
# sh1 = wb.active                                        # active or create_sheet       # same same                 
# sh1['A1'].value = 'HEAD 0'
# sh1['B1'].value = 'HEAD 1'
# sh1['C1'].value = 'HEAD 2'

# sh1['A2'].value = 'VAL 1'
# sh1['B2'].value = 'VAL 2'

# for a in range(5):
#     sh1['A'+str(a+1)].value = a

# ws2 = wb.create_sheet()
# ws2.title = "5>!"                       # This is the title of the sheet ,   # 2 way to change title of sheet
# ws2['A1'] = '6'
# ws2['B1'] = '7'
# ws2['C1'] = '8'

# ws3 = wb.create_sheet()                 # If empty then sheet name is sheet by (default)

# list_of_dicts=[
#         {'ID':1,'NAME':'William','RANK':5532,'ARTICLE':1,'COUNTRY':'UAE'},
#         {'ID':6,'NAME':'William','RANK':5532,'ARTICLE':1,'COUNTRY':'UAE'},
#         {'ID':2,'NAME':'William','RANK':5532,'ARTICLE':3,'COUNTRY':'UAE'}
#         ]

# sh3 = wb.create_sheet()
# sh3.title = "sheet3"

# append keys and values in excel file 
# sh3.append([i for i in list_of_dicts[0].keys()])   # KEYS OF THE DICT
# for values in list_of_dicts:
#     sh3.append([i for i in values.values()])       # VALUES OF THE DICT

# wb.save('filename.xlsx')                           # MAKE SURE YOU save the file 



###################################################################

# Add and install Older version of Python 
# Remove new vesion of python from system variables 
# check version , old will be  placed
############################################################################################################################
#                                                Convert py to exe 
# cd into dir pyinstaller (pip install pyinstaller) > pyinstaller filename.py
# cd into dist > then run filename.exe , thus can send others ur software
# (FIle outside dist dir , runs the file without terminal so for bussiness use)

# HAVE A SINGLE FILE AS EXE , INSTEAD OF MULTIPLE DIRECTORIES FOR THE SOFTWARE
# cd into dist > then run filename.exe , thus can send others ur software
# DONT CONVERT IMG TO ICO file as icon for ur softw
# pyinstaller  --onefile  --name = test_fortclient c:/Users/Tushar/Desktop/python/completed_automation/connect_fortclient.py 


############################################################################################################################
