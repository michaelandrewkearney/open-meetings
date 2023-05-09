#!/bin/bash

PLATFORM="linux/amd64"
MY_UNAME=$(uname -a)
if [[ -n $(uname -a | grep arm64) ]]; then
    PLATFORM="linux/arm64"
fi


# maintain order of all arrays when adding new containers or arrays
export tools=('tika' 'mongodb' 'typesense')
export names=('omp-tika' 'omp-mongodb' 'omp-typesense')
export repos=('open-meetings' 'arm64v8' 'typesense')
export images=('tika' 'mongo' 'typesense')
export tags=('2.7.0.1-full' '6' '0.24.1')
export ports=('9998' '27017' '8108')
export build=('docker build --platform=${PLATFORM} -t open-meetings/tika:2.7.0.1-full - < tika-dockerfile' '' '')

get_tool_index() {
    for i in "${!tools[@]}"; do
        if [[ "${tools[$i]}" = "$1" ]]; then
            echo "${i}"
            return 0
        fi
    done
    return 1
}

export -f get_tool_index

# associative arrays are not support by bash<4.0

# containers=('tika' 'mongodb' 'typesense')

# declare -A repo
# declare -A image
# declare -A tag
# declare -A port

# repo[$containers[0]]='apache'
# image[$containers[0]]='tika'
# tag[$containers[0]]='2.7.0.1'
# port[$containers[0]]='9998'

# repo[$containers[1]]='mongodb'
# image[$containers[1]]='mongodb-community-server'
# tag[$containers[1]]='6.0-ubi8'
# port[$containers[1]]='27017'

# repo[$containers[2]]='typesense'
# image[$containers[2]]='typesense'
# tag[$containers[2]]='0.24.1'
# port[$containers[2]]='8108'