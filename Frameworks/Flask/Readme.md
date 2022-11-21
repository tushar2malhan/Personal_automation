# Load Balanced Flask Applications  with Nginx Server using Docker Compose using round robin Fashion

- [Flask Applications Load Balanced with Nginx Server](#flask-applications-load-balanced-with-nginx-server)
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Step 1: Install Nginx](#step-1-install-nginx)
  - [Step 2: Install Flask](#step-2-install-flask)
  - [Step 3: Create Flask Application](#step-3-create-flask-application)
  - [Step 4: Create Nginx Configuration File](#step-4-create-nginx-configuration-file)
  - [Step 5: Start Nginx and Flask Applications](#step-5-start-nginx-and-flask-applications)
  - [Step 6: Test Load Balancing](#step-6-test-load-balancing)
  - [Conclusion](#conclusion)

## Introduction

In this tutorial, we will learn how to load balance multiple Flask applications using Nginx server. We will use Docker Compose to run multiple Flask applications and Nginx server.

## Prerequisites

To follow along with this tutorial, you will need:

- Docker installed on your machine. Follow the [official Docker documentation](https://docs.docker.com/get-docker/) to install Docker on your machine.

- Basic knowledge of Docker Compose.

## Step 1: Install Nginx or Create Dockerfile

We will use the official Nginx Docker image to run Nginx server. To pull the image, run the following command:

```bash
docker pull nginx
```

- Create Nginx Configuration File

Create a file named `nginx.conf` with a Dockerfile in the root directory

- If error persists like :=
```bash
nginx: [emerg] "upstream" directive is not allowed here in /etc/nginx/nginx.conf:1
```
- make sure your conf file structure should look like this  - Upstream and server should be inside http block

```bash

    http {
        
        upstream loadbalancer {
            server 172.17.0.1:5001 weight=6;
            server 172.17.0.1:5002 weight=4;
            }
            
        server {
            location / {
            proxy_pass http://loadbalancer;
            }
        }

    }

    events {
        worker_connections  1000;
    }
```


## Step 2: Create Flask Application

We will create two Flask applications. Each application will have a single route that returns a message.

Create a directory and create two subdirectories `app1` and `app2` in it. Create a file named `app.py` in both directories 


## Step 3: Create Dockerfile for both flask apps
- check flask app directory structure
```bash
├── app1
│   ├── app.py
│   └── Dockerfile
├── app2
│   ├── app.py
│   └── Dockerfile
└── nginx.conf
```


## Step 4: Create Docker Compose File
- Make it accessible from root directory
- check docker-compose.yml file structure
```bash
├── app1
│   ├── app.py
│   └── Dockerfile
├── app2
│   ├── app.py
│   └── Dockerfile
├── nginx
│   └── Dockerfile
│   ├── nginx.conf
└── docker-compose.yml
```

## Step 5: Start Nginx and Flask Applications using docker-compose command assigned with project named as "flask"

```bash
docker compose -p flask up
```

- Nginx Application will be running on port 8080 and Flask applications will be running on port 5001 and 5002.
`http://localhost:8080/`    - Nginx
`http://localhost:5001/`    - Flask App 1
`http://localhost:5002/`    - Flask App 2


## Step 6: Test Load Balancing

To test load balancing, we will send multiple requests to the Nginx server. Run the following command to send 100 requests to the Nginx server:

```bash
for i in {1..100}; do curl http://localhost; done
```

You should see the following output:

```bash
This is First Flask Application 
This is the second Flask Application
```

## Step 7: Scale Flask Applications

To scale Flask applications, run the following command:

```bash
docker compose -p flask up --build --scale app1=3 --scale app2=2
```

- nginx.conf file structure
```bash
    http {
    
    events { worker_connections 1024; }
    upstream localhost {
        # These are references to our backend containers, facilitated by
        # Compose, as defined in docker-compose.yml   
        server backend1:3000;
        server backend2:3000;
        server backend3:3000;
    }
    server {
        listen 8080;
        server_name localhost;
        location / {
        proxy_pass http://localhost;
        proxy_set_header Host $host;
        }
    }
    }
```

##  Reload Nginx configuration to reload changes in yaml file
```
   docker exec -it flask-nginx-1 nginx -s reload
```

# Make sure you only open container port only as it will automatically map host port to container port otherwise it will throw error becuase of port conflict 

- check port structure in docker compose file
```bash
├── app1
    ports:
      - "5001:5000"
      - "5001"       # if scaling containers is needed
├── app2
    ports:
      - "5002:5000"
      - "5002"       # if scaling containers is needed
```
This will scale the Flask applications to 3 and 2 respectively. 

```bash

## Conclusion

In this tutorial, we learned how to load balance multiple Flask applications using Nginx server. We used Docker Compose to run multiple Flask applications and Nginx server.
