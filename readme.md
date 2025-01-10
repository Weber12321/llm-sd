# Lab

This is a repository for setting up the demosite using streamlit including prompt lab and any gen project.   


## Pre-requirement
+ docker and docker compose v2

## Usage

+ Clone the project: 
```bash
$ git clone https://github.com/Weber12321/llm-sd.git
```

+ Change directory into the repository and setting up the required environment settings, run the command below:
```bash
$ cd llm-sd
$ cp docker-vars.env.example docker-var.env
$ cp .env.example .env
```

+ build images
```bash
$ DOCKER_BUILDKIT=1 docker build -f docker/Dockerfile.lab -t llm/demo:lab-develop .
$ DOCKER_BUILDKIT=1 docker build -f docker/Dockerfile.server -t llm/demo:vllm-server .
```

+ Start up the demosite service:
```bash
$ docker compose up
```

## Structuredetails.
![alt text](docs/structure.png)
![alt text](docs/abstract.png)
