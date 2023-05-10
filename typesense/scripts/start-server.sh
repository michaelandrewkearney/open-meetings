#!/bin/bash

exit()

port=$1

mkdir $(pwd)/typesense-database

echo STARTING TYPESENSE ON PORT $port
sleep 3;

api_key=${TYPESENSE_API_KEY}

docker rm opm

docker run  --name opm -p $port:$port -v $(pwd)/typesense-database:/data typesense/typesense:0.24.1 \
  --data-dir /data --api-key=${api_key} --enable-cors --api-port=${port}