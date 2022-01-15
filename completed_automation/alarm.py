import speech_recognition as sr
import pyttsx3,datetime ,os,time,signal



engine = pyttsx3.init('sapi5')   
voices = engine.getProperty('voices')
# print(voices[0])
engine.setProperty('voice',voices[0].id)  # set the male voice 
engine.setProperty('rate',200)
from win10toast import ToastNotifier

def speak(audio):
    print('  ')
    engine.say(audio)
    engine.runAndWait()

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
        return "None" #None string will be returned
    return query # or QUERY.lower()






alarm_hour=19
alarm_minute=44


if __name__ == '__main__':
    print(2,'file')
    title='base'
    message='test'
    # speak('title')
    # title = takeCommand().lower()
    # speak('Message')
    # message = takeCommand().lower()

    # speak('ok then \n tell me at what hour should i remind you ?')
    # alarm_hour=int(takeCommand().lower())

    # speak('how many minutes ?') 
    # alarm_minute=int(takeCommand().lower())

    # alarm_seconds=0

    # speak("Setting up alarm..")

    # speak(f'Alright ill notify you at {alarm_hour} hours and f{alarm_minute} minute ')
    


    while 1:
            now = datetime.datetime.now()
            current_hour =  datetime.datetime.now().hour
            current_minute =  datetime.datetime.now().minute
            current_seconds =  datetime.datetime.now().second
            # print(current_minute,current_seconds)
    
            time.sleep(1)
            
            # print(alarm_minute-current_minute-1,'minutes &&' ,60-current_seconds ,'seconds left ')
            if alarm_minute-current_minute >1:
                os.system(r'"C:/Users/DELL/Python 3.9.7/python.exe" c:/Users/DELL/Desktop/PYTHON/completed_automation/web_scraping.py')
            
            elif 60-current_seconds<4:
                print('\t\n\t ')
                print(60-current_seconds )

            elif alarm_minute-current_minute==1:
                print(60-current_seconds ,'seconds left Now! ')
                if current_seconds==0:
                    continue
            elif(alarm_hour-current_hour==0 and alarm_minute-current_minute==0 ):
                speak('Alarm breached ')
                send_notification(title,message)
                break
            else:
                print('time not set properly')
                break

