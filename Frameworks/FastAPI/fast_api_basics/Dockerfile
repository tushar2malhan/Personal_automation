FROM python:3.8

# set env variables
# ENV DATABASE_URL = "postgres://postgres:postgres@postgres:5432/postgres"
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY /app/requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--reload"]

# EXPOSE 8000

# CMD ["uvicorn", "app.main:app", "--host=0.0.0.0"]


# Create an image                              ->   docker build -t fast_api . 


# Port has been exposed > run the container    ->   docker run --name fastapi_container -p 8000:8000 fast_api
# your application is running on port 8000     ->   http://localhost:8000/docs

#  Remove everything                           ->   docker system prune -a -f && docker system df && docker system prune -a -f && docker builder prune -f

# wanna go inside the shell Direcly     ? (  docker run -it --name fastapi_container fast_api bash  )
# Get access to the running container   ? (  docker exec -it container /bin/bash   )

# restart the exited containers WEB     ? (  docker run --name container -p 8000:8000 project_web:latest )
# Restart the exited  containers        >>>     docker compose up    |   docker compose -p <name> up
