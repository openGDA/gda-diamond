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
   echo "scanname WITHOUT the .cine extension"
   exit
fi
scanname=$1

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

