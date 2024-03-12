#!/bin/sh

ls -trsh | tail -10 ; 
SCAN=$((SCAN+1))

if [[ $SCAN -eq 1 ]]; then
  for f in $VISIT/*.nxs ; do
    [[ $f -nt $newest ]] && newest=$f
  done
  SCAN=$(basename $newest)
  export SCAN=${SCAN%.nxs}
fi
echo -e "\nSCAN=$SCAN\n"
