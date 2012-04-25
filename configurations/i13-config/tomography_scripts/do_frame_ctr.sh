#!/bin/bash 

sinoscript="/dls_sw/i12/software/tomography_scripts/sino_listener.py"

if [[ $# -ne 2 ]]
then
   echo "Usage: $0 scanname framenumber"
   echo "scanname is the name of a folder in the current folder containing the tiff projections"
   echo "This program generates sinograms for the specified frame, then applies a range of centre for a test reconstruction"
   exit
fi

scanname=`basename "$1" ".cine"`
fr=$2

visitfolder="/dls/i12/data/2011/ee6893-1/"
basefolder="$visitfolder/processing/"
tiffolder=$basefolder/tiffs/$scanname
sinofolder=$basefolder/sino/$scanname

flatfolder=$basefolder/tiffs/ff$scanname
darkfolder=$basefolder/tiffs/df$scanname

tmpfolder=$visitfolder/tmp/
qoutfolder=$tmpfolder/q_output

#test whether the sinogram folder can be created or accessed
if [[ ! -d $sinofolder ]]
then
   mkdir -p $sinofolder 
fi

if [[ ! -d $sinofolder ]]
then
   echo "ERROR: $sinofolder cannot be created. "
   exit
fi
echo "sinogram folder $sinofolder is OK"

declare -a jobline

mywd=`pwd`
cstart=385
cstep=1
cslice=150

for frame in "frame_46"
#for frame in `ls  $tiffolder`
do
   sinoframe=$sinofolder/$frame/sinograms
   mkdir -p $sinoframe
   if [[ ! -d $sinoframe ]]
   then
      echo " ERROR Could not create frame folder $sinoframe"
      break
   fi

   echo "sinoframe folder will be: " $sinoframe

      datestring=`date +"%m%d%H%M%S"`
      jstring=`/dls_sw/i12/software/tomography_scripts/sino_listener.py  -o $sinoframe -U $datestring -i $tiffolder/$frame/projections -l 504 -w 752 -p 360 -n 16 -Q low.q | tee out$datestring.txt |  grep "JOB NAME IS"`
      rv=$?
      echo "return value" $rv
      echo "JSTRING:" $jstring
      jobline=($jstring)
      nm=${jobline[3]}
      echo "HOLDNAME: " $nm

      set -x
      cd $sinofolder/$frame
      qcentrexml.py $cstart 32 $cstep  $cslice 1 1  $nm
      cd $mywd
      set +x
done






