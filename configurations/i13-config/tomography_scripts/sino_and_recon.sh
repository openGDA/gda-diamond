#!/bin/bash
#set -x
#$Id: sino_and_recon.sh 214 2012-02-13 15:46:36Z kny48981 $
SCRIPTPATH=/dls_sw/i12/software/tomography_scripts
timestamp=`date +%y%m%d%H%M%S%N`
#set up some version tracking
svnid='$Id: sino_and_recon.sh 214 2012-02-13 15:46:36Z kny48981 $ '
svnurl='$URL: file:///home/kny48981/SVN/progs/tomo_recon_pipe/scripts/sino_and_recon.sh $ '

#initialize some default values
sdate=`date`
mypid=$$
mydir=$PWD

printusage(){
echo " usage:"
echo "$0 -n nchunks -f folder -o output -s slices -C center -R radius [-c -S]"
echo " -n nchunks - how many of the available chunks to reconstruct"
echo " -J jobname - short mnemonic name to include in the job name"
echo " -w image width "
echo " -l image chunk lenght (height ) "
echo " -0 how many slices of each chunk (starting at slice 0 )  omit for all slices"
echo " -s segments "
echo " -p number of projections per segment"
echo " -R radius (percent) from center to reconstruct (omit for full radius)"
echo " -C specify the center (omit to use  midpoint of image) "
echo " -I specify the input settings file ( default: settings.in ) "
echo " -S bypass sinogram creation "
echo " -G use Tesla GPU  "
echo " -E use existing projections  "
echo " -z time-out polling interval  "
echo " -Z time-out   "
echo " -b number of bytes "
echo " -x for debug (bash -x flag) "
}


if [[ $# -le 1 ]]
then 
printusage;
exit;
fi

echo "Submitting a tomographic reconstruction master job"
echo "Nanosecond Timestamp: $timestamp   [yymmddhhmmss and nanoseconds]"
echo "PID of Submitting Script: $mypid"
oflag=0
namestr=''


#$SCRIPTPATH/sino_listener.py -i huge -o huge-2-out -w 4000 -l 125  -n 1 -b 2 -s 10 -p 10 -z 1 -Z 10 -E

jstring=`$SCRIPTPATH/sino_listener.py $*  -i projections/ -o sinograms | tee out.txt |  grep "JOB NAME IS"`
rv=$?
echo "return value" $rv
declare -a jobline
echo "JSTRING:" $jstring
jobline=($jstring)
nm=${jobline[3]}
echo "HOLDNAME: " $nm

set -x
$SCRIPTPATH/recon_array.sh $*  -i sinograms -o image -j $mypid -H $nm
set +x

# set +x


