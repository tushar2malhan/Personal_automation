
# from BOT import test
import speech_recognition as sr  #pip install SpeechRecognition
import os 
import pyttsx3

engine = pyttsx3.init('sapi5')   
voices = engine.getProperty('voices')
# print(voices[0])
engine.setProperty('voice',voices[1].id)  # set the male voice 
engine.setProperty('rate',200)

def speak(audio):
    print('  ')
    engine.say(audio)
    engine.runAndWait()



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
        return "None" #None string will be returned
    return query # or QUERY.lower()

while True:
        wake_up = takeCommand().lower().strip()
        if "ok start" in wake_up:
            speak('Sure' )
            # speak('callling my bro ')
            os.system(r'C:\Users\DELL\Desktop\PYTHON\completed_automation\BOT.py')
             
        elif 'bye' in wake_up:
            speak('ok Then Bye ')
            break
        else:
            print('nothing...')

# D:\Users\tusha\env\Scripts\python.exe D:/Users/tusha/Desktop/PYTHON/play_at_bg.py


''' play the video in background (personal project)''' 

# from completed_automation.BOT import speak, takeCommand
# from time import sleep
# import os

# while 1:
#      # query = takeCommand().lower() 
#      # print(query)
#      # if query in ('you there'):
#           speak(' Always at your service sir ')
#           query = takeCommand().lower()      
#           speak('Sure    will  do the needful  ')
#           """
#           Dont move the cursor , video will automatically pop up
          
#           """
#           os.startfile(r"C:\Users\Tushar\Downloads\output\output1.avi")
#           sleep(5) # increase the time for live video
#           speak('Well i can clearly depict that you are in shape sir  ')
     # else:
     #      print(None)