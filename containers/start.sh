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
            echo start.sh Help Page
            echo
            echo This script starts the docker environments associated with this project.
            echo
            echo Usage:
            echo "    sh start.sh -[ah] [Containers...]"
            echo
            echo Arguments:
            echo "    Containers    the containers to start"
            echo
            echo Flags:
            echo "    -a    start all containers. Cannot be used with any additional arguments."
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

TO_START=()

if [[ $1 == "-a" ]]
then
    for TOOL in ${tools[@]}; do
        TO_START+=" $TOOL "
    done
else
    STR_TOOLS=" ${tools[*]} "
    for ARG_TOOL in "$@"
    do
        if [[ $STR_TOOLS =~ " ${ARG_TOOL} " ]]
        then
            TO_START+=" $ARG_TOOL "
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

for TOOL in ${TO_START[@]}; do
    echo
    INDEX=$(get_tool_index $TOOL)
    NAME=${names[$INDEX]}
    echo Finding container with name $NAME...
    ID="$(docker ps -a -q --filter name=$NAME --format="{{.ID}}")"
    if [[ -n "$ID" ]]; then
        echo Starting container $NAME with ID $ID...
        STOP_ID=$(docker start $ID)
        echo Container $NAME with ID $STOP_ID is started.
    else
        echo Could not find container with name $NAME.
    fi
done
