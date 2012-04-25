#!/bin/bash 
#$Id: dark_array.sh 121 2010-11-26 20:09:26Z kny48981 $
timestamp=`date +%y%m%d%H%M%S%N`
#set up some version tracking
svnid='$Id: dark_array.sh 121 2010-11-26 20:09:26Z kny48981 $ '
svnurl='$URL: file:///home/kny48981/SVN/progs/tomo_recon_pipe/scripts/dark_array.sh $ '
export PATH=/bin:/usr/bin:$PATH
export HOME=/tmp

#hard code SGE 
#hard code SGE
#export SGE_ROOT=/dls_sw/apps/sge/SGE6.2
#export SGE_CELL=DLS
#ARCH=lx24-x86
#
#echo $ARCH
#
#export SGE_QMASTER_PORT=60000
#export SGE_EXECD_PORT=60001


#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh
#add the modules required 
module add i12
module add /dls_sw/i12/modulefiles/local-64
module add global/cluster
##hard code the library paths
#export LD_LIBRARY_PATH=/dls_sw/i12/software/intel/lib64:/dls_sw/i12/software/64/lib:$LD_LIBRARY_PATH
#export PATH=/dls_sw/i12/software/64/bin:/dls_sw/i12/software/tomography_scripts:$PATH


#initialize some default values
sdate=`date`
mypid=$$
mydir=$PWD
ifile=${mydir}/settings.in 
chunkdir=${mydir}/ch #folder containing the data 
nchunks=16
#autochunk=1
cleanupflag=0
realflag=1
centreflag=0
Centre=0  #0=use midpoint 1=use entered value
radflag=0 #0=use full radius 1=use input value
Rad=100
sliceflag=0 #0=use last slice 1=use entered value
lastslice=0
sinogramflag=1
gpuflag=0
xflag=0
TRYLIMIT=10
jsuffix=$mypid
firstchunk=1
avflag=0
nsegs=1
nproj=1
qqueue=medium.q
wd=4008
ht=167

printusage(){
echo " usage:"
echo "$0 -n nchunks -i input -o output -s segments -U uniqueid -C center [ -R radius] [-c  etc. etc.]"
echo " -U specify unique identifier (REQUIRED) "
echo " -a naverage - how many images to average (REQUIRED)"
echo " -n nchunks - how many of the available chunks to reconstruct"
echo " -H auto hold for prior job "
echo " -J jobname - short mnemonic name to include in the job name"
echo " -j suffix - job suffix name -- defult is script PID "
echo " -i folder containing the projection data split into chunks"
echo " -o folder in which to place the solution files"
echo " -O Output how many slices of each chunk (starting at slice 0 )  omit for all slices"
echo " -w width (default 4008)"
echo " -l length (height) of each chunk (default 167 i.e. 16 chunks)"
echo " -p projections per segment"
echo " -s segments per tomography dataset"
echo " -R radius (percent) from center to reconstruct (omit for full radius)"
echo " -C specify the center (omit to use  midpoint of image) "
echo " -I specify the input settings file ( default: settings.in ) "
echo " -G use Tesla GPU  "
echo " -c for cleanup (removes sinograms after reconstruction) "
echo " -x for debug (bash -x flag) "
}


if [[ $# -le 1 ]]
then 
printusage;
exit;
fi

echo "Submitting a darkfield averageing batch job"
echo "Nanosecond Timestamp: $timestamp   [yymmddhhmmss and nanoseconds]"
echo "PID of Submitting Script: $mypid"
oflag=0
namestr=''
uniqueflag=0
suffixflag=0
vflag=0

while getopts "a:U:f:O:C:EGH:I:J:N:R:STZ:b:cdf:hi:j:l:n:o:p:s:vw:xz:" flag
do
  echo "$flag" $OPTIND $OPTARG
  case $flag in
  "x")
  echo "debug x"
  xflag=1
  ;;
  "G")
  echo "GPU"
  gpuflag=1
  ;;
  "H")
  echo "HOLD"
  holdflag=1
  holdname="$OPTARG"
  ;;
  "I")
  echo "Input settings file"
  ifile="$OPTARG"
  ;;
  "S")
  echo "Sinograms provided"
  sinogramflag=0;
  ;;
  "J")
  namestr=$OPTARG
  echo "Job name $namestr "
  ;;
  "U")
  echo "Unique id "
  uniqueid=$OPTARG
  uniqueflag=1
  ;;
  "j")
  echo "job suffix"
  jsuffix=$OPTARG
  suffixflag=1
  ;;
  "O")
  echo "Slices"
  sliceflag=1;
  lastslice=$OPTARG
  ;;
  "R")
  echo "Radius"
  radflag=1;
  Rad=$OPTARG
  ;;
  "C")
  echo "Centre"
  centreflag=1;
  Centre=$OPTARG
  ;;
  "c")
  echo "cleanup"
  cleanupflag=1;
  ;;
  "w")
  echo "width" $OPTARG
  wd=$OPTARG
  ;;
  "l")
  echo "length (height) of a chunk" $OPTARG
  ht=$OPTARG
  ;;
  "s")
  echo "segments" $OPTARG
  nsegs=$OPTARG
  ;;
  "p")
  echo "projections per segment" $OPTARG
  nproj=$OPTARG
  ;;
  "f")
  echo "firstchunk" $OPTARG
  firstchunk=$OPTARG
  ;;
  "a")
  echo "naverage" $OPTARG
  navg=$OPTARG
  avflag=1
  ;;
  "n")
  echo "nchunks" $OPTARG
  nchunks=$OPTARG
 # autochunk=0
  ;;
  "i")
  echo "input folder" $OPTARG
  chunkdirstr=$OPTARG
  ;;
  "o")
  echo "output folder" $OPTARG
  outdirstr=$OPTARG
  oflag=1
  ;;
  "d")
  echo "dryrun" 
  realflag=0
  ;;
  "h")
  printusage;
  exit
  ;;
  "v")
  vflag=1
  echo "Verbose flag selected"
  ;;
  "?")
  printusage;
  exit
  ;;
  esac

done
if [[ $xflag -ne 0 ]]
then
set -x 
fi

if [[ $avflag -ne 1 ]]
   then
      echo "MUST SPECIFY NUMBER TO AVERAGE with -a flag!"
      exit
   fi

if [[ $uniqueflag -ne 0 ]]
then
mypid=$uniqueid
else
echo "MUST SPECIFY UNIQUE ID with -U flag!"
exit
fi

echo "Unique ID used: $mypid"

if [[ suffixflag -ne 0 ]]
then
jsuffix=$mypid
fi
echo "Job name suffix used: $jsuffix "


   DIR=$(dirname $chunkdirstr)
   DIR=$(cd "$DIR" 2> /dev/null && pwd -P)
   if [[ -n "$DIR" ]] ; then
      chunkdir="$DIR/${chunkdirstr##*/}"
   fi 
   jname="r${namestr}${jsuffix}"

if [[ oflag -eq 0 ]]
then
outdir=$chunkdir
else
   DIR=$(dirname $outdirstr)
   #add a comment explaining what this does
   DIR=$(cd "$DIR" 2> /dev/null && pwd -P)
   if [[ -n "$DIR" ]] ; then
      outdir="$DIR/${outdirstr##*/}"
   fi 
fi
echo "outdir= $outdir"


#check that the folder exists
if [[ ! -e $chunkdir ]]
then
   echo "data folder $chunkdir not found!"
   mkdir -p $chunkdir
fi


#check if its a dry-run
if [[ $realflag != 1 ]]
then
   exit
fi

#calculate the sinogram size
(( sinolen = $ht * $wd ))

##count the chunks
#if [[ $autochunk -eq 1 ]]
#then
#echo "Autochunk"
#   cd $chunkdir
#   nchunks=`ls -ld [0-9]* | grep '^d' | wc -l`
#   cd $mydir
#fi
#
   #create a queue script
   cat > rundarkq.qsh <<-EOF
#!/bin/bash 
set -x

#add the modules required to run Valeriy's code
source /dls_sw/i12/modulefiles/modules.sh
module add i12
module add /dls_sw/i12/modulefiles/local-64
module add /dls_sw/i12/modulefiles/intel-32
module add global/cluster
myjob=\$JOB_ID
tasknum=\${SGE_TASK_ID}  
# the zero-padded task number
# is used for the chunk number
i=\`printf "%03d" \${tasknum}\`
logname=\`printf "dk_%s_t%s" \$myjob \$i\`
ddir=${outdir}/\$i #the output folder

if [[ ! -d \${ddir} ]]
then
   #handle a missing chunk folder
   echo "chunk folder \${ddir} not found!"
   echo "creating chunk folder \${ddir} "
   mkdir -p \${ddir}
fi

flat_chunk_capavg.q -f dark.tif  -w $wd -l $ht -i $chunkdir -J \$logname -o $outdir -p 1 -s 1 -a $navg -m \$tasknum 

EOF
  #sumbit the "dark" job
echo "Submitting the 'dark' job..."
darkname="dk_${jname}"
qstring=`qsub ${qpflag} -t $firstchunk-$nchunks -q $qqueue  -cwd -pe smp 4 -N "${darkname}" rundarkq.qsh`
retval=$?
echo "qstring = $qstring"
echo "Dark script returned: " $retval

#get the assigned task number
oifs=$IFS
IFS=' 	.:'
qout=(${qstring})
qtask=${qout[2]}
echo "queue dark task number: ${qtask}"
echo "queue dark job name: ${flatname}"

IFS=$OIFS
if [[ $retval -ne 0 ]]
then 
  echo $qstring
  echo "ERROR: The 'dark' script returned a bad status for the queue submission."
  echo "ERROR: Please check the output of the queue submission above for problems."
  echo "ERROR: Since the script got this far, the tasks for the reconstruction were"
  echo "ERROR: probably submitted, but you will not receive email notification "
  echo "ERROR: and the post-reconstruction cleanup will not be performed."
else
echo "Your darkfield task $qtask from script PID $mypid has been submitted." 
fi

if [[ $xflag -ne 0 ]]
then
set +x 
fi
