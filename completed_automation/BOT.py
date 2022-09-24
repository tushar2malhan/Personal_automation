''' A complete automation Bot for your daily needs '''
import  sys

sys.path.append(r'D:\Users\DELL\Downloads\env\Lib\site-packages')


#   REQUIREMENTS.TXT
# pip install requests pyautogui selenium keyboard pytesseract  win10toast wikipedia pyjokes pywhatkit pygame pyautogui opencv-python numpy playsound translate  SpeechRecognition pyttsx3 pytube PyPDF2 pywikihow win10toast  translate paramiko  keyboard  pytesseract flask fastapi django gtts englisttohindi torch nltk regex openpyxl
#  # issue with PyDictionary  

# Downlaod chrome driver based on your chrome 
# -  chrome > help > about google chrome >  check version of chrome
# https://chromedriver.chromium.org/downloads


from datetime import date
# from  pygame import mixer
# from win32com.client import Dispatch
import os , json , requests , pickle , datetime , time 
import argparse ,sys
import re 
# if issue with PyAudio , go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and search for pyaudio and download amd64.whl 
# and run pip install  the downloaded file in the terminal 
# pip install PyAudio-0.2.11-cp310-cp310-win_amd64.whl  OR  pip install PyAudio-0.2.11-cp310-cp310-win_amd64.whl
import webbrowser
import os
import smtplib
import wikipedia
import pyjokes
import pywhatkit
import pygame
from translate import Translator
import paramiko
import pyautogui
import keyboard
from PyDictionary import PyDictionary as pd
import numpy as np
import cv2                  # pip install opencv-python
import requests
from bs4 import BeautifulSoup
import playsound
import random


from tkinter import Button, Entry, Label , Tk , StringVar, mainloop
from pytube import YouTube
from englisttohindi.englisttohindi import EngtoHindi
import PyPDF2
from gtts import gTTS
from pywikihow import search_wikihow 

from win10toast import ToastNotifier

import shutil

import speech_recognition as sr # pip install SpeechRecognition
import pyttsx3

engine = pyttsx3.init('sapi5')   
voices = engine.getProperty('voices')
# print(voices[0])
engine.setProperty('voice',voices[0].id)  # set the male voice 
engine.setProperty('rate',190)        #  redeuce rate to slow down the speed 

# web driver for brave browser 
from selenium import webdriver


cancel = ['stop','leave','stop','quit','exit']


def speak(audio):
    print('  ')
    engine.say(audio)
    engine.runAndWait()


def takeCommand():
    #It takes microphone input from the user and returns string output
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source) 
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language = 'en-IN') #Using google for voice recognition.
        print(f"You asked : {query}\n")  #User query will be printed.

    except Exception as e:
        # speak( " WHAT ")   #Say that again will be printed in case of improper voice 
        return "None" #None string will be returned
    return query # or QUERY.lower()


def wish():
    hour = int(datetime.datetime.now().hour)
    if hour >=6 and hour <=12: 
        engine.say('Good morning') 
    elif hour >=12 and hour <=18 :
        engine.say('Good afternoon')

    elif hour >=23 and hour >=5 :
        engine.say('Sir , its quite late , kindly postpone your current tasks and take rest \t If not then ') 
        time.sleep(2)
    else:
        speak('good evening')
    engine.runAndWait()
    # speak(' How can i help you ? ')


def search(word):
    try:
        # driver_path = r"D:\Users\tusha\Downloads\chromedriver_win32\chromedriver.exe"
        # brave_path = r"D:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        # option = webdriver.ChromeOptions()
        # option.binary_location = brave_path
        # browser = webdriver.Chrome(executable_path=driver_path, chrome_options=option)
        url=(f'https://www.{word}.com') 
        webbrowser.open_new_tab(url)
    except:
        speak('cant find it on on the web ')


def translator():
    speak('Tell me the word ? ')
    alpha = takeCommand().lower()           # take word
    speak (' wanna translate it into Hindi')
    inp = takeCommand().lower()
    if inp in ['yes', 'Yes','ok','yup']:
        res = EngtoHindi(alpha)
        speak(res.convert)
        print(res.convert)
    else:
        translator = Translator(from_langg='english',to_lang='german')
        word = translator.translate(alpha)
        time.sleep(1)
        speak(f'in german {alpha} is called \n {word} ')
        print(word)


def whatsapp_func(number):
    speak('sure , whats the message')
    msg = takeCommand().lower()
    speak('wanna send the message now')
    ans = takeCommand().lower()
    
    hour = datetime.datetime.now().hour
    minutes = datetime.datetime.now().minute
    
    if ans in ['no','not now','na','n','tomorrow']:
        speak('ok then \n at what hour ?')
        hour = int(takeCommand().lower())
        speak('how many minutes ?')
        minutes = int(takeCommand().lower())
        pywhatkit.sendwhatmsg(number,msg,hour,minutes,20)
        speak('Sent')
    else:
        pywhatkit.sendwhatmsg(number,msg,hour,minutes+2)
        speak('Sent')

def whatsapp_send():
    speak('whom do you want to send ? ')
    name = takeCommand().lower()
    if name in ['me','myself','i','sent to me','tushar']:
        whatsapp_func('+917814891872')
    elif name in ['maugham','mom','mata','meri maa','mommy']:
        whatsapp_func('+917814891872')
    elif 'Das' in name:
        whatsapp_func('+919967541997')
    elif name in ['mum','mom']:
        whatsapp_func('+918169257690')
    elif 'samridhi' in name:
        whatsapp_func('+919988994191')
    elif name in['bhai','bro','jimmy bhaiya','bruh']: 
        whatsapp_func('+17472324574')
    elif 'rohit' in name:
        whatsapp_func('+917678260679')
    elif 'armaan' in name:
        whatsapp_func('+918427746367')
    elif 'rahul' in name:
        whatsapp_func('+12368816765')
    else:
        speak(f'sorry {name} not listed yet , kindly ask Tushar to add the number for the respected individual ')

def closeapp(app_name):
    speak('which applicaiton do you want to close?')
    query = takeCommand().lower()
    if app_name in query:
        os.system(f'TASKKILL /F /im {app_name}.exe')
        speak(f'closed {app_name}')

def youtubeAuto():
        speak(' Keys are     Pause restart minimize fullscreen')
        com = takeCommand().lower()
        if 'pause' in com:
            keyboard.press('space bar')
            speak('Done \n pressed ur key ')
        elif 'restart' in com:
            keyboard.press('m')
            speak('Done \n pressed ur key ')
        elif 'minimize' in com:
            keyboard.press('i')
            speak('Done \n pressed ur key ')
        elif 'full screen' in com:
            keyboard.press('f')
            speak('Done \n pressed ur key ')
        elif com in ['',0]:
            speak('pardon speak again')
        elif com in cancel:
            speak('Done with your youtube automation ')
            return False
        else:
            speak('not allowed currently , first practice this')
    
def chromautomation():
    speak('lets automate chrome now \n how u wanna start this ?' )
    speak('Speak , open tab , close tab , open history , open downloads' )
    comm = takeCommand().lower()
    if 'close' in comm:
        keyboard.press_and_release('ctrl + w')
    elif 'open' in comm:
        keyboard.press_and_release('ctrl + t')
    elif 'history' in comm:
        keyboard.press_and_release('ctrl + H')
    elif 'downloads' in comm:
        keyboard.press_and_release('ctrl + j')
    elif comm in cancel:
        speak(' alright ')
        return False    
    else:
        speak('no else command allowed yet')

def temp(word):
    url=(f'https://www.google.com/search?q=temperature={word}')
    r = requests.get(url)
    data = BeautifulSoup(r.text,"html.parser")
    temperature = data.find("div",attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
    speak(f'{temperature} ')

def reader():
    # speak('Tell me the name of the book ')
    # name = takeCommand().lower()
    # os.startfile(r'D:\Users\tusha\Documents\aws summary\aws PDF\AWS.pdf')
    book = open(r'D:\Users\tusha\Documents\aws summary\aws PDF\AWS.pdf','rb')
    pdfreader = PyPDF2.PdfFileReader(book)
    pages = pdfreader.getNumPages()
    speak(f'Number of pages in this book are {pages}')
    speak('from which page you want to start reading the book')
    num= int(input('page number ? '))
    page = pdfreader.getPage(num)
    text = page.extractText()
    speak('In which language you want to listen ')
    lang = takeCommand().lower()
    if 'hindi' in lang:
        trans = Translator()
        texthindi = trans.translate(text,'hi')
        textm = texthindi.text
        speech = gTTS(text=textm)
        try:
            speech.save('book.mp3')
            playsound('book.mp3')
        except:
            playsound('book.mp3')
    else:
        speak(text)

def taskgui():
    query = takeCommand().lower()

def send_notification(title, message):
    notifier = ToastNotifier()
    notifier.show_toast(title, message)



leavee =['get lost now','thank god ur leaving','please go and let me rest','its better u should leave before i insult you','yeah bye ','chall nikal'
,'buzz off now ']
reply = ['hello ','Hey',' im here only','listening you ','speak fast','i got it ! will u say now ','Always here ','hey how can i help you']


if __name__ == "__main__":

    def test():
        wish()

        real_idenity='Tushar'
        administrator ='tushar'
        administrator.lower().strip()
        password = 'open'
        speak('Kindly provide credentials ! whats the password ? ')
        for i in range(3,0,-1):
            query = takeCommand().lower().strip() 
            if password in query :
                # names ={'samridhi':'sumdraa' , 'tushar':'tushii' ,"rohit":'Mr rohit pathak',None:'Anonymous','kishore':'tushar','':'anonymous','none':"tushar"}

                speak('Great , You are successfully authenticated to use this bot  \t ')
                real_idenity = 'Tushar'  
                speak(f' Welcome {real_idenity}')
                time.sleep(0.5)
                speak(f'Yes tell me  {real_idenity} , what can i do for you ? ')
                time.sleep(0.5)

                while True:
    
                        time.sleep(1.5)
                        query = takeCommand().lower() 
                        if 'wikipedia' in query:
                            try:
                                speak(f'Searching Wikipedia for {query} ...')
                                query = query.replace("wikipedia", "")
                                query = query.replace("search",'')
                                results = wikipedia.summary(query, sentences=5)
                                speak("According to Wikipedia")
                                speak(results)
                                speak(' Thats it for him ..')
                            except:
                                speak(f" {query} is not listed in wikipedia")
                        
                        elif query in ['hello','hai','hey','hi','how are you','hey buddy','you are great','your great','hay','ok']:
                            speak(random.choice(reply))
                            # speak(f'Im all yours {real_idenity} , suggest me some actions so that i can help you with   !')

                        elif 'youtube' in query:             #                           search and play video on youtube 
                            speak(f' what do you want to watch on youtube? ')
                            songname = takeCommand().lower()
                            song = songname.replace('song',songname)
                            speak(f'Playing {song} on youtube ')
                            time.sleep(5)
                            pywhatkit.playonyt(song)
                            speak('now do u wanna automate')
                            time.sleep(5)
                            queryy = takeCommand().lower()
                            if queryy in ['yes','ok',True]:
                                    youtubeAuto()
                                    speak('what else')
                        
                        elif 'motivate' in query:
                            pywhatkit.playonyt('https://www.youtube.com/watch?v=xNW3nsKTwNg')

                        elif 'open youtube' in query:
                            search('youtube')
                            
                        elif 'google' in query or 'search' in query:
                            speak ('do you want to search anything specific on google ?')
                            query1 = takeCommand().lower()
                            if query1 in ['yes', 'y','ok',"let's go",'yup','yeah',True]:
                                speak('what do you wanna search  ')
                                query = takeCommand().lower()
                                query = query.replace('ok then','')
                                query = query.replace('search','')
                                pywhatkit.search(query)                 # SEARCH ON GOOGLE
                                speak('Do you wanna automate this search ')
                                say = takeCommand().lower()
                                if say in ['yes', 'y','ok','lets go','yup']:
                                        speak ('tell me when u wanna loop out of this automation') 
                                        chromautomation()
                                        speak('done  what else ')
                                else:
                                    speak('Alright  , do it manually then ')
                            else:
                                search('google')
                        
                        elif 'website' in query:
                            speak('alright')
                            query = query.replace('open','')
                            query= query.replace('yes','')
                            query= query.replace('website','')
                            query= query.replace('this','')
                            print(query)
                            search(query) # SEARCH the SPECIFIC WEBSITE 

                        elif 'github' in query:
                            search('github') 
                        
                        elif 'wwe' in query:
                            search('wwe')    

                        elif 'tell' in query:
                            speak(' You shut up \n Let tushar sir speak ')

                        elif 'joke'  in query:  
                            # data = requests.get(r'https://official-joke-api.appspot.com/jokes/programming/random')
                            # t = json.loads(data.text)
                            # for i in t:
                            #     print(i["type"])
                            #     speak(i["setup"])
                            #     speak(i["punchline"])
                            # speak(pyjokes.get_joke())
                            
                            # speak('lol')
                            # speak('Heres another one')
                            time.sleep(1)
                            get = pyjokes.get_joke()
                            speak(get)
                            speak('ha ha ha ha haa haa')
                            time.sleep(1)
                            # speak('ha ha ha ha haa haa')
                            
                        elif 'music' in query:
                            speak(f'sure {real_idenity} \n , here it goes ')
                                                    
                            music_dir = r'D:\Users\tusha\Music'
                            songs = os.listdir(music_dir) [:2]
                            pygame.init()
                            pygame.mixer.init()
                            print(songs)
                            for each_song in range(len(songs)):
                                pygame.mixer.music.load(os.path.join(music_dir,songs[each_song]))
                                pygame.mixer.music.play()        
                        
                        elif 'stop it' in query:
                                speak('stopping the music')
                                pygame.mixer.music.stop()
                    
                        elif 'time' in query:
                            strTime = datetime.datetime.now().strftime("%H:%M:%S")    
                            speak(f"{real_idenity}, the time is {strTime}")
                        
                        elif 'date' in query:
                            current_time = datetime.datetime.now() 
                            speak(f'{date.today() }')
                            speak(f'So {real_idenity} , Month is {current_time.month}')
                            speak(f'and Day is {current_time.day}')

                        elif 'vs code'  in query:
                            speak(f'sure {real_idenity}  , here it goes ')
                            codePath = r"D:\Users\tusha\AppData\Local\Programs\Microsoft VS Code\Code.exe"
                            os.startfile(codePath)

                        elif 'code' in query:
                            speak('sure  , Lets code  ')
                            codePath = r"D:\Users\tusha\Desktop\PYTHON"
                            lis = os.listdir(codePath)
                            print(lis)

                            time.sleep(5)
                            speak('Which file you require')
                            filename = takeCommand().lower()
                            speak(' extension ')
                            word = takeCommand().lower().strip()

                            c_end = ''.join([i for i in lis if i.startswith(filename) and i.endswith(word)])
                            os.startfile(c_end)
                            print(c_end)

                            try:
                                os.startfile(os.path.join(codePath,c_end))                       # start the file in python   by joining path  
                            # os.startfile(f'{codePath}\{a}')                            # start the file in python      or just start the file 

                            except:
                                speak(f' Kindly check the path or the file name . i cant find any file related to  {filename} ')
                                speak('Try it again ')
                            
                        elif 'job' in query:
                            speak(f' Sure  ')
                            os.startfile(r'D:\Users\tusha\Desktop\trace\Traceart.TXT')
                        
                        elif 'type' in query:
                            ''' keep typing until i say done or stop '''
                            os.chdir(os.getcwd())
                            while True:
                                print('\nSpeak Now \n')
                                speak(' ')
                                content = takeCommand().lower()
                                with open(r'C:\Users\Tushar\Desktop\python\completed_automation\Protected\reminders.txt','a+')as f:
                                        if content in ('ok','type now','type','now'):
                                            speak(' Say something \n')
                                            content2 = takeCommand().lower()
                                            f.write(f'\t Message By {real_idenity} ~ \t {content2} \n'  )
                                            speak(f'Done {real_idenity} , your message has been saved ')
                                       
                                        elif content in ('done','dant','stop','done'):
                                            break
                       
                        elif 'instagram' in query:
                            ''' open instagram on google and type msg for ur friend'''
                            webbrowser.open_new('https://www.instagram.com/direct/t/340282366841710300949128399636759531997')
                            pyautogui.press('enter')
                            time.sleep(10)
                            if pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\Desktop\python\pics\friend_1.png')   : 
                                pyautogui.click( pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\Desktop\python\pics\friend_1.png')   )
                            else:
                                pyautogui.click( pyautogui.locateCenterOnScreen(r'C:\Users\Tushar\Desktop\python\pics\friend_2.png')   )
                            pyautogui.press('enter')
                            speak('Speak the Message you want to send to the user !')
                            sent_msg = ['yes','send','ok','send it','sent','ok send it','yes send it']
                            while 1:
                                msg = takeCommand()
                                print(msg)
                                if msg != 'None':
                                    speak(' Are you sure you want to send this message ? ')
                                    confirmation = takeCommand().lower().strip()
                                    speak (" \t Your message \t "+ msg  )
                                    if confirmation in sent_msg:  pyautogui.typewrite(msg) ,speak('message sent') 
                                    else: speak('message not sent')
                                elif msg in cancel:
                                    break 


                        elif 'news' in query:
                            speak('Highlighting the top headlines for today ! ')
                            url='https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=582ac9b80816460b872a1c9e48ebbabe'
                            newss=requests.get(url).text
                            news_dict = json.loads(newss)
                            articless = news_dict['articles']
                            for i in articless:
                                speak(i['title'])  
                                time.sleep(3)
                                speak('Moving on to the next news ') 
                            speak(f'Thanks for being there {real_idenity} ')
                        
                        elif 'notepad' in query:
                            os.system('Notepad.exe')
                            speak('done')
                                           
                        elif query in ['send','message'] :
                            whatsapp_send()
                        
                        elif 'what' in query:
                            speak(f'{real_idenity} i can crack jokes \n, play music \n, type something for you \n give you todays news \n can play videos on youtube \n open files or directories \n . i bet \n  try me ' )

                        elif query in ['exit','leave noe','bye','Kuwait','quit']:
                            speak(random.choice(leavee))
                            # speak(f' Respected {real_idenity} \n , Thankyou for giving me opportunity \n to serve you  ')
                            break

                        elif 'days' in query:
                            speak('sure \n kindly provide year \n month \n days ')
                            try:
                                speak('Starting From  \n ')
                                first_yr =int(takeCommand().lower())
                                first_m = int(takeCommand().lower())
                                first_d = int(takeCommand().lower())
                                
                                speak('Till \n ')
                                final_yr = int(takeCommand().lower())
                                final_m = int(takeCommand().lower())
                                final_d = int(takeCommand().lower() )

                            except Exception as e:
                                speak('kindly repeat . i must have heard string   ')
                            
                            speak('Do you want to count your specified date till  today ? \n')
                            userinput = takeCommand().lower()
                            if userinput in ('yes', 'y',True,'ok'):
                                b = datetime.datetime.now()
                            else:
                                b = datetime.datetime(final_yr, final_m, final_d, 0, 0, 0)

                            a = datetime.datetime(first_yr, first_m, first_d, 0, 0, 0)
                            c = b-a 
                            speak (f' {c} days ')
                        
                        elif 'convert' in query:

                            ...
                        
                        elif 'translate' in query:
                            time.sleep(2)
                            translator()
                            
                        elif 'server' in query:                      # connect to remote server via ssh 
                            # try:
                            #     ssh_client = paramiko.SSHClient()
                            #     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            #     speak('Give me the hostname')
                            #     hostname = input('? ')   #'3.137.166.213'  ip address of ec2 server
                            #     ssh_client.connect(hostname =hostname , 
                            #     username='ec2-user', 
                            #     password = 'paramiko123', 
                            #     port = 22,
                            #     key_filename =r'D:\Users\tusha\Downloads\ohio_linux.pem')
                            #     speak('connecting to your remote server ')

                            #     stdin, stdout, stderr = ssh_client.exec_command('whoami')
                            #     stdin, stdout, stderr = ssh_client.exec_command('ls')

                            # stfp_client = ssh.open_sftp()   # throw files to ur server
                            # stfp_client.get('/home/ec2-user/test.py','paramiko_downloaded_from_remote_server.txt')      # from remote path   ,  to local path 
                            # stfp_client.chdir('/home/ec2-user')    # now sftp client points to this location , no need to mention in download remote path
                            # print(stfp_client.getcwd())
                            # stfp_client.get('test.py',r'D:\Users\tusha')
                            # stfp_client.put('projects.py','/home/ec2-user')       # from local > to remote server 
                            # stfp_client.close()
                            # ssh.close()
                                
                                # a=stdout.readlines()
                                # speak('Connection successfull ')
                                # print('Output: ', a)
                                # speak(a)
                                # print('Error : ', stderr.readline())
                                # speak('Done')
                            # except:
                            #     speak('cant connect , kindly check the respective settings the from server ')

                            try:

                                ...
                            except:
                                print('sorry cant connect to the server')
                                # chmod 600 s2dev.pem
                                # sftp -i  s2dev.pem ubuntu@40.76.12.176
                                # ssh -i s2dev.pem ubuntu@40.76.12.176
                                #  get , put , post, delete 
                        
                        elif 'screenshot' in query:
                            from PIL import ImageGrab
                            save_path=(fr'C:\Users\DELL\Desktop\PYTHON\screenshots_by_bot\snapshot_{datetime.datetime.today().day}.jpg')
                            snapshot = ImageGrab.grab()
                            snapshot.save(save_path)
                            speak('screenshot saved')
                                                        
                        elif 'close' in query:
                            try:
                                speak('whats the Name of the app  ? \n')
                                app=takeCommand().lower()
                                closeapp(app)
                            except:
                                speak('i dont think we have that applicaiton with us ')

                        elif 'dictionary' in query:
                            speak('whats the word ')
                            try:
                                prob = takeCommand().lower()
                                prob.replace('search','')
                                prob.replace('meaning','')
                                prob.replace('of','')
                                prob.replace('meaning of','')
                                result = pd.meaning(prob)
                                global result_opt_verb
                                result_opt_verb = result.get('Verb')
                                print(result_opt_verb)
                                speak(f' The meaning of {prob} is ')  
                                time.sleep(3)
                                speak(result_opt_verb)  
                            except:
                                speak('couldnt find it ')

                        elif 'download youtube' in query:
                            ''' remove ube from youtube link and use driver mp4 to download the video '''
                            # root = Tk()
                            # root.geometry('500x300')
                            # root.resizable(0,0)
                            # root.title('Youtube video downloader')
                            # speak('Enter your link ')

                            # Label(root,text="Download youtube video",font='arial 15 bold').pack()
                            # link = StringVar()
                            # Label(root,text='Paste your link here',font='arial 12 bold').place(x=150,y=60)
                            # Entry(root,width=70 ,textvariable=link).place(x=35,y=90)


                            # def VideoDownloader():
                            #     url =YouTube(str(link.get()))
                            #     video = url.streams.first()
                            #     video.download(r'D:\Users\tusha\Desktop\PYTHON\youtube_downloaded_videosBY_bot')
                            #     Label(root,text="Downloaded",font='arial 15').place(x=180,y=210)

                            # Button(root,text="Click here",font='arial 15 bold',bg ='pale violet red',padx=2,command =VideoDownloader).place(x=170,y=150)

                            # root.mainloop()
                            import pytube  
                            from pytube import YouTube
                            speak('Enter ur Url')  
                            video_url = input('Url ~ ')   
                            youtube = pytube.YouTube(video_url)  
                            video = youtube.streams.first()  
                            print(video.title) 
                            video.download(r'D:\Users\tusha\Desktop\PYTHON\youtube_downloaded_videosBY_bot')
                            speak('your video has been  downloaded')
                            # or use this url to download video 
                            # https://loader.to/en102/1080p-video-downloader.html

                        elif 'wait' in query:
                            speak('ok')
                            time.sleep(15)
                            speak('Now tell me something ')

                        elif 'my' in query:
                            with open(r'D:\Users\tusha\Desktop\PYTHON\completed_automation\reminders.txt') as s:
                                a=s.readlines()
                                speak('Your reminders :- ')
                                speak(a)
                                time.sleep(1.5)
                                speak('Done')

                        elif 'remind'in query:
                            msg = query.replace('remember that','')
                            msg = query.replace('remind me to','')
                            with open(r'D:\Users\tusha\Desktop\PYTHON\completed_automation\reminders.txt','a+')as f:
                                f.write(f'\nBy {real_idenity} on  {datetime.datetime.now()} > \t {msg} \n'  )
                                time.sleep(1.5)
                                speak('Alright ')
                                
                        elif 'temp' in query:
                            speak('Which city ? ')
                            w = takeCommand().lower()
                            
                            temp(w)

                        elif 'read' in query:
                            reader()

                        elif 'how to' in query:
                            op = query.replace('how to','')
                            maxx =1
                            how_func = search_wikihow(op,maxx)
                            assert len(how_func) == 1
                            how_func[0].print()
                            speak(how_func[0].summary)
                  
                        elif 'notify' in query:
                            os.system(r'D:\Users\tusha\Desktop\PYTHON\completed_automation\alarm.py')
                       
                        elif 'search' in query:
                            speak('opening ur c drive')
                            pyautogui.click(pyautogui.locateCenterOnScreen(r"C:\Users\DELL\Desktop\PYTHON\pics\search.png"))
                            speak('tell me what you wanna search ')
                            search = takeCommand().capitalize()
                            
                            keyboard.write(search)
                            pyautogui.press('enter')   
                            pyautogui.press('enter')   
                            
                                                  

            speak(f' {i-1} times left  ')
            if i == 2:
                speak(f' its the last chance  ')
            elif i == 1:
                speak(f' well i dont think you know  {administrator}') 
                time.sleep(0.5)
                speak('soo take guidance from him before getting ur hands on me ')
                speak('Goodbye , i only follow my masters commands and this proves thats not you ')
                exit()
  
    test()