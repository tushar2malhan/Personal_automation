






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




#                           Decorators 


# In the above example, the greet function takes another function as a parameter 
# (shout and whisper in this case).
#  The function passed as an argument is then called inside the function greet.

# Why do decorators need wrappers?
# The purpose of having a wrapper function is that a function decorator receives a function object to decorate, and it must return the decorated function. before some_function() is called. 

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



#                           multiple classes inheritance

class Parent:
    _pro = 'parent protected variable '
    __prvt = 'parent private variable '
    def __init__(self,name):
        self.firstname = name
        print('parent init called ')

    def __private_method(self):
        print('Called parent private method')
        print(self.firstname,)
        print(self._pro,self.__prvt)
    
    def __call__(self):
        print('parent func called where name is {}'.format(self.firstname))
    

# a = Parent('Tushar')
# call private method __private_method
# a()
# a._Parent__private_method()
# print(a._pro,a._parent__prvt)

class Child(Parent):
    def __init__(self,age,name):
        # what does super() do ?
        # super() is used to call the parent class constructor
        self.age_of_child = age
        print('child init called too')
        super().__init__(name)

    def __private_method(self):
        print(f'Called child private method where age is {self.age_of_child}')
        # print(self._pro,self.__prvt)

# b = Child(25,'Rashmi')
# b()
# b._Parent__private_method()
# b._Child__private_method()


class Base:
    variable1 = 'parent cls variable'
    def __init__(self,name):
        self.variable1 = "instance var in Parent class "
        print('base init called')

class Child1(Base):
    variable1 = 'child1 cls variable'
    def __init__(self,age,name):
        # super().__init__(name)
        self.age = age
        self.variable1 = name 
        print('child1 init called')
        # Base.__init__(self,name)

class Child2(Base):
    # variable1 = 'child2 cls variable'
    def __init__(self,color,name):
        # super().__init__(name)
        self.color = color
        # self.variable1 = name 
        print('child2 init called')
        # Base.__init__(self,name)

# a = Child1(25,'Rashmi')
# b = Child2(23,'tushar')
# b = Child2('red','tushar')


# print(b.variable1)
# print(a.variable1)

#    Heirarchy in inheritance 
# from instance variable of class   > 
# to class variable of class        > if u dont have init in child class else it will look for init in parent class
# from inherited instance variable  > 
# to inherited class variable 

# java =>    pubic class name , private class name
# python =>   class public    , class _private

# public => Student class's attributes and also modify their values
# protected => Protected members of a class are accessible from within the class and are also available to its sub-classes. No other environment is permitted access to it. This enables specific resources of the parent class to be inherited by the child class.
# private =>  private. It gives a strong suggestion not to touch it from outside the class. 

# Every member with a double underscore will be changed to _object._class__variable. So, it can still be accessed from outside the class, but the practice should be refrained.





#                 Iterators VS  generators 

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


