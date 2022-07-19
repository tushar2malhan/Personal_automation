class C():
    def __init__(self,*args,**kwargs) -> None:
        self.name= kwargs.get('name')
        self.age = kwargs.get('age')
    
    @property
    def email(self):
        return self.name + '@gmail.com'
    
    @email.setter
    def change_name(self,new_name):
        print('name before',self.name)
        self.name = new_name +'@gmail.com'
        print('new email with new name',self.name)

# a = C(name='sachin',age=25)

# print(a.name)
# print(a.email)
# a.change_name = 'tushar'
# print(a.email)



# a,b =30,20
# max = 0
# min = 0
# min,max = (a,b) if a<b else (b,a)
# print('min =',min,'\tmax=',max)


def command_split(command):
    match command.split().strip():
        case["make"]:
            print("default make")
        case["make",cmd]:
            print(f"make command found:{cmd}")
        case["restart"]:
            print("restarting")
        case["rn",files]:
            print(f"deleting files:{files}")
        case _:
            print("didn't match")

# command_split('rn',)    #deleting files:test.txt

ar = [2,4,5,3,1]
