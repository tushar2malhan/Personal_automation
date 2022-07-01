##  Connect Database running on Docker with FastAPI application <br />
<br />
- Install docker   <br />
<br />

##   Create the Container and execute it <br />
- `docker run --name [container_name] -e POSTGRES_PASSWORD=[your_password] -d postgres`  <br />
- `docker exec -it [container_name] psql -U [postgres_user]` <br />


##   Commands to run in postgres shell  in docker <br />
- `create database fastapi_database;`  <br />
- `create user tushar with encrypted password 'password';`  <br />
- `grant all privileges on database fastapi_database to tushar;`  <br />
- `psql -h localhost -p 5432 postgres`  <br />
[*] If your setting your own user and password, make sure you change the configurations in database.py file too <br />


##  Create your fastAPI application and run it <br />
- `pip install -r requirements.txt` <br />
- find location of the app in the terminal <br />
- `uvicorn app:app --reload` <br />
- Go to url -> http://127.0.0.1:8000/docs <br />


## If issue persists for Reconnection, try to restart the container or 
use this run command ->  `docker run --rm -P --publish 127.0.0.1:5432:5432 --name [container_name] -e POSTGRES_PASSWORD=password -d postgres` <br />


