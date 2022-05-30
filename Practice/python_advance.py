






#                   print([ i if i!= 3 else '3 three' for i in range(6) if i>1 ])
#                      print( 1 if     ask.startswith( ('7','8','9') )     else 0 )
#                        if  kingdom_name.endswith (tuple(i for i in [ 'a', 'e', 'i', 'o', 'u'] ))




#                                           global variables

# global a : print(a)      
# create global variable  , use the same variable for the function , to call the global variable 
# when creating a function  => set this a inside function => func.a =1  => when func called func() , print(func.a)

# use it to create global and local variables inisde function
# globals()             # will return all global variables 
# x = globals()['a']    # will return specific global variable outside the function which is a


# print(globals()['x'])

# a = 5
# def h():
#     global a
#     a = 10 
#     print(a,'from h ')
#     def wrapper():
#         global a
#         a = 15 
#         print(a,'from wrapper')
#     return wrapper
# print(a)
# h()
# print(a)

# def get_var_from_func():
#     get_var_from_func.func_var = 'function variable'

# get_var_from_func()
# print(get_var_from_func.func_var)


#                                               nonlocal vs global  

from abc import abstractmethod
from operator import ne


def scope_test():
    def do_local():
        spam = "local spam"

    def do_nonlocal():
        nonlocal spam
        spam = "nonlocal spam"

    def do_global():
        global spam
        spam = "global spam"

    spam = "test spam"      # even after declaring and calling func 
    do_local()              # variable spam is not accessible outside the func
    print("After local assignment:", spam)          # test spam
    do_nonlocal()           # we declare non local to make spam accessible outside the func
    print("After nonlocal assignment:", spam)       # nonlocal spam
    do_global()
    print("After global assignment:", spam)

# scope_test()
# print("In global scope:", spam)


# non local makes the variable accessible outside the func , when function is called ()
# global cant do it
# global runs when u call the func , it will make the variable accessible to the func

#               difference between global and non local 
#  global is accessible to all the functions in the program
#  non local is accessible only to the function in which it is declared




#                           Decorators 


# In the above example, the greet function takes another function as a parameter 
# (shout and whisper in this case).
#  The function passed as an argument is then called inside the function greet.

# Why do decorators need wrappers?
# The purpose of having a wrapper function is that a function decorator receives a function object to decorate, and it must return the decorated function. before some_function() is called. 


#                           Closures 



a=9
def func1(a1,b,c,var):
    global a 
    a = 100
    return var

def func2(a2,b,c,func):
    global a 
    a = 200
    func()
    print(5) 
    print('a\t = ',a)
    return 'func2 printed out'

def called_func():
     print('this is the func being called everywhere')

# print(func2(1,2,3,called_func))
# print(func1(1,2,3,'ok'))
# print(a)
'''  we pass variables  as param '''



def create_adder(x):
    ''' decorator '''
    # print(x)
    def adder(y):
        return x+y      
 
    return adder #(9)         # what happens when we return the function
  
    # - 1 step ???   either give y arg   > adder #(9)          here in adder
    # - 2 step ???   or return the function ang give arg in > create_adder(15)(10)
    # - 3 step ???   or put the create_adder decorator in variable and give args twice
 
# print(
# create_adder(15)(10)
# )

# ok = create_adder(15)       # 3 step where 15 == x
# print(ok(5))




''' now we pass func as param '''



def printall(func,val=1):

    '''
    This is a decorator function
    taking func a parameter
    '''
    # print('greet func called Now executing your function')
    # print('no need to call the function again now \n')
    # print(val)
    print(' now @ printall  will automatically  call the function')

    def inner(age ,lastname = 'malhan',*args, **kwargs):
        ''' 
        we call the wrapper 
        so that func 
        dosent gets execcuted when called 
        in the decorated function and we store the return value in wrapper 
        which is returned in greet decorated function '''
        print('Calling decorated function')
        print ('Arguments for args: {}'.format(args))
        print ('Arguments for kwargs: {}'.format(kwargs))
        print('i know your name \t >',func.__name__)    # calling the function name  == decorated one 
        print(val,args[0]*args[1])

        print(f' age = {age} \t lastname = {lastname}')
        return func(age ,lastname,*args, **kwargs)
    return inner

# @printall
def random_func(*args, **kwargs):
    print('\n\nmain function  called')
    print(args[0],args[1])
    ...
    # print(args[1],kwargs.get('name2','Malhan'))
    # return 'args 0 * args 1 => ' +str(args[0] *args[1])


# real_decorator2 = printall(random_func, "value of printall ")
# real_decorator2(23,'malhan',7,2,5, name="rashmi", name2="tushar")
# print(real_decorator2(23,'malhan',7,2,5, name="rashmi", name2="tushar"))

# print(random_func(1,2,3, name="rashmi", x="z", name2="tushar"))

''' its better to caluclate the value of args and kwargs in decorator 
otherwise in the main function > the values wont be same'''

'''
#  we are 
printing and calling according to the decorator function  () which takes func as param
'''




def decorator(func):
    # def e():
        print(1,"Gfg decorator called before function")
        # called hello decorator  == func()
        return func ()
    # return e

# @decorator
def hello_decorator():

    print(2)
    print(3,"Gfg")
    
    def wrapper():
        print(4)
        print(5,"Hello")
        return 'hello'
    return wrapper

# print(hello_decorator()()())
# print(decorator(hello_decorator)())  # since func is already called , will throw error if tried to call 







'''                        multiple classes inheritance               '''


# class variables                = shared by all instances  without using super().__init__()
# class initilization (__init__) = multiple variables with different arguments  (multple children having different names or abilities)


class Parent1():

    Parent1 = "parent 1 "

    def __init__(self, name_1 ,*args,**kwargs) -> None:
        self.n = name_1 
        self.personality = 'patient' 
        self.args = args
        self.kwargs = kwargs
        # print('\t By default name_ is taken as ',name_1,'\n')

    def __str__(self) -> str:
        return f"\
         name is {self.n}\n\
         args is { self.args} \n\
         kwargs are { self.kwargs}\n\
         Personality is { self.personality}\
         "
    @staticmethod
    def static_method():
        print('\t this is a static method of parent 1')
         

# obj = Parent1('imaginary','i am ','arg of parent',name ='Gldy',age = 52)


class Parent2:
    ''' parent 2  '''

    def __init__(self,personality) -> None:
        self.personality = personality
    
    @staticmethod
    def static_method():
        print('\t this is a static method of parent 2')

    def __call__(self):
        print(f'\t used this to call for parent 2 parent which is {self.personality}')
    
        

class Child(Parent1,Parent2):

    child1 = 'child 1 '

    def __init__(self, name_1, *arg, **kwarg) -> None:
        self.name_2_bychild = name_1

        #    Copy Parent init with params  # mandatory 
        super().__init__(name_1, *arg, **kwarg)    
        #  - super() is used to access the parent class variable and methods  
        #    here init of parent class is overriden, so object will access this init variables 

        # self.personality = 'Aggresive'                    # override  # optional 
   
    @staticmethod
    def static_method():
        print('\t this is a static method of Child ')
    
    @classmethod
    def add_new__object(cls,string,string1):
        ''' Create new class variable & new obj from class method  '''
        cls.new_var = string1
        return cls(string)
    
    @classmethod
    def change_cls_variable(cls,value):
        print('\n\t Old value of Child class variable is ->',cls.child1,)
        print('\t Child class new variable given by child is ->',value)
        cls.child1 = value

    # @classmethod     >>>          # this class method only works for this class,not parents class 
    # so make sure if your changing parent class variable , dont use this class method on this func
    def change_parent_cls_variable(cls,value):
        print('\n\t Old value of Parent1 class variable is ->', Parent1.Parent1 )
        Parent1.Parent1 = value
        print('\t Parent1 class new variable given by child is ->',value)
        print('\t Look i confirmed it > ',Parent1.Parent1)
    
    def change_name_2(self,new_name):
        self.name_2_bychild = new_name
        print(f'\t name is changed to {new_name}')


obj2 = Child('tusharmalhan','i am ','arg of child',name ='Tushar',age = 23)

# obj3 = obj2.add_new__object('Obj_3','new_cls_var_2')
# print(obj3)
# print(obj3.new_var)
# print(Child.new_var)
# print(obj3.n)

# obj2()
# obj2.static_method()


''' child class can change both theirs class variable and parent class variable -(only by   Parent_class_name.class_variable = 'new cls var'  ) '''
# obj2.change_cls_variable('child_1 class variable  ')
# obj2.change_parent_cls_variable('parent_1 class variable  ')


'''                                 OVER-RIDING                           '''   
# Object looks First for instance variables  if not, then own class variable and then  search for inherited class variable
#  So if u want to access the parent class variable and methods , thats where we use super().__init__()

#  - if again variables name same "var2" , it will check position of super().__init__(), if called first then => B class instance Variable will over ride it
#    else if called after assigning "var2" value in child class  = it  will take variable from super ( PARENT ) class instance Variable
#           
#           # implicit call will call the parent class again and again [ in diamond shape class inheritance ] ,making it useless 
#           impilict call  ->  ClassName.__init__(self)
#           explicit call  ->  super().__init__()        or  super(ClassName,self).__init__()   == same 


'''      @property @getter @setter   and operator modulo  
-        make sure variable name and function name are not same  '''


class Trap():

    # private variable of class
    __private_class_variable = 'private class variable'
    # protected variable of class
    _protected_class_variable = 'protected class variable'

 

    def __init__(self,name) :
        self.name = name

    @property
    def email(self):
        ''' so whenever getter called we know about it '''
        print(f'Calling your email -> {self.name}@gmail.com')
        return f'{self.name}@gmail.com'


    @email.setter
    def email(self,new_email):
        ''' with setter we can change  other attributes too'''
        print('\nSetting your new  email ...')
        self.name = new_email
        print('Your new email is -> ',self.email)
  
    
    def __getitem__(self, index):
        ''' suppose  a is the object of class check and
        we want to get the value of a[0] as its a sequencial data type 
        we can use this method to get the value of a[0]
        else it cant subscribe to the object of class  check and throw error
        print(a[0])'''
        print('\n\t This will access your dict or string by the index ')
        return self.name[index]


    def __len__(self):
        ''' when u call object with len() method it will return the length of the object
        called from here 
        print(len(a))'''
        return len(['1',2,3])


    def __call__(self):
        ''' a() is  like a function '''
        print(self.name)

    
    def __add__(self, other):
        '''  
        where 2 objects a and b item and other gets added  
        print(a+b)     #   
        - This item will be taken from the constructor of the class
        '''
        return self.name + other.name
    
    
    def __mul__(self,other):
        return self.name +'\t'+ other.name * 2
    
    
    def __str__(self):
        ''' preference given first when object is printed as compared to __repr__
        print(object), print(self) to initate this '''
        return '\nThis class is for Practice , called by __str__ method'

   
    def __del__(self):
        ''' del object  to initate this method '''
        return ('Destructor called, Object deleted.')

print()
r = Trap('TusharMalhan')
# print(r.email)                # getter called here 
# r.email = 'malhan2'           # setter called here 

# print(r.email())              # getter called here 
# print(r.email_('malhan3'))    # setter called here 
# print(r.name)                 # without getter setter too , we can change attributes 

# print(r[0])                   # __getitem__()
# r()                           # __call__()
# print(len(r))                 # __len__()
# s = TrapArtist('Jimmy Malhan')
# print(r+s)                    # __add__()
# print(s)                      # __str__()
# print(r*s)                    # __mul__()
# print(r.__del__())            # __del__()

# print(r._protected_class_variable)                     # WE CAN CALL both PROTECTED variable of both class and instance >   DIRECTLY         
# print(r._TrapArtist__private_class_variable)           # for private , we need        object._classname__attribute  or getter method
# print(r.__dict__)                                      # call constructors params in dict format


''' 
PRIVATE ==       Even if variable or method is private or even if we access prvt attribute from parent class >>> 
|                we need  =  obj._classname__attribute  ==     CLASSNAME in between to call it  
|                else put private variable in public method and call it     DIRECTLY 

So Access private only by  :=   
|                        obj._classname__attribute   
|                        getter methods
|                        creating functions or private ones too

PROTECTED == means we can call both class and instance protected variable   DIRECTLY 
'''

#                       Diamiond Shape Inheritance

class Class1:
    def m(self):
        print("In Class1")  
     
class Class2(Class1):
    def m(self):
        print("In Class2")
        # Class1.m(self)
        super().m()
 
class Class3(Class1):
    def m(self):
        print("In Class3")
        super().m()         
        # Class1.m(self)  
      
class Class4(Class2, Class3):
    '''  given attribute is first searched in the current class 
    if it’s not found then its searched in the parent classes.
    The order that is followed is known as a linearization 
    of the class Derived and this order is found out using 
    a set of rules called Method Resolution Order (MRO).'''
    def m(self):
        print("In Class4")  
        super().m()                 # explicit call which will do the mro and make the parent class call once 
        # Class2.m(self)
        # Class3.m(self)            # implicit call which will make the class 1 twice
      
# obj = Class4()
# obj.m()

from abc import ABCMeta,abstractmethod

class A(metaclass = ABCMeta):
    @abstractmethod
    def hello(self):
        print('\
            -This is an abstract method which ensures that\
             all the child classes must create a method name hello()\
             or else it will throw an error\
            - This works only with direct class inheritance not with sub class inheritance \
            - Thus no object cant be created for this class where abstract class method is set')

class child1(A):
    def hello(self):
        print('Hello from child 1 class')
    ...


# a = child1()
# a.hello()
    



#                 Iterators VS  generators 

# normal_d = {1:'1',2:2,3:3,'4':4}
# while normal_d :
#     x = next(i for i in normal_d)
#     print(x)
#     normal_d.pop(x)

# both are iterators - generators are called infinite iterators
# yield is used to convert a regular Python function into a generator.  = inorder to save ram > so that u dont waste ur server RAM 
# generate values on the fly by  __next__() = printing one by one 

    # iter_list = iter(['tushar', 'For', 'Malhan'])
    # print(next(iter_list))
    # print(next(iter_list))
    # print(next(iter_list))

#        Generators =>      CALL IT AS MANY TIMES AS YOU WANT
#  It is another way of creating iterators in a simple way 
#  where it uses the keyword “yield” instead of returning 
#  it in a defined function. 
#  Generators are implemented using a function. 


    # def a():
    #     for i in markdict:
    #         yield i 
    # print(next(a()))
    # print(next(a()))


    # def ok(n):
    #     for i in range(n):
    #         yield 'yield called'
    #         yield 1
    #         return 'ok'
    # o=ok(2)
    # print(o.__next__()) # or   next(o) 



#                   log vs   log2

#               importing from log directory 
# import os,sys
# sys.path.append(os.getcwd())
# from log.old import * 




# Question :
markdict=[
    {"Tom":67, "Tina": 54, "Akbar": 87, "Kane": 43, "Divya":73},
    {"Tom2":672, "Tina2": 254, "Akbar2": 287, "Kane2": 243, "Divya2":273}
    ]


