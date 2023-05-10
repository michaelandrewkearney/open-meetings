#!/bin/bash
port=$1

echo STARTING TYPESENSE ON PORT $port
sleep 3;

containerExists= $(docker container ls -a | grep opm-test)

if [ -z "$output" ]; then
	echo "opm-test container not found, creating and starting..."
else
	echo "opm-test container found, removing and recreating"
	docker container rm opm-test
fi

api_key=${TYPESENSE_API_KEY}

docker run  --name opm-test -p $port:$port -v typesense-test-db:/data typesense/typesense:0.24.1 \
  --data-dir /data --api-key=${api_key} --enable-cors --api-port=$port