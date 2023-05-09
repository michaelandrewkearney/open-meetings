#!/bin/bash

source "$(dirname $0)"/vars.sh

while getopts "ah" OPTION
do
	case $OPTION in
		a)
            if ! [ "$#" -eq 1 ]
            then
                echo Usage error: cannot pass any arguments with -a flag.
                echo
                echo Exiting script...
                exit
            fi
			;;
        h)
            echo
            echo stop.sh Help Page
            echo
            echo This script stops the docker environments associated with this project.
            echo
            echo Usage:
            echo "    sh stop.sh -[ah] [Containers...]"
            echo
            echo Arguments:
            echo "    Containers    the containers to stop"
            echo
            echo Flags:
            echo "    -a    stop all containers. Cannot be used with any additional arguments."
            echo "    -h    view help information"
            echo
            exit
            ;;
		\?)
			echo "Unrocognized flag. Run this script with the -h flag for help."
            echo
            echo Exiting script...
			exit
			;;
	esac
done

TO_STOP=()

if [[ $1 == "-a" ]]
then
    for TOOL in ${tools[@]}; do
        TO_STOP+=" $TOOL "
    done
else
    STR_TOOLS=" ${tools[*]} "
    for ARG_TOOL in "$@"
    do
        if [[ $STR_TOOLS =~ " ${ARG_TOOL} " ]]
        then
            TO_STOP+=" $ARG_TOOL "
        else
            echo Tool \'$ARG_TOOL\' not recognized. The tools are:
            for REAL_TOOL in ${tools[@]}
            do
                echo "    ${REAL_TOOL}"
            done
            echo
            echo Exiting script...
            exit
        fi
    done
fi

for TOOL in ${TO_STOP[@]}; do
    echo
    INDEX=$(get_tool_index $TOOL)
    NAME=${names[$INDEX]}
    echo Finding container with name $NAME...
    ID="$(docker ps -a -q --filter name=$NAME --format="{{.ID}}")"
    if [[ -n "$ID" ]]; then
        echo Stopping container $NAME with ID $ID...
        STOP_ID=$(docker stop $ID)
        echo Container $NAME with ID $STOP_ID is stopped.
    else
        echo Could not find container with name $NAME.
    fi
done
