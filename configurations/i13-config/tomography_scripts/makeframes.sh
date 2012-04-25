#!/bin/bash -x

if [[ $# < 1 ]]
then
   echo "$0 nproj-per-frame"
   exit
fi

nproj=$1
a=0
framenum=0
(( startnum = $framenum * $nproj ))
startfile=`printf "p_%05d.tif" $startnum`

count=0

while [[ -e projections/$startfile ]]
do
   echo "startfile is " $startfile
   (
      (( startnum = $framenum * $nproj ))
      framedir=`printf "frame_%02d/projections" ${framenum}`
      mkdir -p $framedir
      cd $framedir
      set +x
      for ((i=0;i<=nproj;i++))
      do
         (( thisnum = $startnum + $i ))
         ifname=`printf "p_%05d.tif" $thisnum`
         ofname=`printf "p_%05d.tif" $i`
         ln -s ../../projections/$ifname $ofname
      done
) &

set -x
(( framenum++ ))
(( startnum = $framenum * $nproj ))
startfile=`printf "p_%05d.tif" $startnum`
echo " AFTER... startfile is $startfile "
 (( modd = $framenum % 5 ))

if [[ $modd -eq 0 ]]
then
   echo "waiting... "
   wait
fi

done

         
wait
echo "All done! "

