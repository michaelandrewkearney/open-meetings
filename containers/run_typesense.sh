#!/bin/bash

tool_to_get="typesense"

source "$(dirname $0)"/vars.sh

index=$(get_tool_index $tool_to_get)

TOOL=${tools[index]}
NAME=${names[index]}
REPO=${repos[index]}
IMAGE=${images[index]}
TAG=${tags[index]}
PORT=${ports[index]}

export TYPESENSE_API_KEY=xyz

DIR=$(dirname $0)/typesense
DATA_DIR=data
LOGS_DIR=logs

mkdir -p $DIR/$DATA_DIR
mkdir -p $DIR/$LOG_DIR

INTERNAL_DIR="ts"

echo Starting $TOOL container on port $PORT...

docker run --name $NAME -p 127.0.0.1:$PORT:$PORT -v$(pwd)/$DIR:/$INTERNAL_DIR $REPO/$IMAGE:$TAG --data-dir=/$INTERNAL_DIR/$DATA_DIR --api-key=$TYPESENSE_API_KEY --enable-cors --log-dir=/$INTERNAL_DIR/$LOGS_DIR