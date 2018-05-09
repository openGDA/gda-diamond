#!/bin/bash 
#$Id: recon_array.sh 214 2012-02-13 15:46:36Z kny48981 $
timestamp=`date +%y%m%d%H%M%S%N`
#set up some version tracking
svnid='$Id: recon_array.sh 214 2012-02-13 15:46:36Z kny48981 $ '
svnurl='$URL: file:///home/kny48981/SVN/progs/tomo_recon_pipe/scripts/recon_array.sh $ '
export PATH=/bin:/usr/bin:$PATH
export HOME=/tmp

#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh
#add the modules required 

module add /dls_sw/i12/modulefiles/local-64
module add global/cluster

##hard code the library paths
#export LD_LIBRARY_PATH=/dls_sw/i12/software/intel/lib64:/dls_sw/i12/software/64/lib:$LD_LIBRARY_PATH
#export PATH=/dls_sw/i12/software/64/bin:/dls_sw/i12/software/tomography_scripts:$PATH


#initialize some default values
sdate=`date`
timestamp=`date +%s`
mypid=$$
mydir=$PWD
ifile=${mydir}/settings.in 
chunkdir=${mydir}/ch #folder containing the data 
nchunks=16
cleanupflag=0
realflag=1
centreflag=0
Centre=0  #0=use midpoint 1=use entered value
radflag=0 #0=use full radius 1=use input value
Rad=100
sliceflag=0 #0=use last slice 1=use entered value
lastslice=0
ht=167
wd=4008
sinogramflag=1
gpuflag=0
xflag=0
TRYLIMIT=10

printusage(){
echo " usage:"
echo "$0 [-f firstchunk] -n lastchunk -i input -o output -s segments -U uniqueid -C center [ -G ] [ -R radius] [-c  etc. etc.]"
echo " -U specify unique identifier (REQUIRED) "
echo " -Q specify queue (default: low.q) "
echo " -f firstchunk - first chunk to reconstruct"
echo " -n nchunks - last chunk to reconstruct"
echo " -H auto hold for prior job "
echo " -J jobname - short mnemonic name to include in the job name"
echo " -j suffix - job suffix name -- defult is script PID "
echo " -i folder containing the projection data split into chunks"
echo " -o folder in which to place the solution files"
echo " -O Output how many slices of each chunk (starting at slice 0 )  omit for all slices"
echo " -w width"
echo " -l length (height) of each chunk"
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

echo "Submitting a tomographic reconstruction batch job"
echo "Nanosecond Timestamp: $timestamp   [yymmddhhmmss and nanoseconds]"
echo "PID of Submitting Script: $mypid"
oflag=0
namestr='recon'
uniqueflag=0
suffixflag=0
nsegs=1 #default
vflag=0
firstchunk=1
qqueue="low.q"

while getopts "Q:U:O:C:EGH:I:J:N:R:STZ:b:cdf:hi:j:l:n:o:p:s:vw:xz:f:" flag
do
  echo "$flag" $OPTIND $OPTARG
  case $flag in
  "Q")
  echo "queue"
  qqueue=$OPTARG
  ;;
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
  "n")
  echo "nchunks" $OPTARG
  nchunks=$OPTARG
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

jsuffix=$mypid
qscript=recon_$mypid.qsh
finishscript=finish_$mypid.qsh

if [[ $uniqueflag -ne 0 ]]
then
mypid=$uniqueid
else
uniqueid=$timestamp
mypid=$uniqueid
echo "Unique id not specified -- default: timestamp $timestamp used!"
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
   echo "ERROR: data folder $chunkdir not found!"
   exit
fi

#check that the folder exists
if [[ ! -e $ifile ]]
then
   echo "ERROR: settings file $ifile not found!"
   exit
fi

#check if its a dry-run
if [[ $realflag != 1 ]]
then
   exit
fi

#calculate the sinogram size
(( sinolen = $ht * $wd ))

   #create a queue script
   cat > $qscript <<-EOF
#!/bin/bash 
set -x

#add the modules required to run Valeriy's code
source /dls_sw/i12/modulefiles/modules.sh
module add /dls_sw/i12/modulefiles/local-64
module add /dls_sw/i12/modulefiles/intel-32
module add global/cluster
myjob=\$JOB_ID
tasknum=\${SGE_TASK_ID}  
(( zchunk = \$tasknum - 1 ))
i=\`printf "%03d" \${tasknum}\`
ddir=${chunkdir}/

if [[ ! -d \${ddir} ]]
then
   #handle a missing chunk folder
   echo "chunk folder \${ddir} not found!"
   exit
fi

#handle errors reported by sinogram creation
if [[ -e error_$mypid.txt ]]
then
   echo "Cravenly refusing to attempt reconstruction after sinogram error"
   exit
fi

cd \$ddir

#find the width and divide by two (dumb autocenter)
#declare -a tiffline
#tiffline=(\`tiffinfo c\${i}_p00000.tif | grep Width\`)
#tifwid=\${tiffline[2]}
#tifflen=\${tiffline[5]}
(( tifcen = $wd / 2 ))
odir=${outdir}/recon_job\$JOB_ID
if [[ ! -e \${odir} ]]
then
mkdir -p \${odir}
fi
EOF

if [[ $centreflag -eq 0 ]]
then
cat >> $qscript <<-EOF
	CEN="\${tifcen}.5"
	EOF
	
else
cat >> $qscript <<-EOF
	CEN=$Centre
	EOF
	
fi

echo "sliceflag = $sliceflag "
if [[ sliceflag -eq 1 ]]
then
echo "using input slice"
   cat >> $qscript <<-EOF
   SLI=$lastslice
EOF

else echo "using auto last slice"
cat >> $qscript <<-EOF
  ((  SLI = $ht - 1 ))
EOF
fi


cat >> $qscript <<-EOF
dfile="${mydir}/d_${jname}_\$i.txt"

#count the projections
#npro=\`ls c\${i}_p*.tif | wc -w\`
#(( npro -- ))
#echo \$npro
#if [[ \$npro -le 0 ]]
#then
#echo "ERROR: projection files not found for chunk \${i} in job-id \$JOB_ID "
#echo "ERROR: projection files not found for chunk \${i} in job-id \$JOB_ID " >> \$dfile
#exit
#fi

npro=${sinolen}

echo "Reconstruction log for chunk \$i" >> \$dfile
echo "Running on host \$HOSTNAME \$i" >> \$dfile
echo "CEN = " \$CEN >> \$dfile
echo "SLI = " \$SLI >> \$dfile
echo "npro = " \$npro >> \$dfile
echo "Rad = " ${Rad} >> \$dfile

(( fslice = $ht * \$zchunk ))
(( lslice = \$fslice + \$SLI ))

#swap the control parameters for Valeriy's reconstruction
cd $mydir
sed -e "s/^input_file_prefix.*$/input_file_prefix = sino_ /" \
       -e "s|^input_file_path.*$|input_file_path = ./|" \
       -e "s|^flat_field_file.*$|flat_field_file = ../flat/flat.tif|" \
       -e "s|^dark_noise_file.*$|dark_noise_file = ../dark/dark.tif|" \
       -e "s/^output_file_prefix.*$/output_file_prefix = image_/" \
       -e "s|^output_file_path.*$|output_file_path = \${odir}|" \
       -e "s/^image_centre.*$/image_centre = \$CEN /" \
       -e "s/^slices_first.*$/slices_first = \$fslice /" \
       -e "s/^slices_last.*$/slices_last = \$lslice /" \
       -e "s/^backprojection_radius2_value.*$/backprojection_radius2_value = ${Rad} /" \
       ${ifile} > \${ddir}/settings_\${i}_${uniqueid}.in


#go back to the data directory
cd \${ddir}
EOF


#do the reconstruction using cpu code
if [[ gpuflag -eq 0 ]]
then
processor=" CPU "
cat >> $qscript <<-EOF
echo "before reconstruction" >> \$dfile
date >> \$dfile
#TEMPORARY (I hope) workaround for peculiar Lustre problem
###cp \`which VT_reconstruct\` .
VT_reconstruct settings_\${i}_${uniqueid}.in out_\${i}_${uniqueid}.txt >& \${odir}/recon_\$i.out  
recretval=\$?
echo "before compressing" >> \$dfile
date >> \$dfile

#go to the solution directory and compress the chunk
cd \${odir}
#tar -zcvf c\${i}_solution.tgz c\${i}_sol*.tif

echo "end of script " >> \$dfile
date >> \$dfile
echo "\$myjob \$i \$flopretval \$recretval " >> ${mydir}/array_returns_\${myjob}.txt
echo 
set +x
EOF
else
processor=" Tesla "
qpflag=" -P i12"
cat >> $qscript <<-EOF
mycuda=0
cudafound=0
tries=0
mylockdir=/tmp/tomo-i12-\$USER/lock

mydate=\`date\`
mkdir -p \$mylockdir
#try to acquire a lock representing one of the cuda cards
while [[ \$cudafound -eq 0 ]]
do

   for mycuda in 0 1 
   do
       mylockf=\$mylockdir/cuda\$mycuda
       exec 8>>\$mylockf

       if  flock -w 5 -x 8
       then
          cudafound=1
          echo "host \$HOSTNAME date \$mydate job \$myjob task \$tasknum"  >> \$mylockf
          echo "Got lock on \$mylockf"
          break
       else
          echo "Did not get lock on \$mylockf"
       fi
   done
    if [[ \$cudafound -eq 0 ]]
    then
       (( tries ++ ))
       if [[ \$tries -gt 10 ]]
       then
            echo "Could not acquire the lock on a CUDA device lock-file!"
            echo "Check \$mylockdir "
            exit
       fi
     sleep 5
     fi

done


echo "using cuda \$mycuda " >> \$dfile


echo "before reconstruction" >> \$dfile

date >> \$dfile
#run the reconstruction routine
dt64c  -c  \${ddir}/settings_\${i}_${uniqueid}.in -o \${odir}/output_\${i}_${uniqueid}.out  -G \$mycuda  >& \${odir}/recon_${uniqueid}_\$i.out  
recretval=\$?
echo "reconstruction routine returned \$recretval" >> \$dfile
cp out_\${i}_${uniqueid}.txt \$odir
cp settings_\${i}_${uniqueid}.in \$odir

echo "before compressing" >> \$dfile
date >> \$dfile
cd \$odir
#tar -zcvf c\${i}_solution.tgz c\${i}_sol*.tif

echo "end of script" >> \$dfile
date >> \$dfile
echo "\$myjob \$i \$flopretval \$recretval " >> \${odir}/array_returns_\${myjob}.txt
echo 
set +x
EOF
fi

if [[ cleanupflag -eq 1 ]]
then
cat >>$qscript <<-EOF
set -x
#rm c\${i}_s*.tif
rm c\${i}_sol*.tif
echo "after cleanup" >> \$dfile
date >> \$dfile
set +x
EOF


fi

if [[ $holdflag -ne 0 ]]
then
holdstring="-hold_jid $holdname"
else
holdstring=""
fi

#submit the script to the queue
declare -a qout
qstring=`qsub ${qpflag} -t $firstchunk-$nchunks -q $qqueue $holdstring  -cwd -pe smp 4 -N "${jname}" $qscript`
retval=$?
echo $qstring
echo "Script returned: " $?
if [[ $retval -ne 0 ]]
then 
  echo "ERROR: The script returned a bad status for the queue submission."
  echo "ERROR: Please check the output of the queue submission above for problems."
  exit
fi

#get the assigned task number
oifs=$IFS
IFS=' 	.:'
qout=(${qstring})
qtask=${qout[2]}
echo "queue task number: ${qtask}"
IFS=$OIFS

echo "  "
echo "Internal Variables: "
echo "timestamp = " $timestamp "yymmddhhmmss and nanoseconds"
echo "jobname = " $jname 
echo "mypid = " $mypid 
echo "mydir = " $mydir 
echo "chunkdir = " $chunkdir 
echo "nchunks = " $nchunks 
echo "cleanupflag = " $cleanupflag 
echo "realflag = " $realflag 
echo "centreflag = " $centreflag 
echo "Centre = " $Centre 
echo "radflag = " $radflag 
echo "Rad = " $Rad 
echo "sliceflag = " $sliceflag 
echo "lastslice = " $lastslice 
echo "qpflag = " $qpflag
echo "  "
echo "Waiting..."
wait
echo "Reconstruction Jobs sumbitted..."

fdate=`date`
logdir="recon_output${qtask}"
errortxt=''
filesdir="${namestr}_files"

if [[ ! -e $filesdir ]]
then
 mkdir -p $filesdir
fi

	cat > $finishscript <<-EOF
		#!/bin/bash 
		set -x
		fdate=\`date\`

                  #check for error file from previous script
                  if [[ -e error_$mypid.txt ]]
                  then
                     errortxt="Error reported by sinogram routine .. \`cat error_$mypid.txt\`"
                     echo \$errortxt

                  fi
		#clean up 
		mkdir ${logdir}
                if [[ ! -e $filesdir ]]
                then
                   mkdir -p $filesdir
                fi
		mv ${jname}.* $qscript $finishscript d_${jname}_* ${logdir}
		#zip -rm ${logdir}.zip  ${logdir}
                #mv ${logdir}.zip ${filesdir}
                mv ${logdir} ${filesdir}

		#send a mail message when completed
		/usr/sbin/sendmail -t $USER <<-ENDM
			Subject: [QUEUE] I12 job $qtask from PID ${mypid} -- ${nchunks}-chunk reconstruction


			Diamond I12-JEEP  ${nchunks}-chunk  tomographic reconstruction finished...

                        \$errortxt

                        Using processor $processor qpflag $qpflag
			Start date: $sdate
			Finish date: \$fdate
                        Job name: ${jname}
                        Queue task: ${qtask}
                        Time stamp: ${timestamp}

			Working directory: \$PWD
			Input directory: ${chunkdir}
			Output directory: ${outdir}
			Output files will be in a folder labelled with the queue task ID
			Log files directory: ${logdir}
			Script: $0

			Parameters: $*

			The script process i.d. number was:
			$mypid

			Internal parameters in the script:

			 "timestamp = " $timestamp "yymmddhhmmss and nanoseconds"
			 "jname = " $jname	job name
			 "mypid = " $mypid	PID of submitting script 
			 "mydir = " $mydir	Working directory of submitting script
			 "chunkdir = " $chunkdir	 Location of the input data 
			 "outdir" = " $outdir	 Requested output location
			 "nchunks = " $nchunks	 Number of parallel chunks 
			 "cleanupflag = " $cleanupflag	 Option to remove intermediate files
			 "realflag = " $realflag	 Option for dry-run
			 "centreflag = " $centreflag	 Option for auto-centering
			 "Centre = " $Centre	 Specified center
			 "radflag = " $radflag	 Option to specify a centered R.O.I.
			 "Rad = " $Rad	 Radius (percentage) of the centered R.O.I.
			 "sliceflag = " $sliceflag	 Option to automatically reconstruct all available slices
			 "lastslice = " $lastslice	 Specified last slice to reconstruct

			The script version was: 
			$svnid

			The script repository was 
			$svnurl

                         This  e-mail was automatically generated by
                         the tomographic reconstruction batch processing system

		ENDM
                echo "Job ${jname} is finished" > finish_${jname}.txt
		set +x
EOF

  #sumbit the "finish" job
echo "Submitting the 'finish' job..."
finishname="f_${jname}"
qstring=`qsub -hold_jid $jname -q medium.q -cwd  -e $filesdir -o $filesdir -N "${finishname}" $finishscript`
retval=$?
echo "qstring = $qstring"
echo "Finishing script returned: " $retval

#get the assigned task number
oifs=$IFS
IFS=' 	.:'
qout=(${qstring})
qtask=${qout[2]}
echo "queue finish task number: ${qtask}"
echo "queue finish job name: ${finishname}"

IFS=$OIFS
if [[ $retval -ne 0 ]]
then 
  echo $qstring
  echo "ERROR: The 'finish' script returned a bad status for the queue submission."
  echo "ERROR: Please check the output of the queue submission above for problems."
  echo "ERROR: Since the script got this far, the tasks for the reconstruction were"
  echo "ERROR: probably submitted, but you will not receive email notification "
  echo "ERROR: and the post-reconstruction cleanup will not be performed."
else
echo "Your reconstruction task $qtask from script PID $mypid has been submitted." 
echo "You should receive email at address $USER when the reconstruction is finished." 
fi

if [[ $xflag -ne 0 ]]
then
set +x 
fi
