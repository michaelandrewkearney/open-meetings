#!/bin/bash

output=$(docker images | grep "53d71694cf5a")

if [ -z "$output" ]; then
	echo typesense image typesense/typesense:0.24.1 not found, pulling
	docker login
	docker pull typesense/typesense:0.24.1
	echo typesense docker image downloaded succesfully
else
	echo ${output}
	echo "typesense found"
fi