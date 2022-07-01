import os , time 

main_dir =r"C:\Users\Tushar\Desktop\django_prac\Django_bot"             # CREATE UR DIR FIRST 

def add_under_installed_apps(main_dir,project_name):
    word = input('what needs to be  installed under installed apps  ? \n')
    if word:
        with open(fr'{main_dir}\{project_name}\{project_name}\settings.py') as f1:
            lines = f1.readlines()
        with open(fr'{main_dir}\{project_name}\{project_name}\settings.py','w') as f:
            for line in lines:
                    if 'django.contrib.staticfiles' in line:
                        line += f"\t '{word}' , \n"
                    f.write(line)
        print('Done changes in your settings.py file ')
    else:
        print('Alright then , if anything missed , kindly add it manually ')

def table_changes():
    os.system('python manage.py makemigrations')
    os.system('python manage.py migrate')

def runserver():
    os.system('python manage.py runserver')
def listdir_in_ur_home():
    return os.listdir(main_dir)      # [ listing down your files in this home directory ]
def chdir_to_home():
    os.chdir(main_dir)       # here ur projects and apps files will be installed  [ you can create ur directory and do changes accordingly ]
check_packages = os.listdir(r"C:\Users\Tushar\AppData\Roaming\Python\Python310\site-packages")    # if django , rest_framework , packages are  installed or not , set path where ur packages are installed in ur local system 



a  = input('Create Django from scrath ').lower().strip()
if a in ['django' , 'go','','l','ok','yes']:

    chdir_to_home()    
    r=None
    for i in check_packages:
            if i in ('virtualenv'):
                r = True
    if r:          
        os.system('python -m venv env2')
        print('Hope your virtualenv is not running in any other thread')
    else:
        os.system('pip install virtualenv && python -m venv env2')
        os.system('python -m venv env2')
    
    project_name = input('Project name ? \t')    
    if project_name in ['None',None,'',0,'empty']:
        print('\n Your Project should have a valid Name ')
        exit()

    for each_package in check_packages:
        if each_package in ('django','rest_framework'):
            time.sleep(2)
            print('django and rest framework are installed ')
            time.sleep(2)
            print('  ')
            r = True
    if not r:
        time.sleep(2)
        print('installing the workload')
        os.system(f'pip install django && pip install djangorestframework ')

    if project_name in listdir_in_ur_home():
        time.sleep(2)
        print('Project with that initials already present Done now !  , You are good to go now')
    else:
        os.system(f'django-admin startproject {project_name}')
        print(f'created new project named {project_name} in {os.getcwd()}') 
    time.sleep(2)
    

    app_name = input('App name ? \t ')
    (print('Your app should have a valid name'),exit()) if app_name in ['None','none',None,0,'','empty'] else print('\tGood to go')

    os.chdir(f'{main_dir}\{project_name}')    #  we put the app under project directory
    if app_name in main_dir+"\\"+project_name:
        time.sleep(2)
        print(f'{app_name}  Your app present with that initials \n ')
    else:
        time.sleep(2)
        os.system(f'django-admin startapp {app_name}')
        print(f'Your app also created in {os.getcwd()}')
    
    if project_name ==app_name:
        print('You cant have same initials for your project and app , kindly change it ')
        exit()
    else:
        print(f'Your project named {project_name} and app named {app_name} are ready now!  ')

    
    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 

    time.sleep(2)
    table_changes()
    # runserver()

    db = input('\nWanna install  postgres database ? \t ')
    if 'yes' in db:
        time.sleep(2)
        if 'psycopg2' not in check_packages:
            os.system('pip install psycopg2')
        else:
            print('Already installed ')
        enter = input('wanna go inside and start ? ')
        if 'yes' in enter:
                os.chdir(r'C:\Program Files\PostgreSQL\13\bin')                 # if u wanna enter shell directly kindly set ur path of Postgress/bin
                time.sleep(2)
                print('kindly provide credentials for your postgres database ')
                time.sleep(2)
                os.system('psql -U postgres -h localhost')
                time.sleep(3)
                exit = input('done changes ? wanna exit ')
                if 'yes' in exit:
                    os.system('exit()')
                else:
                    os.system('psql -U postgres -h localhost')
    else:
        time.sleep(2)
        print('\n ok then , using the db sql lite  by default')
    
    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    table_changes()
  

    ask= input('Wanna add rest_framework modules in ur views.py ?\t ').strip().lower()
    if ask in ['yes','yup','y' ,'ok','yes ',' yes']:
        with open(fr'{main_dir}\{project_name}\{app_name}\views.py','w') as f2:
            f2.write(
'''
# Imported almost everything , create your view accordingly , if anything missed kindly add it manually

from django.shortcuts import render
from django.http import HttpResponse , JsonResponse
from requests import api
import json

from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User          # get all the users  in ur account 

from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework. parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token             # just like User table we import the Token table 
from rest_framework.generics import ListAPIView
''')

    else:
        print('Alright then , you can add it manually to your views.py file ')



    
    auth = input('\nDo you want to secure your API ?      \t\t  ')
    print('\nNow remember if you are securing your APIs , then make sure you are importing the rest_framework & rest_framework.authtoken in your settings.py file as well \n')
    if  auth in ['yes','yup','ok','y']:
        os.chdir(f'{main_dir}\{project_name}\{project_name}')
        with open('settings.py','a+') as f:
            f.write(
'''
REST_FRAMEWORK={
'DEFAULT_AUTHENTICATION_CLASSES':[
'rest_framework.authentication.TokenAuthentication']
}
'''
)
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('views.py', 'a+') as f:
            f.write(
'''

@api_view(['POST'])                         # login portal 
def login (request):
    # if request.method == 'POST':
        data = JSONParser().parse(request)
        username =data['username']
        password = data['password']
        user = User.objects.get(username=username)
        if user.check_password(password):
            token, obj=Token.objects.get_or_create(user=user)       # if user is right , we create token by passing this user object
            print(token , obj)
            return Response({'message':f'Login successful {username} ','token':token.key})
        else:
            return Response({'message':'Login unsuccessful'})

''')
        os.chdir(f'{main_dir}\{project_name}\{project_name}')
        with open('urls.py','w') as p:
            p.write(
f'''

from django.contrib import admin
from django.urls import path,include
from rest_framework.authtoken.views import  obtain_auth_token
from {app_name}.views import login

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('',include('{app_name}.urls')),            # uncomment it accordingly
    path('api-obtain-auth/',obtain_auth_token) ,     # from here we get the token generated by the server 
    path('login/' ,login)                            # this view will be created in your views.py 
]
''')
    # os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    # table_changes()


    while 'no' not in input(' Add data sensitively Here , as this adds directly in your settings.py file , kindly confirm yes or no : '):   # until u say no , add anything in settings.py under installed apps 
        add_under_installed_apps(main_dir,project_name)  
    
 
    else:
        with open(fr'{main_dir}\{project_name}\{app_name}\urls.py','w') as f2:
            f2.write(
f'''

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/3.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('{app_name}.urls'))
]
'''     )
  

  
    view_ans = input('\nDo you want a class base view ? \n |\t yes == for class base API || no is for DRF  base API | \t ')
    if view_ans in['yes','yup','y' ,'ok']:
        class_name = input('Classname  of your view ? \t')
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('views.py', 'a+') as f:
                f.write(
f'''
class  {class_name} (APIView):                                  # CLASS BASE API       without SERIALIZERS
      #permission_classes =[IsAuthenticated]                    # IF you have authentication , uncomment it and utlize as per your requirement ! 
      def get(self,request,pk=None):
            return Response('Get called with class api True')

      def post(self,request,pk=None):
            return Response('post called with class api ')

      def put(self,request,pk=None):
            return Response('put called with class api ')

      def delete(self,request,pk=None):
            return Response('delete_message delete called with class api ')

# If you have SERIALIZERS , uncomment the following
# class ShowMoviesAPIView(ListAPIView):       #  CLASS BASE API with  SERIALIZER VIEW for ur  TABLE model  here LIST view = get api 
#         queryset = model.objects.all()
#         serializer_class = model_Serializer # remember to import your serializers as well                
#                                             # here serializer_class  is keyword , we give the class with serializer that we created in serializers



''')
    else:
        print(' Alright , using DRF based API ')
        func_name = input('Name of your function base API ?\t ')
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('views.py', 'a+') as f:
                f.write(
f'''        
@api_view(['GET','POST','DELETE','PUT'])    #   IN DRF BASE  WITH  SERAILIZERS   with token with all http methods 
# @permission_classes([IsAuthenticated])    # authentication as per requirement        
def {func_name}(request,pk=None):
    if request.method == 'GET':
        # movies = model.objects.all() #.order_by('-movie_id')         # import your models 
        return Response('Get called with class api ')

    if request.method == 'POST':                             # POST Request                             
        return Response('Post_message post called with class api ')    
    
    if request.method == 'PUT':         # PUT Request 
        return Response('Put_message put called with class api ')      
    
    if request.method == 'DELETE':         # deleTe Request 
        return Response('delete_message delete called with class api ')
''')
    

    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    table_changes()

    time.sleep(2)
    print('\nTime to add urls for your views , that you created for your app \t')
    time.sleep(2)

    tell= input('\nAre your views class base or function base ? \t')
    if view_ans in['yes','yup','y' ,'ok'] and tell in ['func','function','functionbase','function-base','function_base','()','Function','FUNCTION']:
        time.sleep(3)
        print('are you kidding me ? dont try to test this software ! just go with the flow  ')
        time.sleep(1.5)
        print('Now construct the rest manually')

        print("\U0001F606")
        exit()
    elif view_ans not in['yes','yup','y' ,'ok'] and tell in ['class','classbase','class_base','cls','class-base','c','Class','CLASS']:
        time.sleep(3)
        print('are you kidding me ? dont try to test this software ! just go with the flow  ')
        time.sleep(1.5)
        print('Now construct the rest manually')
        time.sleep(1.5)
        print("\U0001F606")
        exit()


    if tell in ['class','class-base','class_base','classbase','cls']:
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('urls.py', 'w') as f:
            f.write(
f'''
from django.urls import path
from .views import  ({class_name} )
from django.http.response import HttpResponse,JsonResponse

urlpatterns = [
    path('', {class_name}.as_view()),
    path('<int:pk>', {class_name}.as_view()),      # if you need to pass any parameter for your server 
    path('home/',lambda request:HttpResponse('Message Created By Tushar Malhan'  ) )
]
''' 
)
    else:
        # print('')
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('urls.py', 'w') as f:
            f.write(
f'''
from django.urls import path
from .views import  ({func_name} )
from django.http.response import HttpResponse,JsonResponse

urlpatterns = [
    path('', {func_name}),
    path('<int:pk>', {func_name}),                        
    path('home/',lambda request:HttpResponse('Message Created By Tushar Malhan ' ) )
    ]
'''
)  


    os.chdir(f'{main_dir}\{project_name}\{project_name}')
    with open('urls.py','w') as p:
        p.write(
f'''

#The `urlpatterns` list routes URLs to views. For more information please see:
#    https://docs.djangoproject.com/en/3.2/topics/http/urls/
#Examples:
#Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))


from django.contrib import admin
from django.urls import path,include
from rest_framework.authtoken.views import  obtain_auth_token
from {app_name}.views import login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('{app_name}.urls')),            # uncomment it accordingly
    path('api-obtain-auth/',obtain_auth_token) ,     # from here we get the token generated by the server 
    path('login/' ,login)                            # this view will be created in your views.py 
]
''')

    if auth not in ['yes','yup','ok','y']:
    
        os.chdir(f'{main_dir}\{project_name}\{project_name}')
        with open('urls.py','w') as p:
            p.write(
f'''

#The `urlpatterns` list routes URLs to views. For more information please see:
#    https://docs.djangoproject.com/en/3.2/topics/http/urls/
#Examples:
#Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))


from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('{app_name}.urls'))            # uncomment it accordingly
]
''' )





    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    table_changes()
    
    # runserver()

    model_request = input('\nDo you want to create a model for this project? \t')
    if model_request in ['yes','yup','y' ,'ok']:
        model_name = input(' model name ? \t')
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('models.py', 'w') as f:
            f.write(
f'''
from django.db import models
# from django.db.models.fields import AutoField
from django.db.models.fields import AutoField
from django.contrib.auth.models import User

class {model_name}(models.Model):
    pass
    # create your models columns accordingly

    # class Meta :
    #     verbose_name ='Give specific name for your model '
    #     ordering = [according to ur column_name]   # give column wise ordering

    # def __str__(self):
    #     return self          #return ur column here 


''')

    with open('admin.py', 'w') as f:
            f.write(
f'''
from django.contrib import admin
from .models import {model_name}

admin.site.register({model_name})
''')

    # runserver()
    
    location =0
    os.chdir(f'{main_dir}\{project_name}\{app_name}')
    with open('views.py' ) as f:
        lines_list =f.readlines()
    with open('views.py' ) as f:
        for index ,line in enumerate(lines_list):
            if line == ' ':
                location = index
    lines_list.insert(location,f'from .models import {model_name} ')
    with open('views.py','w') as r:
        r.writelines(lines_list)

    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    table_changes()

    print('Lets create a super user\n ')
    time.sleep(2)
    os.system('python manage.py createsuperuser')
    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    table_changes()

    print("\U0001f600")
    runserver()

    
