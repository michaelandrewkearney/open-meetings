#!/bin/bash

output=$(docker images | grep typesense)

if [ -z "$output" ]; then
	echo typesense image not found, pulling
else
	echo ${output}
	echo typesense found, no setup needed :\)
fi
