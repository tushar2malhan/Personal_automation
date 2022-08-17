
# Django - Docker - Postgres Microservice

* This web application creates CRUD application hosted on DOCKER with postgreSQL as DATABASE in an App where users can 
    * add Tasks 
    * delete,update,modify Tasks
    * Tools used here are HTML, CSS, Django, Docker, PostgreSQL
    * Python , DJango, and Bootstrap  to create the Application.
    * [optinal] Here user can filter out the Tasks based on the category



# Template 1
# SETUP 
    * Dockerfile            ->    Instructions layed out
    * docker-compose.yaml   ->    For PostgreSQL service compatible with our Dockerfile


# Template 2
* A COMPLETE App WITH DJANGO FRAMEWORK
    * Able to show all the Tasks 
    * Displaying the Updated Tasks  with striked out text 
    * These main features have  been currently implemented
    Try to Replicate them along with their functionalities:
    Features:
        []:  View The tasks
        []:  Add the Tasks
        []:  Submit results and view the Results pages
        []:  Modify Tasks




* Template 3
- You need to create a superuser to add the Main User to the database | Create a superuser
    
    * []:  python manage.py createsuperuser
    * []:  http://127.0.0.1:8000/admin - Sign in with the username and password you created
    * []:  Click on login to check the Models and User created.
    * []:  Click on the User and check the User created.

# MAKE SURE YOU HAVE DJANGO AND DOCKER INSTALLED
 * If on Windows, Make sure your docker desktop is running.
 * If on Mac, Make sure you have docker-machine installed.
 * If on Linux, Make sure you have docker-compose installed.


# INSTRUCTIONS 
```
    []:  cd djang-doc                         ->  ( Dockerfile and docker-compose.yaml are in the same path )
    []:  docker compose up                   ->   Boot up the Containers 
    []:  docker compose -p djang-doc up       -> Tag your containers | If name given Specify each command with name |  docker compose -p djang-doc up, restart ...
    []:  docker compose ps                   ->   Check the running the containers 
    []:  docker compose restart              ->   Restart the Exited containers 
    []:  Ctrl + C                            ->   stop and exit from containers
    []:  docker-compose down                 ->   Remove the containers
    []:  docker-compose rm -f                ->   Remove the containers
    []:  Remove everything from scratch      ->  docker system prune -a -f && docker system df && docker builder prune -f && docker volume prune -f
```

*  Create and start the Container 
`docker run -it <image_name> bash`

* SSH into the Running container - Docker Db > to execute the SQL queries 
- docker exec -it container_name /bin/bash
` docker exec -it djang-doc-db-1 bash `    
` psql -U postgres `
` \dt  `                         > Find the table 
`select * from tasks_task; `     > Execute the command 
` \q `                           > Exit from the container
</br>
</br>
</br>

*   Access Docker Postgres Container to view the results 
` docker run -d -p 5432:5432 --name <db_container_name> -e POSTGRES_PASSWORD=mysecretpassword -U postgres  <db_image_name> `

* Access The Non Existent Container from the image  in bash terminal 
`docker run --rm -it --entrypoint bash <image_name>`


* PROJECT/settings.py  | Database Configuration |
```
 DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'password for postgres',
        'HOST': 'db',               # For docker container
        # 'HOST': '127.0.0.1',      # For postgres connectivity
        'PORT': '5432',
    }
}
                   # For local host
DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.sqlite3',
         'NAME': BASE_DIR / 'db.sqlite3',
     }
 }
```
* Open `http://127.0.0.1:8000` to see the main site.

# Issues:

*  Suppose db is connected but table throwing error where it does not exist in db in django ! 
` docker exec -it django-doc-web-1 bash `
#   Execute these commands inside the Docker WEB Container 
```
  python manage.py migrate --run-syncdb
  python manage.py makemigrations appname
  python manage.py migrate --fake appname
```

* [ Hint :] If Facing issue Check your project url and app url and make sure they are correct.
* [If Issue Persists ->  try running `localhost:8000` or `http://127.0.0.1:8000` in New Incognito Tab ]

# Create a new project
    
    []:  python manage.py startproject project_name

# Create a new App
        
    []:  python manage.py startapp app_name

# Run the server

    []:  Language: python,bash
    []:  Path: cd /project_name/app
    []:  python manage.py runserver

## Dependencies
#### Python, Django, Docker, PostgreSQL

## run 

```
pip install -r requirements.txt
python manage.py test # Run the standard tests. These should all pass.
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```


