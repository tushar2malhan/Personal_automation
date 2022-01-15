''' git  '''
# push files to main branch >            git branch -m master main  OR        git branch -M main
# get fetch what new updates are made
# git checkout  commit_id      - get file back
''' linux shell '''
# change tusha/ name dir       - can't
# play mp3 file in linux shell - use 3 party tool

''' understand 
before google - we have dns  = when someone searched from google 
acquired by goggle
urls companies have their respective server , dont use google servers 
computers not connected to internet called standalone  , local server - not shown to world ,but like UAT 
local host =  http:// 127.0.0.1
any computer without internet is called Standalone

'''
#DONE if a.split (' ') print(a) = str     if b = a.split(' ') print(b) = list
# >>> because split function makes string to a list , so in str methods we need to apply the method to bring the output called implicit functions 

# pyc - py cache > its an optimized version of py file , They contain the "compiled bytecode" of the imported module/program so that the "translation"
# from source code to bytecode (which only needs to be done once) can be skipped on subsequent imports if the . pyc is newer than the corresponding
# pip install virtualenv | python3.9 -m venv name    |  source name/bin/activate
# py -m pip install --user virtualenv
# py -m venv env
# .\env\Scripts\activate

#  values have same id   | typecasting int(input)
# 0 , ''  ,  None =  False    |   if -1 or 0.4 or ' ' = true
#           zero = int(False)
#           one = int(True)
#           hundred = int(f"{one}{zero}{zero}")

# DATA TYPES
# list  []                 - can be updated , can  of different data types
# array []        - same as list but here same data types present
# tuple ()                 - can't be Updated
# dict dict() or {1:''}   - can be updated  , cant be updated In ITeration
'''     Access  d['hmm'] - gives value of the key |  a=d1.get(1.3,'ok') print(a) = give DEFAULT value if not present 
        ADD     # dict['hmm']=True  |  d[2] = d[2] +' ok' | d[2] = d[2].split()  | d[2].append('Tushar')
        DELETE  # del dict['hmm']   |  dict.pop('hmm') 
        Update  # animals.update({animal:1})   else   animals.update({animal:k[v]+i})  or print(animals ,**animalss)
'''
# set  set() or {1,2,3}    - unique items , can;t be updated
# in str b   =  we apply the functions DIRECTLY  on it and print it directly
#       print(a.lower())
# in data types - list , dict , set , tuple =  after the function is set , it's saved like function order
#       a.sort()  ,     print(a)
#

#  _ is last value in shell and can be called as UNNAMED VARIABLE   and in string it is ignored - print(11_11) == 1111
#  use zip to concatinate list and variables print(zip('a','b')(1)(2))  , in respect to Dict where we need to map iterations with var
#  == compares values between 2 , though id is not same     <>  is checks the id of the vars

# LOOPS
# for a,y in enumerate(range(10,0,-1)):
#     print(a,y)
    # print(y)
# SHORT FORM OF loop  print(*a)           ==  end with space (' ') automatically
# a = iter(['e',42,2,4,2])     # print(next(a))

# FILE
# when u read a file , u print out with read   print(f.read()) not print(f) > it throws error
# when u repeat code - use function
# INSIDE COLLECTION MODUEL >>> DEFAULT DICT  , ORDER-DICT , COUNTER , CHAIN MAP NAMED TUPLE
# data = json.load(json_file) == python dict , data2 = json.dumps(python_dict) == json_file


# d ={0:'Lol',1.5:' K','hmm':'',1:'ok2',2:'two',3:'ok',True:'alright',True:'damnn',45j:False ,True:'ok', False:5j}
# d1 ={0:'','hmm':'',1.5:{'name':'tushar','1':'Malhan'},int('1'):'tusharmalhan@gmail',
# 2:'two',3:'ok',True:'alright',True:'damnn',45j:'bool', False:'false'}


# Functions
# from intro import a1   # must be same dir
# global needs to be declared first , if u need to use
# any global variable will overcome , even if it's inside function inside of function
from math import copysign, e, perm
import os           # print(dir(os))
import collections  # print(counter(animals))
import calendar
import re
from typing import DefaultDict, Tuple  #calendar.month(2021,6)
import requests      # a = requests.get('https://www.wwe.com')
import sys           # print(sys.argv)  #python test.py tushar malhan
import csv           # with open ('path')as f: csv.reader(f)
import time          # time.sleep(2)
import random        # print(random.randint(1,10))
from functools import *   # 
# f = DefaultDict(bool)    # default value passed if key not present in dictinary 
    # f['ok']=1
    # print(f['d'],f)

# a = sm(3)  # we can assign function to the variable
''' remember what does the function returns ,
 thats what you apply when u call the function 
 [ whether u r returning executable func() or just returning function]'''

# 'NoneType' object is not callable   > when u call function but there;s no func to execute  return_func()()
# so when u return - we need to call it as wel ()

# DECORATORS -  just function that take function as first parameter and return a function

# def func (number):
#     return number

# a = func(2)       # assign functions to variable
# print(a)
# print()

# def func1():
#     def func2(n):      # Defining functions inside other functions
#         print('helo')
#         return  n * 2
#     return func2     # if im executing inner func down , why should u call it in outer func

# print(func1()(2))
# print()



'''  think decorators like creating class without self  where decorated function is referring as the  instance of class  '''


# def hi(func):
#      print('hello this is the decorator ')
#      def wrapper(a):
#           print(f' calling {a} from inside the wrapper')
#           # return a+'hi'
#           return func(a)              # This  refers to the decorated function called  , where it gets called accordingly
#      return wrapper
''' here a == value |  means wrapper function is call function only  |  if called func(a) means print what is called in call function line 135'''
# @hi
# def call(val):
#      print(val+'malhan')     

# call('tushar')



# def f1(func):
#     def inner(required, *args, **kwargs): #  thats y , we pass these params here
#         print('hi 1')
#         # original_func(required , args,kwargs )   # parameters  [ like self.args = args ]
#         print('end 3')
#         # print(required , args, kwargs)
#         # func(required,args,kwargs)            # after setting attribute , how u want to display the content  
#     return inner

# @f1
# def hi(required ,args,kwargs):  # inner func == hi()
#     print(required)
#     print(args)      #parameters assigned
#     print(kwargs)

# hi('tushar','malhan')
# hi(6,34,56,6,tushar='hello',lname ='Malhan')
# hi(12,3,4,a= input(' args ') , b = input(' kwargs ') )
#        arguments given like in class   |  # args with input values


# def decoratorr(func):
#      def wrapper(n):
#           n = n +'ok tis this tis tushar malhan'
#           func(n)
#      return wrapper

# @decoratorr
# def hi(n):
#      print(n+'1')

# hi('tushar')


''' dont hard code functions , pass it in decorators like variables
def give_me_output():
    return ' Actual func '
def dec (main_func):
    def wrp(func):
        o= '*' +func() +'*'            # return the wrapper without variable , shows u In Tuple ()
        return o                      # put the wrapper and assign to a variable and return
    return wrp()
dec(give_me_output)
''' 

''' This behaviour is the syntactic sugar because writing @decorator is same as calling f = decorator(f) after it.'''

''' if u cant have keys to alphabets or list  use numbers as key to identify and do multiple changes   '''



# CLasses

# class parent:
#     def __init__(self,x,y,*args):
#          self.x = x
#          self.y = y
#          self.args = [2*self.x   if self.x < self.y  else 0]
#          for a in self.args:
#              print(a)
#     def print(self):
#         print('y=',self.y  if self.x > self.y  else self.y)
#         print('both ',self.x,self.y)
#         print('args ',*self.args)
# class child(parent):
#     def __init__(self, x, y ):
#         super().__init__(x,y )
#     def print9(self):
#         print(self.y if self.y < self.x  else 1)
#         print(self.x , self.y )
#         print(self.y)
#     def prin(self):
#         print(self.x , self.y , self.args )

# a1 = parent(2,10)
# print()
# b1 = child(1,2)
# b1.print()


# print(obj.add())




# class attributes > self.object attributes > defining attribute manually for the object
# CHeCK Priority  #1 manual define      > parenta.age =53  ,
#                 #2 constructor define > self.age = 21
#                 #3 args passed        > ob=person(19) ,
#                 #4 default args       > def _init(age=18)
# class and object attributes VALUES CAN BE OVERWRITTEN

# def __init__(self,color,interest,age,name):     # if ur calling parent , u need to bring the  params in child object and thus give arg as well 
#                                                       otherwise give default args
# Under hood this def is access by class name    
#         Teslacar.totalwheel(a)
# 
#         super().__init__(name,age )             # this is mapped with parent attribute , when passing arg u need to take care there only
#                                                       so LOOK ONLY INIT OF PARENT , CHILD VALUES WILL BE PASSED IN SAME INIT ORDERR LIKE PARENT INIT 
# super().__init__ ()                 #  when u pass the arguments IN child init order of parent init parameters will be same as child arguments  
   
# class animal:   # LOOK thIS EXAMPLE
#         def __init__(self,n,a,*h):   # if args brought from parent 
#             self.n =n
#             self.a=a
#             self.h =h

#         def print(self):
#             print(self.n,self.a,self.h)
# # a = animal('n','a','h')

# class Lion(animal):
#         a1='Lion'
#         def __init__(self,a,n,h,l=(),*k,**kw):
#             super().__init__(a,n,h)
#             self.k =k
#             self.kw=kw
#             self.l =l
#         def printt(self):
#             print(self.l,self.a,self.n,self.h,self.k,self.kw)
#             # l ='L', a='N' , n='A', h='H'                        # data type comes first
# # ''' if parents super init is called , then params will be passed accordingly , would ignore params value in child class'''

# b = Lion('A' ,'N' ,'H', 'L', 'K','O',Tushar='name')   
#     # for those 3 parameters , Parent args will be given in child class, 
#     # they will do their own job & make those args as specified in parent ,
#     # same -child   will return args as specified  
# a.print()
# b.print()
# b.printt()
# print(b.a)
# print(b.h)
# print(type(b.h))
# print(type(b.h),b.h)
# print(type(b.l))
# print(type(b.k),b.k)
# print(type(b.l),b.l)

# DUNDER METHODS 
        # def __repr__(self):       #  used in shell 
        #     return 'malhan'      
        # def __str__(self):       # get a string representation of object
        #     return 'tushar'      # print(a)  or object  prints('tushar')
        # def __iter(self):     # IN CLASS  with iter u can print object in range 
        #     return self        print(i) for i in range(abc)        #abc is object    

# operator overloading   # add two objects attributes  objects ,get result    [ a.__add__(12) or a+12 = same ]
        # def __gt__(self,other):
        #     return self.a1 > other.a1     # gt =  greater then    [ if other.a1 = give object value ]
        # def __sub__(self,other):          # lt = less than 
        #     return self.a1 - other        # subtract here         [ with other value , not of objects value ]

         # print(a > c)
         # print(c- 1)
        # def __add__(self,other):          # IF more than 2 objects   (self,other)
        #             # return self.a1 + other.a1   # just return both objects for 2 object 
        #         total= animal('1',2,'3')  # for more than 2 objects , we create new objects 
        #         total.a= self.a+other.a
        #         return total

        # a= animal('a',1,'h')
        # b= animal('b',2,'h2')
        # c= animal('c',3,'h3')
        # print(c.a,b.a,a.a)
        # print((a+b+c).a)


# class base:
#     def __init__(self,response):
#         self.response=response
    
#     def __call__(self):
#         print( self.response)

# a = base(1)   # it calls __init__()
# a()           # it calls __call__()


# str = 'Hello World String'    
# print(str(10))                             =     'str' object is not callable  means calling string as a function 



# INHERITANCE
#  call super() , here order will be specified accordingly set in child 
# def make_sound(self,sound,eyes):
#           print('child')       WONT OVERWRITE HERE
#           super().make_sound()          # call both child and parent function    OR
#           super().__init__(sound,eyes)  # call parent attributes 
 

# for i in range(10):
#     print(random.randint(1,))
#     time.sleep(2)
# iteration and generetors > except list , evrything is iteratable 
# print iterations one by one  by iter(datatype) next(datatype)
# a = iter([1,4,4,5,])       # | a.__iter__()    ,    print(a.__next__())
# print(next(a),next(a))   # | isinstance(12, Iterable) > false or isinstance([1,2,3],list) > true


# yield is used to convert a regular Python function into a generator.  = inorder to save ram > so that u dont waste ur server RAM 
# generate values on the fly by  __next__() = printing one by one 
# def ok(n):
#     for i in range(n):
#         yield 'yield called'
#         yield 1
#         return 'ok'
# o=ok(2)
# print(o.__next__()) # or   next(o) 
# print(o.__next__())
# print(o.__next__())

# i=iter('tushar')
# print(i.__next__())
# print(i.__next__())



# class engine:
#     name ='ENGINEXX '        # class attribute
   
#     @classmethod              # methods created to change class attribute 
#     def update_name(cls,new_name):
#         cls.name=new_name

#     def __init__(self,oil):
#         self.oil =oil
#         self.__sn =10       # private attributes - child can't see 
#     def __fill_oil(self):   # private methods  - only used by class 
#         self.oil +=10 
#     def __burn_oil(self):
#         self.oil -=10
#     def get_sn(self):
#         return self.__sn    # getter method  - returns private variable of parent when called 
#     def Move(self,km):
#         for i in range(km):
#             self.__burn_oil()
#     def goahead(self,km):
#         print(f'{km} moved in km')

#     def fillup(self,oil_in_ltr):
#         for i in range(oil_in_ltr*10):
#             self.__fill_oil()    

# class Motorbike(engine):

#     # def __new__(cls):
#     #     print('im new method in motorbike')
#     #     return super().__new__(cls )

#     def __init__(self, oil_count,name,color):
#         self.name =  name 
#         self.color = color 
#         super().__init__(oil_count)   # HERE  parent attribute can be changed when called 

#     def __iter__(self):
#         return self
#     def accelerate(self,km):
#         self.Move(km)
#         super().goahead(km)           # passing var  # calling parent method 
    
#     @staticmethod                     # without self , create method 
#     def hi():
#         print('hi')
#     def fill(self,ltrs):
#         self.fillup(ltrs)

# harley = Motorbike(20,'Harley','Black')
# # harley.goahead(10)
# # print(harley.get_sn())                 # calling parent's private attribute from child object 
# a= engine(1)
# print(a.name)
# # a.name ='ENGINEY'                   
# print(a.name)
# a.update_name('tushar')
# print(a.name)


# print(harley.oil)
# harley.accelerate(200)                   # calln parent and class methods                     
# harley.hi()

 
# CLASS METHODS     - change class attribute like a function - decorator,   - only used to change class attribute


class server:
    engine ='apache'
    def __init__(self,name,typee,price):
        self.type=typee
        self.price=price
        self.name=name
    def __str__(self):
        return f'{self.type , self.price, self.name}'
    
    @classmethod                 # make changes only for class
    def changengine(cls,val):
        cls.engine=val
    
    @classmethod
    def from_str(cls,str): # from str create instance of class 
        # params = str.split('-')
        # return cls(params[0],params[1],params[2])    
        return cls(*str.split('-'))
# ''' this list of params -values will be taken by cls which is server([0],[1],[2]) or classname '''

# a1=server('apache-ubuntu','opensource','APC')
# b1=server.from_str('LINUX-PAID-VPC')                 # new instance with class method         
# print(b1)

# # print(a1)
# print(a1.engine)
# server.engine='APACHE 2'                            # this way u can hardcode it  , USING CLASSNAME 
# print(a1.engine)
# a1.changengine('APACHE 3 ')                        # THIS OVERCOMES HARDCODED , AS FUNC USED IT 
# print(a1.engine)





'''public , protected , private variables in classes '''

# class Difference:
#     public           = 9   # accessible to everyone
#     _protect_variable= 10    # only derived class like child  or itself means parent  can use it
#     __private = 11          # only used by the class and their instances !
#     def __init__(self, a):
#         self.__elements = a

# a= Difference(1)
# print(a.public)
# print(a._protect_variable)
#                                  # print(a.__private_variable)   # ERROR  >  u can't access it normally 
# print(a._Difference__elements)   # >>> access private variables like this !
# print(a._Difference__private)    # >>> access private variables like this !



'''  ALTERNATIVE OF LOOPS    '''
# takes function as 1 param  : depending upon function param takes  2 parameteres   
    # [takes each iteration , no need of loops here ]
    # [if 2 args then in lambda then map(a,b) ]

#| WRAPP THEM IN  any data type or it will show map object ERROR |

# MAP     - map  the function with all  iterables and give result  for all iterators 
# FILTER  - create the function , it will exclude the values GIVE VALUES THAT MATCH THE FUNCTION
# REDUCE  - performs the operation for all the items in the iterables with the previous result 
#          reduce (func , iterable , initial_value )
#   
#              l =[1,2,3,4,4,5]
#              prod = reduce(lambda x,y:x+y,l,1)
#              print(prod)
        # print( list(map(lambda x:isinstance(int(x), int),input('number ').split(' ')))   )
        # l=[12,[], 10,[], 9, 56,[], 24]
        # print(list(filter(None , l)))

        # print(list(map(lambda x,b: (x,b), a,b)))
        # a=tuple('90')
        # b=[100] 
        # print(list(map(lambda x,y:{x:y}, a,b)   )
# a= [ 5,4,4]
# b= [ 1,2,3] 
# def m(n,n2):
#     return n*2 , n2*2  # each iteration is multiplied and sent as in a tuple ()
# print(list(map(m,a,b)))   # can   BE USED AS ZIG ZAG BETWEEN 2 DATA TYPES 

    # mylist = [5, 4, 6, "other random stuff", True, "22", "map", False, ""]
    # filterr =(list(filter(lambda x: isinstance(x, int) , mylist )))
    # print(filterr)

# a= [ 5,4,4]
# b= [ 1,2,3] 
# a1=a+b  # key 
# b1=tuple(a+b)  # value 
# print(f(a1,b1))
# print(list(map(lambda x,b: {x:b} , b1,a1)))   # can put int , as it's not iterable 
# print(dict(zip(range(2),[1,3])))       # TAKES SAME ITERATIONS LIKE MAP , FILTER, REDUCE 

'''  @ zip  and map, filter,reduce takes same iteration values 
     print(tuple(zip(a1,b1)))  | # print(list(map(lambda x,y:(x,y),a1,b1)))
'''


# JOIN             # here int won't join  =  so use for loop and use end='' to join int 
# lis=['tushar','1','2','3,4']
# print(' - '.join(lis))


# matrix = [[1, 2, 3, 4], [4, 5, 6, 8]]
# for first_list in range(len(matrix[0])):           # 4 iterations
#     transposed_row = []
#     for each_list in matrix:
#         print(each_list)
#         transposed_row.append(each_list[first_list])
# print(transposed_row)


# c = a,b
# res = [i for j in c for i in  j ]   # if nested loop look single iteratorations wont come first 
# print(res)


# try:
#     choice = int(input('f '))
#     print(choice)
# except KeyError:
#     print('No str ')
# except ValueError:
#     print('only int allowed ')
# print(array1)
# for i in array1:
#     if i 

# a=[1,2,3,4,5,4,5.6]
# print(a)
# a=[15,21,90,8,76,54]
# def ar(arr):
#     max = 0
#     runner =0
#     for i in range(len(arr)):
#         if arr[i]> max:
#             runner = max            #  2 runner up 
#             max =arr[i]          # max value in list 
#     print(runner)
# ar(a)

# def an(n):
    # python_students= []
    # for _ in range(n):
    #     name = input(' Name ')
    #     score = float(input(' Score '))
    #     python_students.append([name,score])     
    # second_highest = sorted(set([score for name, score in python_students]))[1]
    # print('\n'.join(sorted([name for name, score in python_students if score == second_highest])))
# an(2)    


'''
Multiple if's means  execute all IF's whereever possible , 
[  BOTH " IF's " statements are being evaluated. The computer sees them as two separate statements:  ]

where as in case of elif, if one 'IF' condition 
satisfies it would not check other conditions  and print the single true condition
'''




''' questions                                                        ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||                                                                            '''




#Q 1 There are two players joey , chandler having candies . 
# Create a game where when 
# either one of player is left with to give candies which are not enought will lose 
# In first move Joey gives Chandler 1 candy so, 
# Chandler has 3 candies and Joey has 0.
# In second move Chandler gives Joey 2 candies so, Chandler has 1 candy and Joey has 2.
# In third move Joey has to give Chandler 3 candies but he has only 2 candies so he loses.


# count_Joey = 0
# count_chandler = 2
# for i in range(1,4+1):

#     if i ==1:
#         count_Joey-=i
#         count_chandler+=i
#     elif i ==2:
#         count_chandler-=i
#         count_Joey+=i
#     elif i ==3:
#         count_Joey -=i
#         count_chandler +=i
#     elif i ==4:
#         count_Joey +=i
#         count_chandler -=i
# if count_Joey<1 :
#     print('joey lose')
# elif count_chandler<1:
#     print('chandler lose')

# print('Chandler count =',count_chandler)
# print('Joey count =',count_Joey)






# each police can cought theif only once 
# police cant catch if thief is k units away 

# Q how many theifs in total will be cought ? 
# a= ['p','t','t','p','t']
# k = 1
# ans = 2
# count_theifs = 0
# moves = 0

# police=([i for i,s in enumerate(a) if s =='p'])
# thief=([i for i,s in enumerate(a) if s =='t'])

# a1=list(zip(police,thief))
# c=0
# for a,b in enumerate(a1,start=1):
#     c+=1
#     # print(a,a1)





# count = ''''''list(zip(police,thief))
# for i in count:
#     count_theifs +=1
#     moves +=1
# print('total count of theifs = ',count_theifs)
# print('total moves = ',moves)

# sec_last=len(a)-2
# c_last=len(a)-1
# if a[0] =='p' and a[1] =='t':
#     count_theifs+=1
#     moves +=1
# if a[sec_last] =='p' and a[c_last] =='t':
#     moves +=1
#     count_theifs +=1

# print('count of theifs = ',count_theifs)
# print('total moves = ',moves)




'''
Ross has N students in his class this semester. The ith student's favourite number is F[i]. 
The ith student is a boy if G[i] is 0 and is a girl if G[i] is 1. 
Now, Ross wants to create an array Arr filled with non-negative integers with values less than 1018. 
Arr is liked by students if it satisfies following conditions:
If ith student is a boy, Arr[i] should be less than or equal to F[i].
If ith student is a girl, Arr[i] should be greater than or equal to F[i].
Sum of all the elements of Arr[i] should contain "47" as a substring.
Help Ross find how many arrays exist that are liked by students. As answer can be huge, find answer modulo 1000000007.
Input
The first line of input contains a single integer N.
The second line of input contain N integers where ith integer denotes F[i].
The third line of input contain N integers where ith integer denotes G[i].

Constraints:
1 <= N <= 8
0 <= F[i] < 1018
0 <= G[i] <= 1
Output
Print a single integer denoting how many arrays exist that are liked by students modulo 1000000007.

Sample Input
2
2 150
0 0

Sample Output
6
Explanation: Required arrays are: [0, 47], [1, 46], [2, 45], [0, 147], [1, 146], [2, 145] '''
''' thats it '''


# n=None                                 # n = number of students 
# n[i] =f[i]                             # i'th  student fav number is f[i]
# n[i](student)=='boy' if g[i] ==0 else 'girl'    # The ith student is a boy if G[i] is 0 or it is a girl if G[i] is 1
# arrayy=[>0 <1018]  #
# if n[i] =='boy'    arr[i] <= f[i]
# if n[i] =='girl'    arr[i] >= f[i]
# sum(array) =='47' as substring    # means total_of_sum_of_array = [47]  should contain 47
#   Print a single integer denoting how many arrays exist that are liked by students modulo 1000000007.

# The first line of input contains a single integer N.
# The second line of input contain N integers where ith integer denotes F[i].
# The third line of input contain N integers where ith integer denotes G[i].







# class vector:
#     def __init__(self,vec):
#         self.vec = vec
#         self.op = 'op'
#     def __str__(self):
#         str1= ''
#         index=0
#         for i in self.vec:
#             str1 += f'{i} a {index}  '
#             index +=1
#         return str1

#     def __add__(self,vec2):
#         newlist=[]
#         for i in range(len(self.vec)):
#             newlist.append(self.vec[i] + vec2.vec[i])   
#         return vector(newlist)   
#     def __mul__(self,vec2):
#         sum=[]
#         for i in range(len(self.vec)):
#             sum.append(self.vec[i] * vec2.vec[i])
#         return vector(sum)                            # IMPORTANT HERE 
# # we choose the parent class string to print our values     vector(list) 

# v1 = vector([1, 4 , 6] )
# v2 = vector([1, 6 , 9] )
# print(v1)
# print(v1+v2)
# print(v1*v2)






#  SAME FROM ABOVE 


    # def call(self):
    #     index=0
    #     for i in range(len(self.vec)):
    #         print(f'{self.vec[i]}',index , sep= 'a' ,end=' ')
    #         index +=1
# class vector:
#     def __init__(self,vec):
#         self.vec = vec
#     def __str__(self):
#         str1= ''
#         index=0
#         for i in self.vec:
#             str1 += f'{i} | {index} '
#             index +=1
#         return str1

#     def __add__(self,vec2):
#         newlist=[]
#         for i in range(len(self.vec)):
#             if len(self.vec) > len(vec2.vec) or len(self.vec) < len(vec2.vec):
#                 print('error')
#                 break
#             else:
#                 newlist.append(self.vec[i] + vec2.vec[i])
#         return vector(newlist)
    
#     def __len__(self):
#             return True

# a = vector([1,3,3])
# b = vector([1,5,4])
# # a.call()
# print(a+b)
# print(len(b))
# print()

#   def __len__(self):
#         return 1
# n = number()
# print(len(n))


#   INHERITANCE  SUMMARY 
# print( object.attribute='' ) ,     from parent in child class    >>> same attribute name from parent and assigning new values inside child attribute
# obejct.call() : self.name = '' ,   from parent in child clas     >>> same function name and assign child values 
# if __init__ of parent class > class child(parent): >> tushar = child('attr1','att2','attr3')
# using  the class method  WE ALWAYS USE cls.attribute = that make  changes to default ATTRIBUTE  of class which is already predefined. 
# print(B.var2)            # u can't access class attributes directly 
''' class methods by calling parent or using class method to print class method '''
# usind super().__init (attributes) >>> inorder to inherit same attributes or methods  from parent to child but can assign new values , 
#                                       if not then = parent's values will be copied to child |    
#                                        super().__init__(price)    # without super u can't print parents init attribute  like pr 
# using DEF FUNCTIONS USED  ARE FOR == changing and naming only OBJECT ATTRIBUTES  not class attributes 
# but if you want to change class attribute in def FUNCTION = use @classmethod above def to give the class attribute as a variable 
# @property   >>>  make the def function a string or an attribute 
'''   @property           with property u call the function like a string 
    def email(self):
        return(f'{self.name}.{self.lname}@gmail.com')
when u will call this object >>>    print(tushar.email)    (not tushar.email())
'''
# IN getter = we CAN CALL PRIVATE ATTRIBUTES  ALSO !
''' @property
    def age(self):
          print("getter method called")
          return self._age             
tushar = employee()
tushar.age =20            print(tushar.age)
'''
       
# IN setter =  WHEN ANY FUNC CALLED WITH SETTER , WE CAN DYNAMICALLY SET THOSE ATTRIBUTES ACCORDINGLY 
'''         WE NEED TO SET PROPERTY AND THEN CALL THE SETTER FUNCTION INORDER TO DO SET CHANGES 

 @email.setter       # whenever any object  changes email           >>> tushar.email ='tushar.malhan@gmail.com'
#or use this func email = self.fname , self.lname will also be updated 
    def email(self,string):
        print('seting now ...')
        name =string.split('@')[0]
        self.name = name.split('.')[0]            # new self.name is set 
        self.lname = name.split('.')[1]           # new self.lname is set 
    @email.deleter     # call this func by        = del tushar.email
    def email(self):
        print('deleting now ! ')                  # when called we delete , so new self.name and self.lname is set 
        self.name =None
        self.lname =None
'''
# OVERLOADING 
# by __add__ , __sub__ , __mul__ , __len__ , __str__  >>> do operations on different child objects  > inorder to combine them or use them inorder to print their respective values as one.
# [  print (object 1 of class + object 2 of class)        # overloading ex  ]








'''  examples  '''

# class A:
#     def __init__(self,name,lname):
#         self.name=name
#         self.lname=lname

#     def explain(self):
#         print(f'employee is {self.name ,self.lname}')
    
#     @property
#     def email(self):
#         if self.name==None or self.lname ==None:
#             return f'email not set.kindly set with setter  '
            
#         return(f'{self.name}.{self.lname}@gmail.com')
    
#     @email.setter       # whenever someone changes email 
# #or use this func email = self.fname , self.lname will also be updated 
#     def email(self,string):
#         print('seting now ...')
#         name =string.split('@')[0]
#         self.name = name.split('.')[0]
#         self.lname = name.split('.')[1]
#     @email.deleter                        # call this func by  =    del tushar.email
#     def email(self):
#         print('deleting now ! ')
#         self.name =None
#         self.lname =None


# rohit = A('rohit','pathak')
# tushar =A('tushar','malhan')

# print(rohit.email)
# print(tushar.email)
# tushar.email='tushar.malhan@gmail.com'               # setter called 
# print(tushar.name)
# print(tushar.lname)                                  # new self.name and self.lname called 
# print(tushar.email)

# del tushar.email
# print(tushar.name)
# print(tushar.lname)
# print(tushar.email)



''' prefernce given first to child  def-methods , then  attributes , then class attributes  even if same name '''



# print(B.var)         # if class called  - it looked class variable ,first for his own class , then others 
# print(jimmy.var)     # if object called - it looked for instance varibale first for his own class

# son looks for his own attributes and methods FIRST , then if solution not found > then go to dad or grandparents attributes and methods 
#  - same attributes & methods called by son > will be overwrited and printed , if same_name methods not printed >>> son use parents methods
#  - once u overwrite methods or attributes of parents , they will be forgone  >>> so  use super().__init__()   = to use both attributes and methods of parents and son

''' super method allows to access your parents methods and attributes , is placed under a function()'''






# from abc import ABC,abstractmethod
# class Shape:           # PARENT CLASS   force the functions to be printed in every CHILD  class 
#     @abstractmethod     # either use abstractemthod or  inherit ABC in class Shape(ABC )
#     def printarea(self):    #  printarea =  function will be mandatory for every  class - no class can ignore it !
#         print(0)            #  >>> WE CANT MAKE OBJECTS FROM @abstract method
# class rectangle(Shape):
#     type ='reactangle'
#     sides = 4
#     def __init__(self):
#         self.lenght = 6
#         self.breadth = 4
#     def printarea(self):
#         return self.lenght * self.breadth
# b = Shape()
# b.printarea()                # if base Shape (ABC)  = can;y create instance of parents 
# a = rectangle()
# print(a.printarea())

    


# iterative functions = using loops 
# recursive functoins = calling func inside func 

# a= list(map(int,input('- ').split()))
# print(a)

# def add(li):
#     if len(li) ==1:
#         return li[0]
#     else:
#         return li[0] + add(li[1:])
# print(add(a))


# def op(c,t):
#     print(c+t)
# print(__name__)
# if __name__=='__main__':
#     op(1,2)


# _ = '45'
# b = eval(_)
# print(type(b))     # evaluated the python string in respect to the actual data type 

# def f(st):
#     print(''.join([ i.lower() if i.isupper() 
#     else i.upper() for i in st ]))
# f('HackerRank.com presents "Pythonist 2".')

#  ==   value     , two  objects have same value 
#  is   checks id of variables , two references refer to the same object and match id 
# a=[2]
# a2=a       # a2 is same copy of a  # id (a) == id (a2)
# a2[0] =9
# print(a)
# c= a 
# print(c)   # c is new copy of a   # ie c = a[:]


# changes in string possible  by 

#   convering it into list , do changes by indexing and and then converting it into str by join 
#   another way is to do SLICING > where str[::5] +'k' + str[6::]

'''  pythonw <pyfile>  = run py file in  background  - cd into dir and pythonw filename 
stop the file by finding the pid from task manager and do    = taskkill /F /PID id_num '''

# import datetime



                              


# os.system('NUL > EmptyFile.txt')
# os.system('Notepad demo.txt')           # cmd to create new file 






''' run vscdoe on github by  using  .   on ur repo '''

# di = [
# {'name':'Sahil','age':25},
# {'name':'Vicky','age':10},
# {'name':'Abhi','age':24},
# {'name':'Rahul','age':36}]

# # print(  [(k,v) for each_dic in di for (k,v) in each_dic.items() ])
# d = sorted ([ (k['age'],k) for k in di ])
# print(d)
# [print(v,de['age']) for (v,de) in d]
# dec = sorted ([(k['name'],k) for k in di])
# re = [ dict_ for (k,dict_) in dec]
# print(re)




# def func1(a,b,c,var):
#      return var

# print(func1(1,2,3,'ok'))

# def func1(a,b,c,func):
#      print(5) 

# def called_func():
#      print('this is the func being called everywhere')

# print(func1(1,2,3,called_func()))

#                          print is executed first 
#          wherever func is called it will be executed then return value gets printed

##################################################################################


'''                 NESTED LOOPS                '''



# THINK OF ORDER BY IF IT IS SORTED TO GET HIGHEST VALUE
# for i in range(1):
#      print(l[::-1][0]) 
# get the last value from list 


# 
# l = ['small', 'medium', 'large']
# for i in range(len(l)):
#      for j in range(i+1, len(l)):
#           print('i = ',i,'j = ',j,'\tl[j] = ', l[j]) 
# first iteration j completely done , second iteration j reduce  by 1 because
# it is i + 1 so second loop = j(2,5) # 234 , third loop j(3,5) # 34 , last loop j(4,5) # 4



#         for j in range(i):
#               matlab i ek SAATH SAATH badh , each j iteration stores i'th iteration  (1, 22, 333, 4444 ....)
#               here i will be keep on reducing  | 
#               because range starts from i so j == (0,4)  , i == 1  j == (1,4)   ,i == 2 j ==(2,4)
#               means will keep on Increasing POSTIVILY based on outer iteration


#         for j in range(i+1,10):             | for j in range(i-1)  == positive loop
#               means NEGATIVE loop for inner iteration as it starts from (1,10) then j == (2,10) (3,10) ...





unsorted_list = [3, 1, 0, 9, 4]
sorted_list = []

# while unsorted_list:
#     minimum = unsorted_list[0]
#     for item in unsorted_list:
#         if item < minimum:
#             minimum = item
#     sorted_list.append(minimum)
#     unsorted_list.remove(minimum)

# first check the minimum value in unsorted_list , then add it to sorted_list and remove it from unsorted
# do it until unsorted list is not empty


# # print(sorted_list)
# print(unsorted_list)


