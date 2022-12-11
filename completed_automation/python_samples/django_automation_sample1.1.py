'''
    Description     : Django Automation Tool with frontend and backend options
    Author          :                Tushar Malhan
    Requirements    : Provide Path to main_dir and check_packages
    Status          : Completed

'''

import os
import sys
import time


main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


check_packages = os.listdir([i for i in sys.path if  i.endswith('site-packages')][0])  # print(sys.path)  # Check your python path and do changes accordingly in check_packages

confirmation =  ['yes','yup','y' ,'ok']


def add_under_installed_apps(main_dir,project_name,app_name,word=None):
      
        with open(fr'{main_dir}\{project_name}\{project_name}\settings.py') as f1:
            lines = f1.readlines()
        with open(fr'{main_dir}\{project_name}\{project_name}\settings.py','w') as f:
            if word:
                for line in lines:
                        if 'django.contrib.staticfiles' in line:
                            line += f"\t'{app_name}' ,\n\t'rest_framework',\n\t'rest_framework.authtoken', \n\t'{word }',\n"
                        f.write(line)
            for line in lines:
                    if 'django.contrib.staticfiles' in line:
                        line += f"\t'{app_name}' ,\n\t'rest_framework',\n\t'rest_framework.authtoken', \n"
                    f.write(line)     
        time.sleep(1)
        print('\n\t[*] Done Added your changes in your settings.py file ')
        time.sleep(1)


def table_changes():
    os.system('python manage.py makemigrations')
    os.system('python manage.py migrate')


def runserver():
    os.system('python manage.py runserver')


def listdir_in_ur_home():
    return os.listdir(main_dir)      


def chdir_to_home():
    '''
    This Dir holds your
     project and app ''' 
    os.chdir(main_dir)       
  

def check_requirements(check_packages):
    ''' Checks for 'virtualenv',
    'django','rest_framework  packages
     installed or not ! '''
    global confirm_the_packages
    confirm_the_packages = None

    for package in check_packages:
        if package in ('django','rest_framework','virtualenv','crispy-forms'):
            confirm_the_packages = True
        
     

project_initialization  = input('\n[*]\tCreate Django from scrath \n\n\t').lower().strip()
if project_initialization in ['django' , 'go','','l','ok','yes']:

    chdir_to_home()    

    check_requirements(check_packages)
    
    if confirm_the_packages:          
        
        print('\t[*]\tAll Main Packages are installed')
        print('\t[*]\tHope your virtualenv is not running in any other thread\n')  
        
     
    else:
        os.system('pip install virtualenv && virtualenv env && env\Scripts\activate')
        print('\t[*]\tInstalling the workload')
        os.system(f'pip install django && pip install djangorestframework\
        && pip install django-crispy-forms && pip install django-ckeditor')
    
    project_name = input('\n[*]\tProject name ? \t')

    if project_name in ['None',None,'',0,'empty']:
        print('\t[*]\t Your Project should have a valid Name ')
        exit()


    if project_name in listdir_in_ur_home():
        time.sleep(0.5)
        print('\n\t[*]\tProject with that initials already present !')
        print('\t[*]\tKindly change your project name and try again !\n ')
        exit()
    else:
        if not os.path.exists(main_dir+"\\"+project_name):
            os.mkdir(main_dir+"\\"+project_name)
            print(f'\t[*]\tDirectory  named {project_name} created')
        os.system(f'django-admin startproject {project_name}')
        print(f'\n\t[*]\tCreated new project named "{project_name}" in {os.getcwd()} Directory \n') 
    time.sleep(1)
    

    app_name = input('\n[*]\tApp name ? \t ')
    (print('\n\t[*]\tYour App should have a valid name'),exit()) \
    if app_name.lower().strip() in ['none',None,0,'','empty']\
    or app_name.lower().strip() == project_name.lower().strip()\
    else print('\n\t[*]\tGood to go\n')

    os.chdir(f'{main_dir}\{project_name}')    #  we put the app under project directory
    if app_name in main_dir+"\\"+project_name:
        time.sleep(2)
        print(f'\n\t[*]\t{app_name}  Your app present with that initials \n ')
    else:
        time.sleep(2)
        os.system(f'django-admin startapp {app_name}')
        print(f'\t[*]\tYour app also created in {os.getcwd()}')
    
    if project_name == app_name:
        print('You cant have same initials for your project and app , kindly change it ')
        exit()
    else:
        print(f'\n\t[*]\tYour Project named "{project_name}" and App named "{app_name}" are ready now!  \n')

    
    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 

    time.sleep(1)
    table_changes()
    # runserver()

    db = input('\n[*] Wanna install  postgres database ? \t ')
    if 'yes' in db:
        time.sleep(1)
        if 'psycopg2' not in check_packages:
            os.system('pip install psycopg2')
        else:
            print('Postgres module Already installed ')
        enter = input('wanna go inside and start ? ')
        if 'yes' in enter:
                os.chdir(r'C:\Program Files\PostgreSQL\14\bin')                 # if u wanna enter shell directly kindly set ur path of Postgress/bin
                time.sleep(1)
                print('kindly provide credentials for your postgres database ')
                time.sleep(1)
                os.system('psql -U postgres -h localhost')
                time.sleep(1.5)
                exit = input('done changes ? wanna exit ')
                if 'yes' in exit:
                    os.system('exit()')
                else:
                    os.system('psql -U postgres -h localhost')
    else:
        print('\n\t[*]\t pip install psycopg2   -- installation guide for postgres\n')
    
    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    table_changes()

    postgres_configuration = input('\n[*] Wanna configure postgres database ? \t ')
    if postgres_configuration in confirmation:
        os.chdir(f'{main_dir}\{project_name}\{project_name}')
        with open('settings.py','a+') as f:
            f.write(
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'admin',
         # 'HOST': 'db',          # for docker container
        'HOST': '127.0.0.1',      # for postgres connectivity
        'PORT': '5432',
     }
}
'''
)
    else:
        print('\n\t[*]\tOk then , using the DB Sql-lite  By default')
  

    ask = input('\n[*] Wanna add rest_framework modules in ur views  ?\t ').strip().lower()
    if ask in ['yes','yup','y' ,'ok','yes ',' yes']:
        with open(fr'{main_dir}\{project_name}\{app_name}\views.py','w') as f2:
            f2.write(
'''
# Imported almost everything , create your view accordingly , if anything missed kindly add it manually

import json
from django.shortcuts import render
from django.http import HttpResponse , JsonResponse
from requests import api

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User          # get all the users  in ur account 
from django.contrib import messages
from django.views.generic import ListView
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token             # just like User table we import the Token table 
from rest_framework. parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
''')

    else:
        with open(fr'{main_dir}\{project_name}\{app_name}\views.py','w') as f2:
            f2.write(
'''
# Imported almost everything , create your view accordingly , if anything missed kindly add it manually

import json
from django.shortcuts import render, redirect
from django.http import HttpResponse , JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User          # get all the users  in ur account 
from django.contrib import messages

from django.views.generic import View
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token             # just like User table we import the Token table 
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
''')

    print("\n\t[*]\tYour App's name, rest_framework and rest_framework.authtoken has been Successfully installed under INSTALLED_APPS  !")
    time.sleep(1)
    word = input('\n[*] What else needs to be  installed under installed apps  ? - [!] Press Enter [!] \t if nothing to add \n')
    add_under_installed_apps(main_dir,project_name,app_name,word)  if word else add_under_installed_apps(main_dir,project_name,app_name)

    #       until u say no , add anything in settings.py under installed apps 
    #       print('\nNow remember if you are securing your APIs , then make sure you are importing the rest_framework & rest_framework.authtoken in your settings.py file as well \n')
    #       if word:
    #            while 'no' not in input(' Add data sensitively Here , as this adds directly in your settings.py file , kindly confirm yes or no : '):   
    #            add_under_installed_apps(main_dir,project_name,app_name)  
        
    
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
    """
    Step 1 > POST http://127.0.0.1:8000/login/  in json body , send username and password {"username": "tushar", "password": "test@123"}
                and get a token in response  {"message": "Login successful tushar ", "token": "e8e93f7a21a4e45c67527d644a69e3e4fc296721"}
    Step 2 > GET  http://127.0.0.1:8000/      call the views function and pass the token in header as Authorization : Token <token>

    Now  when u login with user who has been added by superuser, his token can be generated in 3 ways 
    | now wherever IsAuthenticated class is used ,
    | u can use token authentication which can be generated by auth token  by this function login
    | IF You are in thunder client >  go to bearer > token prefix = Token > Bearer token = token 
    | and now hit the request , it will work 

        Second way to login > http://127.0.0.1:8000/api-obtain-auth/  in json body , send username and password {"username": "vitor", "password": "test@123"}
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        username =data['username']
        password = data['password']
        user = User.objects.get(username=username)
        if user.check_password(password):
            token, obj=Token.objects.get_or_create(user=user)       
            print(token , obj)
            messages.success(request, f'Your Account has been Successfully created !')
            return Response({'message':f'Login successful {username} ','token':token.key})
        else:
            return Response({'message':'Login unsuccessful'})

''')
    
    print('\t[*] Added Rest-framework Basic authentication in your settings.py file')
    print('\t[*] Added a login functionality in your views.py file with the path in urls.py  file too\n')

    os.chdir(f'{main_dir}\{project_name}\{project_name}')    
    with open(fr'{main_dir}\{project_name}\{project_name}\urls.py','w') as p:
        p.write(
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
from django.urls import path,include
from rest_framework.authtoken.views import  obtain_auth_token
from {app_name}.views import login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('{app_name}.urls')),             # uncomment it accordingly
    path('api-obtain-auth/',obtain_auth_token) ,     # from here we get the token generated by the server 
    path('login/' ,login)                            # this view will be created in your views.py 
]
''')
     
    with open(fr'{main_dir}\{project_name}\{app_name}\urls.py','w') as f2:
        f2.write(
f'''

#               IGNORE 
# this is the previous version of urls.py file which 
# had to be updated in projects/settings.py file 
# but  now i'll update it in a moment 

# from django.contrib import admin
# from django.urls import path
# from django.urls.conf import include

# urlpatterns = [
   # # path('_admin_/', admin.site.urls),
   # # path('',include('{app_name}.urls'))
# ]
'''     )
  

  
    view_ans = input('\n[*] Do you want a class base view ? \n\n\t[*]\t| yes == for class base API || no is for DRF  base API | \t ')
    if view_ans in confirmation:
        class_name = input('\n\t[*]\tClassname  of your view ? \t')
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('views.py', 'a+') as f:
                f.write(
f'''
class  {class_name} (APIView):                                  # CLASS BASE API       without SERIALIZERS
      # permission_classes =[IsAuthenticated]                    # IF you have authentication , uncomment it and utlize as per your requirement ! 
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
        print('\n\t[*]\tAlright , using DRF based API ')
        func_name = input('\n\t[*] Name of your function base API ?\t ')
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

    time.sleep(2)
    print('\n\t[*]\tTime to add urls for your views , that you created for your app \t')
    time.sleep(2)

    tell = input('\n[*] Are your views class base or function base ? \t')
    print('\n')
    
    if view_ans in confirmation and tell in ['func','function','functionbase','function-base','function_base','()','Function','FUNCTION']:
        time.sleep(3)
        print('\n\t[*]\tYou have given an incorrect input, Its CLASS Base ')
        time.sleep(1.5)

        print("\U0001F606")


    elif view_ans not in confirmation  and tell in ['class','classbase','class_base','cls','class-base','c','Class','CLASS']:
        time.sleep(3)
        print('\n\t[*]\tYou have given an incorrect input, Its FUNCTION Base ')
        time.sleep(1.5)
        print("\U0001F606")
    


    if view_ans in  confirmation :
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('urls.py', 'w') as f:
            f.write(
f'''
from django.urls import path
# from .views import  ({class_name} )
from .views import  *
from django.http.response import HttpResponse,JsonResponse

urlpatterns = [
    path('', {class_name}.as_view()),
    path('<int:pk>', {class_name}.as_view()),      # if you need to pass any parameter for your server 
    path('home/',lambda request:HttpResponse('Message Created By Tushar Malhan'  ) )
]
''' 
)
    else:
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('urls.py', 'w') as f:
            f.write(
f'''
from django.urls import path
# from .views import  ({func_name} )
from .views import  *
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


    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    table_changes()
    
    # runserver()

    print('\n\t[*]\tTime to add forms and fields to your views , that you created for your app \t')
    front_end_input = input('\n[*] Do you want to create a front end for your app ? \t')
    if front_end_input in confirmation:
        templates_path = fr'{main_dir}\{project_name}\{app_name}\templates'
        if not os.path.exists(templates_path):
            os.mkdir(templates_path)
        os.chdir(templates_path)
        with open('header.html', 'w') as f:
            f.write(
"""
<div class="collapse navbar-collapse" id="navbarNavAltMarkup">
    <div class="navbar-nav">
      <a class="nav-link active" aria-current="page" href="#">Home</a> 
      <!-- <a class="nav-link" href="#">Market</a>
      <a class="nav-link" href="#">Company</a>
      <a class="nav-link" href="#">Education</a>
      <a class="nav-link" href="#">Resouces</a> -->

    </div>
    <form class="d-flex" id="authstyle">

      <a class="nav-link" href="#">NAV 1</a>
      <a class="nav-link" href="#">NAV 2 </a>
      <a class="nav-link" href="#">NAV 3 </a>
      
      </form>
  </div>

</div>
"""
)
        with open('base.html', 'w') as f:
            f.write(
'''
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!--Css Style -->
    <link rel="stylesheet">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6" crossorigin="anonymous">
    <!--Font Link-->
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500&family=Open+Sans:wght@800&display=swap" rel="stylesheet">
    
</head>
<body>
{% load static %}
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark" id="main-navbar">
        <div class="container">
          <a class="navbar-brand" href="#"></a>     
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
        
          {% include 'header.html' %}
          
        </div>
    </nav>

     <div class="container">
        <div>
          {% if messages %}
          {% for message in messages %}
            <div class="alert alert-{{message.tags}}">{{message}}</div>
          {% endfor %}
        {% endif %}
        </div>
        <div>
          {% block content %}
          {% endblock content %}
          </div>
      </div>

      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.bundle.min.js" integrity="sha384-JEW9xMcG8R+pH31jmWH6WWP0WintQrMb4s7ZOdauHnUtxwoG2vI5DkLtS3qm9Ekf" crossorigin="anonymous"></script>

    
</body>
</html>
'''
)
        with open('home.html', 'w') as f:
            f.write(
'''
{% extends 'base.html' %}
{% load static %}
{% block content %}

  <link rel="stylesheet" >
  <div>
    <h1>Home Page</h1>

    <p> Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quisquam, quos, quisquam. </p>
  </div>
{% endblock content %}


'''
)
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('forms.py', 'w') as f:
            f.write(
'''
from django import forms
from django.forms import  Textarea
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField( required=True )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        """ Email needs to be unique """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(' This Email already exists')
        return email

'''
        )
        with open('urls.py',) as f:
            lines_list = f.readlines()
        with open('urls.py','w') as f:
            for index ,line in enumerate(lines_list):
                location = index - 1
            lines_list.insert(location,f'\tpath("index/", index), \n')
            f.writelines(lines_list)
    
    else:
        print('\n\t[*]Sure, Its confirmed it is a Backend Application')

    model_request = input('\n[*] Do you want to create a model for this project ? \t')
    
    if model_request in  confirmation :
        model_name = input('\n\t[*]\tModel Name ? \t')
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('models.py', 'w') as f:
            f.write(
f'''
from django.db import models
from django.contrib.auth.models import User

class {model_name}(models.Model):
   
    """
    # id  column is always autogenerated by django 
    # create your models columns accordingly
    """

    text = models.TextField( null=True, default='Default text')
    
    class Meta :
        verbose_name_plural =  "{model_name}"    
        ordering = ['id']                      #  'Given column ID wise ordering'

    def __str__(self):
        return str(self.id)                    #  'Cant return int or None here else error'


''')

        with open('admin.py', 'w') as f:
                f.write(
f'''
from django.contrib import admin
from .models import {model_name}

admin.site.register({model_name})
''')
    
        location = 0
        os.chdir(f'{main_dir}\{project_name}\{app_name}')
        with open('views.py' ) as f:
            lines_list = f.readlines()
        with open('views.py' ) as f:
            for index ,line in enumerate(lines_list):
                if line == ' ':
                    location = index
        lines_list.insert(location,f'\nfrom .models import {model_name} ')
        lines_list.insert(location,f'\nfrom .forms import UserRegisterForm ') if front_end_input in confirmation else None
        with open('views.py','w') as r:
            r.writelines(lines_list)

    else:
        print('Sure Skipping the Model step')

    os.chdir(f'{main_dir}\{project_name}\{app_name}')
    with open('views.py', 'a') as f:
            f.writelines(
f'''
def index(request):
    """ Rendering the home page """
    # model_object = {model_name}.objects.all()
    # context = data : models_object > return render(request, 'home.html', context )
    return render(request,'home.html')
'''
    )
    

    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    table_changes()

    print('Lets create a super user\n ')
    time.sleep(2)
    os.system('python manage.py createsuperuser --username tushar --email tushar@gmail.com ' )
    os.chdir(f'{main_dir}\{project_name}')         # Inside our Project folder , can make changes using manage.py file 
    table_changes()

    print("\U0001f600")
    runserver()

    
