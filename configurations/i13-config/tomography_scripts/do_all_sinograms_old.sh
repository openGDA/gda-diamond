#!/bin/bash  
#$Id: do_all_sinograms.sh 207 2011-12-09 16:04:34Z kny48981 $
timestamp=`date +%y%m%d%H%M%S%N`
#set up some version tracking
svnid='$Id: do_all_sinograms.sh 207 2011-12-09 16:04:34Z kny48981 $ '
svnurl='$URL: file:///home/kny48981/SVN/progs/scripts/trunk/do_all_sinograms.sh $ '

#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh

#add the modules required 
module add i12


visit="ee7412-1"
year=2012
nflat=18
cstart=1995
cstep=1 
cslice=1300
cnsteps=32
Iflag=0
nproj=6000

rawfolder="processing/rawdata/"
sinofolder="processing/sino/"

usage(){
echo "version information:"
echo $svnid 
echo $svnurl

echo ""
echo "Usage:"
echo "$0 [-y year($year) ] -V visit($visit) -f number-of-flat-fields($nflat) -s start-centre($cstart) -n nsteps-centre($cnsteps) -t centre-step($cstep) -S testslice($cslice) -p nproj -I list-file [REQUIRED]"
echo " -R [raw data folder after 'visit'] (currently $rawfolder)"
echo " -O [sinogram output folder after 'visit'] (currently $sinofolder) "
echo " -n number of projections (currently $nproj) "
echo " "
echo "Generate sinograms and run first centreing routine on a range of samples"
echo "This script submits the jobs to the queue with queue-hold instructions. If the sinograms already exist, their generation is skipped"
echo "the 'list-file' contains the sample names, the flat field should be in a folder of the same name prefixed with 'ff1' "
}

if [[ $# -lt 1 ]]
then
   echo "No command line options specified"
   usage
   exit
fi
Rflag=0

while getopts "V:y:f:s:S:n:t:hI:R:O:p:" flag
do
  case $flag in
  "p")
    nproj=$OPTARG
  ;;
  "R")
    rawfolder="$OPTARG"
    Rflag=1
  ;;
  "O")
    sinofolder="$OPTARG"
    Oflag=1
  ;;
  "I")
    listfile="$OPTARG"
    Iflag=1
  ;;
  "y")
    year=$OPTARG
  ;;
  "V")
    visit=$OPTARG
  ;;
  "f")
    nflat=$OPTARG
  ;;
  "s")
   cstart=$OPTARG
  ;;
  "n")
     cnsteps=$OPTARG
  ;;
  "S")
     cslice=$OPTARG
  ;;
  "t")
     cstep=$OPTARG
  ;;
  "h")
     usage
     exit
  ;;
  esac
done

if [[ $Iflag -ne 1 ]]
then
   echo "*************************"
   echo "ERROR Cannot proceed without input list-file (-I flag)"
   echo "*************************"
   usage
   exit
fi

echo "Using:"
echo "listfile $listfile"
echo "year $year"
echo "visit $visit"
echo "nflat $nflat"
echo "cstart $cstart"
echo "cnsteps $cnsteps"
echo "cslice $cslice"
echo "cstep $cstep"


rootfolder="/dls/i12/data/$year/"
if [[ Rflag -ne 1 ]]
then
rawfolder="processing/rawdata/"
fi
if [[ Oflag -ne 1 ]]
then
sinofolder="processing/sino/"
fi
mywd=`pwd`

echo "Using : "
echo "raw data in $rootfolder/$visit/$rawfolder/"
echo "sinograms into $rootfolder/$visit/$sinofolder/"


if [[ ! -d $rootfolder/$visit/$sinofolder/ ]]
then
   echo "sinogram folder not found"
   echo "$rootfolder/$visit/$sinofolder"
   echo "attempting to create..."
   mkdir $rootfolder/$visit/$sinofolder
fi

if [[ ! -d $rootfolder/$visit/$sinofolder/ ]]
then
   echo "sinogram folder STILL not found"
   echo "sinogram folder STILL not found, or the file of that name is not a folder"
   ls -ld $rootfolder/$visit/$sinofolder
   echo "There must be some permission problem on the parent folder"
   echo "exiting .. "
   exit
fi

while read sname
do
   echo $sname
   pfolder=$rootfolder/$visit/$rawfolder/$sname/projections
   ffolder=$rootfolder/$visit/$rawfolder/ff1$sname/projections
   dfolder=$rootfolder/$visit/$rawfolder/df$sname/projections
   rfolder=$rootfolder/$visit/$sinofolder/$sname
   mkdir  $rfolder

   nflat=`ls $ffolder | wc -w`
   (( nflat = $nflat - 1 ))

   # average the flat field file

   # move to the rfolder 
   cd $rfolder

   echo "Processing the flat field files..."
   flat_capav -i $ffolder -o flat -a $nflat
   echo "Processing the dark field files..."
   flat_capav -i $dfolder -o dark -a $nflat

   #copy the local settings file
   #if available
   if [[ -e $mywd/settings.xml ]]
   then
      echo "Using local reconstruction settings file"
      cp $mywd/settings.xml $rfolder
   else
      echo "Default reconstruction settings file will be used"
   fi

   if [[ -d $rfolder/sinograms ]]
   then

      # do a centering with existing sinograms
      set -x
      qcentrexml.py $cstart $cnsteps $cstep  $cslice 1 1 
      set +x

   else

      #generate sinograms and wait for the job to finish
      #then do the centereing
      nfiles=`ls $pfolder | grep '.tif' | wc -w`
      if [[ $nfiles -ne $nproj ]]
      then
         echo "WARNING: Unexpected number of files in $pfolder : requested $nproj found $nfiles"
         (( nproj = $nfiles - 1 ))
         echo "continuing anyways using $nproj ... "
      else
         echo "number of files matches the request $nfiles $nproj"
      fi

      datestring=`date +"%m%d%H%M%S"`
      jstring=`/dls_sw/i12/software/tomography_scripts/sino_listener.py  -J $sname -U $datestring -i $pfolder -p $nproj -n 16 -Q low.q | tee out$datestring.txt |  grep "JOB NAME IS"`
      rv=$?
      echo "return value" $rv
      declare -a jobline
      echo "JSTRING:" $jstring
      jobline=($jstring)
      nm=${jobline[3]}
      echo "HOLDNAME: " $nm

      set -x
      qcentrexml.py $cstart $cnsteps $cstep  $cslice 1 1  $nm
      set +x

   fi

done < $listfile

