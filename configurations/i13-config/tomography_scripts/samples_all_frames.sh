#!/bin/bash

if [[ $# -ne 1 ]]
then
   echo "Usage: $0 list-file"
   echo "list-file contains the list of scanname and centre on each row"
   exit
fi

declare -a inline
while read inputline
do
   inline=($inputline)
  scan=${inline[0]}
  centre=${inline[1]}
   ./do_all_frames.sh  $scan $centre
done < $1
