#!/bin/bash

if [[ $# -ne 2 ]]
then
   echo "Usage: $0 list-file framenumber"
   echo "list-file contains the list of scanname and centre on each row"
   exit
fi
framenumber=$2

declare -a inline
while read inputline
do
   inline=($inputline)
  scan=${inline[0]}
  centre=${inline[1]}
   ./do_one_frame.sh  $scan $framenumber $centre
done < $1
