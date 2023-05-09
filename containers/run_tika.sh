#!/bin/bash

tool_to_get="tika"

source "$(dirname $0)"/vars.sh

index=$(get_tool_index $tool_to_get)

TOOL=${tools[index]}
NAME=${names[index]}
REPO=${repos[index]}
IMAGE=${images[index]}
TAG=${tags[index]}
PORT=${ports[index]}

DIR=$(dirname $0)

echo Starting $TOOL container on port $PORT...

docker run --name $NAME -d -p 127.0.0.1:$PORT:$PORT -v$(pwd)/$DIR/tika-config.xml:/tika-config.xml $REPO/$IMAGE:$TAG --config /tika-config.xml