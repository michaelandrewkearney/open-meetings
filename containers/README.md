# Scripting with Docker
Scripting with Docker ensures consistency across development environments. These scripts are designed not to interfere with other Docker containers running on your machine. However, if you are already running containers with the tools required for this program, default port assigment may overlap. Support for port assignment is forthcoming. In the meantime, please stop the conflicting containers or services.

## Quick Guide
Run the following commands to quickly get started:

    sh setup.sh                 # downloads images
    sh run.sh -a                # runs all images

When you pause development, stop the containers and reclaim processing power:

    sh stop.sh -a               # stops tool containers

When you wish to resume development, re-start the containers:

    sh start.sh -a              # restarts tool containers

To see the status of all containers, including those from other projects:

    docker container ls -a


## How to use these scripts
Use these scripts to setup, run, start, stop, and reset the docker containers on which the open meetings portal program depends.

Except for setup.sh, use the scripts with the tool name or the -a flag:

    sh run.sh -a                # runs all tools
    sh run.sh tika typesense    # runs just typesense and tika
    sh run.sh -h                # help page

setup.sh does not take any arguments and sets up the images for all tools by default.

## Scripts

- **setup.sh**: Downloads the appropriate docker image versions of tools.
- **run.sh**: Creates containers and runs the images in them. Starts containers by default.
- **start.sh**: Starts the docker container.
- **stop.sh**: Stops the docker container.
- **delete.sh**: Deletes docker container, including all persistent data.

WARNING: delete.sh permanently deletes all persistent data in the container, including data stored in MongoDB and data indexed into Typesense. It is designed to be used only in development and testing to delete and re-run a container to get a clean state.

## Tools

Currently, these tools are supported:
- [Apache Tika](https://tika.apache.org)
- [Typesense](https://typesense.org)
- [MongoDB Community](https://www.mongodb.com)

To add a new tool via Docker that can be used with these scripts, you must do two things:
1. Define the following variables and add them to the same index of the appropriate arrays in vars.sh:
    - tool (Descriptive name of the tool, e.g. "mongodb")
    - name (Name for the container, by convention "omp-{tool}", e.g. "omp-mongodb")
    - repo (Docker respository where the image can be obtained, e.g. "mongodb")
    - image (Name of the docker image, e.g. "mongodb-community-server")
    - tag (Tag of the docker image, e.g. "6.0-ubi8". To maintain consistency and compatability across machines, do NOT use "latest".)
    - port (Port on which to connect to the container, e.g. "27017". Many tools have default ports. You must define a port to maintain consistency across machines.)
2. Write a bash script named "run_{tool}.sh" (e.g. "run_mongodb.sh") in /containers. This script should be modelled on one of the existing scripts. It must call "docker run", preferably with the appropriate environment variables.

## Dependencies
These scripts require Docker and bash.

## Cross-Platform Compatability
To use this program on a Windows machine, you must switch your local Docker daemon to use Linux containers. This is a suggested workflow that is not guaranteed to work:
1. Navigate to C:\Program Files\Docker\Docker
2. Run "./DockerCli.exe -SwitchLinuxEngine"
3. [Run bash scripts on Windows](https://www.onlogic.com/company/io-hub/how-to-enable-bash-for-windows-10-and-11/)