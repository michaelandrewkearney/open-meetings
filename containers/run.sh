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
            echo run.sh Help Page
            echo
            echo This script runs the docker environments associated with this project.
            echo
            echo Usage:
            echo "    sh run.sh -[ah] [Containers...]"
            echo
            echo Arguments:
            echo "    Containers    the containers to run"
            echo
            echo Flags:
            echo "    -a    run all containers. Cannot be used with any additional arguments."
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

TO_RUN=()

if [[ $1 == "-a" ]]
then
    for TOOL in ${tools[@]}; do
        TO_RUN+=" $TOOL "
    done
else
    STR_TOOLS=" ${tools[*]} "
    for ARG_TOOL in "$@"
    do
        if [[ $STR_TOOLS =~ " ${ARG_TOOL} " ]]
        then
            TO_RUN+=" $ARG_TOOL "
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

for TOOL in ${TO_RUN[@]}; do
    echo
    echo Running $TOOL...
    source $(dirname $0)/run_"$TOOL".sh
done