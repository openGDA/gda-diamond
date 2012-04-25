#!/bin/bash
#$Id: qcine.sh 132 2011-02-14 17:54:38Z kny48981 $
#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh #add the modules required #so that the qsub command is available

module add global/cluster >& /dev/null
#bash method for separating a line of 'words'
declare -a fline
if [[ $# -lt 1 ]]
then
   echo "Usage: $0 scanname "
   echo "scanname is the name of a file in the current folder with the .cine extension"
   exit
fi

scanname=`basename "$1" ".cine"`

#set hard coded base folder
set -x
visitfolder="/dls/i12/data/2011/ee6893-1/"
basefolder="$visitfolder/processing/"
infolder=$basefolder/rawdata/
outfolder=$basefolder/tiffs/$scanname/projections
tmpfolder=$visitfolder/tmp/
qoutfolder=$tmpfolder/q_output
if [[ ! -d $qoutfolder ]]
then
   mkdir -p $qoutfolder
fi

if [[ ! -d $outfolder ]]
then
   mkdir -p $outfolder 
fi

if [[ ! -d $outfolder ]]
then
   echo "ERROR: $outfolder cannot be created. "
   exit
fi
   nf=22143
   bname=$infolder/$scanname.cine
   set -x
   #hard code the extraction script ; 
   echo "/dls_sw/i12/software/tomography_scripts/extract_cine_gourlay $bname $outfolder 1 $nf" | \
       qsub -P i12 -q high.q -N cin_${scanname} -e $qoutfolder -o $qoutfolder -pe smp 8 -cwd
   set +x
   

#also do the flat and dark extractions

bn=`basename "$1" ".cine"`

for prefix in 'ff' 'df'
do
scanname=${prefix}$bn

if [[ ! -e $scanname.cine ]]
then 
   echo "Flat/dark file $scanname.cine was not found"
   exit
fi

set -x
outfolder=$basefolder/tiffs/$scanname/projections
avfolder=$basefolder/tiffs/$scanname
avname=$prefix.tif
if [[ ! -d $qoutfolder ]]
then
   mkdir -p $qoutfolder
fi

if [[ ! -d $outfolder ]]
then
   mkdir -p $outfolder 
fi

if [[ ! -d $outfolder ]]
then
   echo "ERROR: $outfolder cannot be created. "
   exit
fi
   nf=100
   bname=$infolder/$scanname.cine
   set -x
   #hard code the extraction script ; 
   echo "/dls_sw/i12/software/tomography_scripts/extract_cine_gourlay $bname $outfolder 1 $nf" | \
       qsub -P i12 -q high.q -N cin_${scanname} -e $qoutfolder -o $qoutfolder -pe smp 8 -cwd

   echo "/dls_sw/i12/software/tomography_scripts/flat_capav -i $outfolder -a 99 -w 752 -l 504 -o $avfolder -f $avname  " | \
       qsub -P i12 -q high.q -N av_$scanname -hold_jid cin_${scanname} -e $qoutfolder -o $qoutfolder -pe smp 8 -cwd
   set +x

done


