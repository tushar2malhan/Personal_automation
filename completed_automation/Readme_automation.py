''' 
    Create a README.md file for the Your PROJECTS 

# 1. need to pass project_name as an argument
# 2. Project info in detail
# 3. need to pass (args*)display as an argument     >=5   , if more show display6
# 4. need to pass (kwargs)features as an argument   >=6   , features['feature7']

Pass These Parmas: IN MAIN CLASS object
    
'''

class Main():
    def __init__(self,project_name,project_info,*display,**features):
        self.project_name = project_name
        self.project_info = project_info

        with open(r'C:\Users\Tushar\Desktop\freelancers_django\README.md','w') as f:
            f.write(
f'''
# {self.project_name}

* {self.project_info}

# Template 1
# A COMPLETE {self.project_name} WITH DJANGO FRAMEWORK
. Need to display an Image of {display[0]}
. Should be able to show {display[1]}
. Should display the {display[2]} 
. {display[3]}
. OPTIONAL: Should be able to show the {display[4]}


# Template 2

These main features have  been currently implemented.\n\
Try to Replicate them along with their functionalities:
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


project13 = Main(
# 1 Project_name
'  ',

# 2 Project_info
'This web application is a basic application which reverts your IP address and Location,  created using django. Using sqllite as database By default \
Here each user will get 4 options to change their theme and get the result. So functionalities include \n\
    * Login \n\
    * View Ip Address\n\
    * Check and Update 4 themes\
    * Tools used here are HTML, CSS, and JavaScript\n\
    * Python , DJango, and Bootstrap  to create the Application.\n',

# 3  Display
'Homepage - IP Address Page \n','Login Page \n ','4 Themes View Page \n','Personalization Page \n','Instructions of the app and images tutorial ',
# 4 Features
feature1= 'Login functionality',
feature2= 'View all the themes in the background',
feature3= 'Check and confirm Ip address',
feature4= 'Verify the Location', 
feature5= 'Registration functionality',
feature6= 'Footer Or contact Page ',

)


