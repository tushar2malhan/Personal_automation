class Main():
    def __init__(self,project_name,project_info,*display,**features):
        self.project_name = project_name
        self.project_info = project_info

        with open('Readme.md','w') as f:
            f.write(
f'''
# {self.project_name}

* {self.project_info}

# Template 1
# A COMPLETE {self.project_name} WITH DJANGO FRAMEWORK
. Need to display an Image of {display[0]}
. Should be able to {display[1]}
. Should display the {display[2]} 
. {display[3]}
. OPTIONAL: Should be able to {display[4]}


# Template 2

These main features have  been currently implemented.\n\
Try to Replicate them along with their funcaionalities:
Features:
    []: # {features['feature1']}
    []: # {features['feature2']}
    []: # {features['feature3']}
    []: # {features['feature4']}
    []: # {features['feature5']}
    []: # {features['feature6']}

# MAKE SURE YOU HAVE DJANGO INSTALLED
# INSTALL DJANGO
    

# Create a new project
    
    []: # python manage.py startproject project_name

# Create a new App
        
    []: # python manage.py startapp app_name

# Run the server

    []: # Language: python,bash
    []: # Path: cd /project_name/app
    []: # python manage.py runserver

# Template 3
# You need to create a superuser to add the Main User to the database
# Create a superuser
    
    []: # python manage.py createsuperuser
    []: # http://127.0.0.1:8000/admin - Sign in with the username and password you created
    []: # Click on login to check the Models and User created.
    []: # Click on the User and check the User created.


Its upon Your imagination How you wanna design it!

## Dependencies
#### Python, Django

## run 

```
pip install -r requirements.txt
python manage.py test # Run the standard tests. These should all pass.
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
* Open `http://127.0.0.1:8000` to see the main site.
* [ Hint :] If Facing issue Check your project url and app url and make sure they are correct.

Look at the screenshots Dir for more information.

'''
        )
# 1. need to pass project_name as an argument
# 2. Project info in detail
# 3. need to pass (args*)display as an argument     >=5   , if more show display6
# 4. need to pass (kwargs)features as an argument   >=6   , features['feature7']
project13 = Main('',
'This web application creates an , where users can \n\
    * \n\
    * \n\
    * ',
'','','','','',
feature1= ' ',
feature2= ' ',
feature3= ' ',
feature4= ' ',
feature5= ' ',
feature6= ' '

)