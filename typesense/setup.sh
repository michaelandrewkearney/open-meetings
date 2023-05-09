#!/bin/bash

output=$(docker images)

if ! grep -q 'REPOSITORY' <<< "$output"; then
	echo Result of docker images was not recognized. This program requires the docker engine to run. Please install a current version from docs.docker.com/engine/install or use homebrew:
	echo "    brew install --cask docker"
	exit
fi

# Tika Image
if ! grep -q 'apache/tika' <<< "$output"; then
	echo Pulling Tika image from dockerhub...
	docker pull apache/tika
else
	echo Tika image is already pulled.
fi

# Mongo Image
if ! grep -q 'mongodb/mongodb-community-server' <<< "$output"; then
	echo Pulling MongoDB image from dockerhub...
	docker pull mongodb/mongodb-community-server
else
	echo MongoDB image is already pulled.
fi

# Typesense Image
# docker pull typesense/typesense results in an error. Specifying a tag fixes the issue but 
if ! grep -q 'typesense/typesense' <<< "$output"; then
	echo Pulling Typesense image from dockerhub...
	docker pull typesense/typesense:0.25.0.rc25
else
	echo Typesense image is already pulled.
fi

echo If no errors occured, setup is complete.
