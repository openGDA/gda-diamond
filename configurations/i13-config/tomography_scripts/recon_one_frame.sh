#!/bin/bash 

#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh
#add the modules required 

module add i12
module add global/cluster

scanname=$1
framenum=$2
centre=$3

visitfolder="/dls/i12/data/2011/ee6893-1/"
basefolder="$visitfolder/processing/"
sinofolder=$basefolder/sino/$scanname
imagefolder=$basefolder/images/$scanname

flatfolder=$basefolder/tiffs/ff$scanname
darkfolder=$basefolder/tiffs/df$scanname

tmpfolder=$visitfolder/tmp/
qoutfolder=$tmpfolder/q_output

mkdir -p qoutfolder


if [[ ! -d $imagefolder ]]
then
   mkdir -p $imagefolder 
fi

if [[ ! -d $imagefolder ]]
then
   echo "ERROR: $imagefolder cannot be created. "
   exit
fi
echo "sinogram folder $imagefolder is OK"

   frame=`printf "frame_%02d" $framenum`
   imageframe=$imagefolder/$frame
   sinoframe=$sinofolder/$frame

   mkdir -p $imageframe
   if [[ ! -d $imageframe ]]
   then
      echo " ERROR Could not create frame folder $imageframe"
      break
   fi

   echo "imageframe folder will be: " $imageframe
   if [[ ! -e settings.xml  ]]
   then
      echo "ERROR: requires a template settings.xml file in the local folder for the reconstruction"
      exit
   fi
   recon_arrayxml.py -I settings.xml -C $centre -w 752 -l 504 -i $sinoframe -o $imageframe
   




