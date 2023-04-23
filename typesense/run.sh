#!/bin/bash

export TYPESENSE_API_KEY=xyz

mkdir $(pwd)/typesense-data

echo STARTING TYPESENSE ON PORT 8108
sleep 3;

docker run -p 8108:8108 -v $(pwd)/typesense-data:/data typesense/typesense:0.24.1 \
  --data-dir /data --api-key=$TYPESENSE_API_KEY --enable-cors
