import datetime , time 
import speech_recognition as sr
from win10toast import ToastNotifier
import pyttsx3

engine = pyttsx3.init('sapi5')   
voices = engine.getProperty('voices')
# print(voices[0])
engine.setProperty('voice',voices[0].id)  # set the male voice 
engine.setProperty('rate',200)

def send_notification(title, message):
    notifier = ToastNotifier()
    notifier.show_toast(title, message)

def takeCommand():
    #It takes microphone input from the user and returns string output
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language = 'en-IN') #Using google for voice recognition.
        print(f"You asked : {query}\n")  #User query will be printed.

    except Exception as e:
        # speak( " WHAT ")   #Say that again will be printed in case of improper voice 
        return "None" #None string will be returnedl
    return query # or QUERY.lower()

def speak(audio):
    print('  ')
    engine.say(audio)
    engine.runAndWait()

speak('title')
title = takeCommand().lower()
speak('Message')
message = takeCommand().lower()

speak('wanna send the message now')
hour = datetime.datetime.now().hour
minutes = datetime.datetime.now().minute
ans = takeCommand().lower()

if ans in ['no','not now','na','n','tomorrow']:
     speak('ok then \n at what hour ?')
     hour = int(takeCommand().lower())
     speak('how many minutes ?')
     minutes = int(takeCommand().lower())
     while datetime.datetime.now().hour !=hour and datetime.datetime.now().minute!=minutes:
          speak('ok')
          time.sleep(5)
          speak('anything else ')
     send_notification(title,message)  
else:
     send_notification(title,message)
     speak('Sent')