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
            echo delete.sh Help Page
            echo
            echo This script hard-deletes the docker environments associated with this project.
            echo Hard-deleting includes deleting all persistent data. Use this script carefully.
            echo To simply stop running containers, use stop.sh instead.
            echo
            echo Usage:
            echo "    sh delete.sh -[ah] [Containers...]"
            echo
            echo Arguments:
            echo "    Containers    the containers to hard-delete"
            echo
            echo Flags:
            echo "    -a    hard-delete all containers. Cannot be used with any additional arguments."
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

TO_DELETE=()

if [[ $1 == "-a" ]]
then
    for TOOL in ${tools[@]}; do
        TO_DELETE+=" $TOOL "
    done
else
    STR_TOOLS=" ${tools[*]} "
    for ARG_TOOL in "$@"
    do
        if [[ $STR_TOOLS =~ " ${ARG_TOOL} " ]]
        then
            TO_DELETE+=" $ARG_TOOL "
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

echo
echo WARNING: IRREVERSIBLE DELETION OF DATA
echo
echo Continuing with this delete script will hard-delete all docker containers created by other scripts in this project.
echo This means that all data, including persistent data, will be permanently deleted.
echo This includes all data stored in MongoDB and data indexed in Typesense.
echo
echo If you would simply like to stop the running containers, do not continue this script and run stop.sh instead.
echo
echo If you would like to permanently delete all data stored in docker containers, continue this script.
echo
echo The following tools will be deleted and all persistent data lost:
for TOOL in ${TO_DELETE[@]}
do
    echo "    ${TOOL}"
done
echo
read -p "Do you want to continue? [Yes/no] >" -r
echo

if [[ $REPLY =~ ^Yes$ ]]; then
    echo THIS SCRIPT WILL IRREVERSIBLY DELETE PERSISTENT DATA.
    echo 
    read -p "I want to continue and irreversibly delete my data. [Confirm] >" -r
    echo
    if [[ $REPLY =~ ^Confirm$ ]]
    then
        for TOOL in ${TO_DELETE[@]}; do
            INDEX=$(get_tool_index $TOOL)
            NAME=${names[$INDEX]}
            ID="$(docker ps -a -q --filter name=$NAME --format="{{.ID}}")"
            echo Finding container with name $NAME...
            if [[ -n "$ID" ]]; then
                echo Deleting container $NAME...
                DEL_ID=$(docker rm $(docker stop $ID))
                echo Container $DEL_ID deleted.
            else
                echo No container was found. Use \'docker container ls -a\' and verify containers were created with naming conventions established in vars.sh.
            fi
            echo
        done
        echo Hard delete complete.
        exit
    fi
fi
echo Hard delete was not continued.