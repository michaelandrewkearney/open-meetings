#!/bin/bash

source "$(dirname $0)"/vars.sh

output=$(docker images)

if ! grep -q 'REPOSITORY' <<< "$output"; then
	echo Result of docker images was not recognized. This program requires the docker engine to run. Please install a current version from docs.docker.com/engine/install or use homebrew:
	echo "    brew install --cask docker"
	exit
fi

for i in "${!tools[@]}"; do
    if ! grep -q "${repos[$i]}/${images[$i]}\s*${tags[$i]//./\\.}" <<< "$output"; then
        if [[ -n "${build[$i]}" ]]; then
            echo Building "${images[$i]}" image from local Dockerfile...
            eval ${build[$i]}
        else
            echo Pulling "${images[$i]}" image from dockerhub...
            docker pull --platform=linux/arm64 ${repos[$i]}/${images[$i]}:${tags[$i]}
        fi
    else
        if [[ -n ${build[$i]} ]]; then
            echo ${images[$i]} image is already built.
        else
            echo ${images[$i]} image is already pulled.
        fi
    fi
done

echo If no errors occured, setup is complete.
