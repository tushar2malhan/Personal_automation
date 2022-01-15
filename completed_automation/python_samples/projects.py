# from functools import lru_cache, reduce
from math import perm
import os , json , requests , pickle , datetime , time 
from datetime import date
# from  pygame import mixer
from win32com.client import Dispatch
import argparse ,sys
import pyttsx3
import re 
import speech_recognition as sr
import webbrowser
import os
import smtplib
import wikipedia

# engine = pyttsx3.init()
# engine.say('Hi Tushar Malhan')
# engine.say('ok')
# engine.runAndWait()
# engine = pyttsx3.init()
# engine.say("I will speak this text")
# engine.runAndWait()
# print(1)

# for i in range(5):
# #     print('\t',i,'=i')
#      print(' ')
#      for j in range(5 , i, -1 ):      # check when i is ending 
#         print(j ,end='')
#      for k in range(i , 5+1):        # check when i is starting 
#          print(k ,end='')

''' pehla 5 par aakar khatam ho , phir dusra start ho 1 , khatam ho 5 tak '''

# from datetime import datetime as dt
# import datetime

# import calendar
# for x in range(1,13):
#     print( calendar.month_name[x] ,end=' ')
# print('\nMonday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday')
# for i in range(1,11):
#     print(i)
 
# import sys  # python prac1.py Tushar 167 71

# a = input('Hi , What is your Name?\n')
# c = float(input('What is your Height in metres?\n'))
# b = int(input('What is your Weight in Kg?\n'))
# d = round(b/(c*c), 1)
# seperator =', '
# dic  ={
#     'name':sys.argv[1:2] ,
#     'height':sys.argv[2:3],
#     'weight':sys.argv[3:] ,       # argv - stores user inputs values 
# }
# print(', '.join(dic) )

# print(sys.argv)

# class parent:
#     def __init__(self,age,*name):
#         self.age=age
#         self.name=name
#     def cal(self):
#         print(self.age,self.name)
#     # def __str__(self):
#     #     return f'{self.age , self.name}'

# class child(parent):
#         def __init__(self,age,name):
#             super().__init__(self,age,name)
#             self.age=age,
#             self.name=name
#         def all(self):
#             print(self.age,self.name)

# # a=parent(52,'goldy')
# # print(a)
# b = child('n- tushar','malhan')
# # b.all()
# print(b.name)
# print(b.age)




# @lru_cache(maxsize=4)    # it dosen't have delay  in calling the func , but it prints it directly 
# # it caches the seconds 
# def work(n):
#     time.sleep(n)
#     print('welcome to mini projects ')

# if __name__=='__main__':
#     print(1)
#     print(2)
#     print(4)
#     print('running it ')
#     work(2)
#     print(__name__)
#     work(2)
#     print('done')

''' corountines  - when functions needs an initialization '''
# def searcher():
#     book ='tushar is reading the text from the given para '
#     time.sleep(4)

#     while True:
#         text = (yield)    # access yield values by send
#         if text in book:
#             print(' your text is there in book ')
#         else:
#             print(' your text is not in the book ')

# a=searcher()
# next(a)
# a.send('tushar')
# input(' press any key ')
# a.send('Tushar')
# a.close()                       # we close the coroutine after we are done



# def music(file,*stopper):
#     mixer.init()
#     mixer.music.load(file)
#     mixer.music.play()
#     while True:
#         a= input(' Stop ?')
#         if a in (stopper):
#             mixer.music.stop()
#             break

# def log(msg):
#     with open('log.txt','a')as f:
#         f.write(f'{msg} {datetime.datetime.now()}')
    

# music('rock.mp3','y','yes','done')


# print(dir(os))
# print(os.getcwd())
# os.chdir('D://')
# print(os.getcwd())
# print(os.listdir('D://'))
# os.mkdir('python')
# print(os.listdir()
# print(os.path.join())
#
# def speak(str):
#     speak = Dispatch('SAPI.SpVoice')
#     speak.Speak(str)

# speak('HELLO TUSHAR')

# a = os.listdir()
# py = [file for file in a if file.endswith('.py')  ]
# for fo in py:
#     os.replace(fo,r'D:\Users\tusha\Desktop\trace\python\python_all')
#     speak('done')
        
# REQUESTS 
# r = requests.get('http://www.wwe.com')
# d={'p1':'name','malhan':'lanme'}
# r1 = requests.post(url='http://www.wwe.com',data=d)
# print(r.text)
# print(r.status_code)
# print(r1.status_code)


# pickle  - preserve py object for futue 
# pyinstaller python.txt


''' creating command like utlity   
cd in file   |   python .\projects.py --x 9 --y 7 --o add  '''
# def calc(args):
#     if args.o =='add':
#         return args.x + args.y
#     elif args.o =='mul':
#         return args.x * args.y
#     elif args.o =='sub':
#         return args.x - args.y
#     elif args.o =='div':
#         return args.x / args.y
#     else:
#         return 'somethinf went wrong '


# if __name__=='__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--x' , type=float, 
#     default=1.0 , help='enter 1 number . Kindly contact Owner for any difficulty ')
#     parser.add_argument('--y' , type=float, 
#     default=6.0 , help='enter 2 number. Kindly contact Owner for any difficulty ')
#     parser.add_argument('--o' , type=str, 
#     default='add' , help='Utility for calculation  ')

#     args = parser.parse_args()
#     sys.stdout.write(str(calc(args)))


''' create packages, modules  '''

#  create __init__.py    = where u deploy the func   , so that people can use it to download it 
#  create setup.py       = create the package for ur init 
# from setuptools import setup

# setup(name='tushar"s_package' , 
#             version='0.1',
#             descripton ='code created by Tushar malhan' ,
#             author ='Tushar',
#             packages ='tushar"s_package',  # in ur func if u are importing any framework u can include here 
#             install_requires =[],
            # )

# Terminal >  pip install wheel 
#             python setup.py sdist bdist_wheel





#     regualar expressions

# [abc]               * or ?  = occurs 0 or 1 times 
# [^abc]   =startwith            +   = 1 or more times 
# [abc$]   =endswith             +   = 1 or more times 
# [a-z]               {n} = occurs 3 times 
# [A-Z]                 
# [a-z A-Z]
# [0-9]              {y,z}  - occurs atleast y times , but less than z times 

# \A   = if specified char is in start
# \b   = search for string in whole para
# \d   = search number   [0-9]
# \w   = prints each character or number in str  [a-z A-Z 0-9]   
# str\Z= prints if word is at end of line 

# a ='''hi tushar malahn 7 , today ur licky number is 3,6,9 which is also the nmber that tesla thaught the world runs on it . 9 ==07
# today i started my journey again with my base formula'''
# x = re.search(' formula',a)     # returns first occurance of the word 
# # print(x)
# lis = re.findall('tushar',a)
# # print(lis)                      # returns that string in a list , else returns empty list 
# sea = re.split(r'9',a)           # splits the text based on str pattern 
# # print(sea)
# replac = re.sub('7','369' ,a,1)   # replaces the string
# # print(replac)                     # here 1 = specifies the count of replacements

# a=re.search(r"\btushar", a)        
# # print(a)

# txt = "098 tusj"
# x = re.findall("\d", txt)
# # print(x)

# x1 = re.findall('\w',txt)
# # print(x1)
# z = re.search('j\Z',txt)
# print(z)

# email = re.findall(r"[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+\.[a-zA-Z]+",str)
# print(email)
# we group in []  + > give count more than one 

'''  pythonw <pyfile>  = run py file in  background  - cd into dir and pythonw filename 
stop the file by finding the pid from task manager and do    = taskkill /F /PID id_num '''



para ='''
print(len(list(filter(lambda x:x==0,a))))
print(sum(list(filter(lambda x: x==1,a))))

a=[1,1,1,0,0,00,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0]
print(sum(a))
print(len(a) - a)

a=[4,5,6,2,7,1]
t = 10
for ind,elem in enumerate(a):
     for sec_elem in a[ind+1:]:
          if elem + sec_elem ==t:
               result=(elem,sec_elem)
               print(result)
print(len([ele for ele in a if ele ==0]))
'''





# os.chdir(r'D:\Users\tusha\Downloads\ohio_linux.pem')
# files =os.listdir()
# p=([file for file in files if file.startswith('ohio')])
# os.system("systeminfo")


''' connecting to linux remote server '''
# import paramiko

# ssh_client = paramiko.SSHClient()
# ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# ssh_client.connect(hostname ='3.137.166.213' , 
# username='ec2-user', 
# password = 'paramiko123', 
# port = 22,
# key_filename =r'D:\Users\tusha\Downloads\ohio_linux.pem')
# print('connecting to youre remote server ')

# stdin, stdout, stderr = ssh_client.exec_command('whoami')
# stdin, stdout, stderr = ssh_client.exec_command('ls')

# # stfp_client = ssh.open_sftp()   # throw files to ur server
# # stfp_client.get('/home/ec2-user/test.py','paramiko_downloaded_from_remote_server.txt')      # from remote path   ,  to local path 
# # stfp_client.chdir('/home/ec2-user')    # now sftp client points to this location , no need to mention in download remote path
# # print(stfp_client.getcwd())
# # stfp_client.get('test.py',r'D:\Users\tusha')
# # stfp_client.put('projects.py','/home/ec2-user')       # from local > to remote server 
# # stfp_client.close()
# # ssh.close()

# a=stdout.readlines()
# print('Connection successfull ')
# print('Output: ', a)
# print('Error : ', stderr.readline())
