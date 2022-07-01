#                                       Dockerfile for fastapi application 
# FROM python:3.8:alpine
# WORKDIR  /app
# COPY requirements.txt /app/requirements.txt
# RUN pip install --no-cache-dir -r /app/requirements.txt
# COPY  .  /app/
# CMD 'uvicorn app:app  --host=0.0.0.0 --reload'


# build successfully 

# docker build -t image_path/name .     # image created
# docker run -it -d -p host_port:container_port image_name  # execute and check

# -----------------------------------------------------------------------------------------

#                                       Dockerfile for Database + FastAPI application 
FROM python:3.8:alpine
WORKDIR  /app

# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1
# ensures that the python output is sent straight to terminal (e.g. your container log)
# without being first buffered and that you can see the output of your application (e.g. django logs)
# in real time. Equivalent to python -u: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV TESTING 0

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY  .  /app/
CMD 'uvicorn app:app  --host=0.0.0.0   --reload'

