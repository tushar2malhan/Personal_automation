''' Play Bot in bg with your project '''
import speech_recognition as sr  #pip install SpeechRecognition
import os 
import pyttsx3

engine = pyttsx3.init('sapi5')   
voices = engine.getProperty('voices')
# print(voices[0])


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
        ''' 
        SPEAK THIS PASSWORD TO PROCEED 
        ok start     ->     to start the Bot 
        you there    ->     to start the model detection
        bye          ->     to stop the Bot
        '''
        if "start" in wake_up:
            engine.setProperty('voice',voices[1].id)  # set the male voice 
            engine.setProperty('rate',200)
            speak('Sure' )
            speak('callling my  \n bro')
            os.system(r'"C:/Program Files/Python310/python.exe" C:\Users\Tushar\Desktop\python\completed_automation\BOT.py')
        elif 'bye' in wake_up:
            speak('ok Then Bye ')
            break
        elif 'there' in wake_up:   # you there 
            engine.setProperty('voice',voices[0].id) 
            engine.setProperty('rate',175)
            speak(' Always at your service sir ')
            import time;time.sleep(10)
            query = takeCommand().lower()      
            """   ur command => So  set the video capture to (0) 
            and make sure the ALGORITHM sets to predict more than 0.8 percent accuracy
            and if we have any, do play bgm to make it more realistic      """
            speak('Sure , will be counting on you sir')
            os.system(r'"C:\Users\Tushar\Downloads\model_detection_Output\abs_hd_output.avi"')
            import time;time.sleep(25)
            speak('Well i could clearly depict that you are in shape sir  ')
        else:
            print('nothing...')