#!/bin/bash 
#$Id: recon_array.sh 86 2010-02-15 17:46:32Z kny48981 $
timestamp=`date +%y%m%d%H%M%S%N`
#set up some version tracking
svnid='$Id: recon_array.sh 86 2010-02-15 17:46:32Z kny48981 $ '
svnurl='$URL: file:///home/kny48981/SVN/progs/tomo_recon_pipe/scripts/recon_array.sh $ '
source /etc/profile.d/modules.sh
#add the modules required 
module add /dls_sw/i12/modulefiles/local-64
module add global/cluster

#initialize some default values
sdate=`date`
mypid=$$
mydir=$PWD
ifile=${mydir}/settings.in 
chunkdir=${mydir}/ch #folder containing the data 
nchunks=8
autochunk=1
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

printusage(){
echo " usage:"
echo "$0 -n nchunks -i input -o output -s slices -C center -R radius [-c -S]"
echo " -n nchunks - how many of the available chunks to reconstruct"
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
echo " -S bypass sinogram creation "
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
namestr=''
uniqueflag=0
suffixflag=0

while getopts "U:O:C:EGH:I:J:N:R:STZ:b:cdf:hi:j:l:n:o:p:s:v:w:xz:" flag
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
  echo "Job name "
  namestr=$OPTARG
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
  "n")
  echo "nchunks" $OPTARG
  nchunks=$OPTARG
  autochunk=0
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

if [[ $uniqueflag -ne 0 ]]
then
mypid=$uniqueid
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

#check if its a dry-run
if [[ $realflag != 1 ]]
then
   exit
fi

#calculate the sinogram size
(( sinolen = $ht * $wd ))

#count the chunks
if [[ $autochunk -eq 1 ]]
then
echo "Autochunk"
   cd $chunkdir
   nchunks=`ls -ld [0-9]* | grep '^d' | wc -l`
   cd $mydir
fi

   #create a queue script
   cat > runq.qsh <<-EOF
#!/bin/bash 
set -x

#add the modules required to run Valeriy's code
source /etc/profile.d/modules.sh
module add /dls_sw/i12/modulefiles/local-64
module add /dls_sw/i12/modulefiles/intel-32
module add global/cluster
myjob=\$JOB_ID
tasknum=\${SGE_TASK_ID}  
i=\`printf "%03d" \${tasknum}\`
ddir=${chunkdir}/\$i

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
cat >> runq.qsh <<-EOF
	CEN="\${tifcen}.5"
	EOF
	
else
cat >> runq.qsh <<-EOF
	CEN=$Centre
	EOF
	
fi

echo "sliceflag = $sliceflag "
if [[ sliceflag -eq 1 ]]
then
echo "using input slice"
   cat >> runq.qsh <<-EOF
   SLI=$lastslice
EOF

else
echo "using auto last slice"
cat >> runq.qsh <<-EOF
   SLI=$ht
EOF
fi


cat >> runq.qsh <<-EOF
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

#swap the control parameters for Valeriy's reconstruction
cd $mydir
sed -e "s/^input_file_prefix.*$/input_file_prefix = c\${i}_s /" \
       -e "s/^output_file_prefix.*$/output_file_prefix = c\${i}_sol/" \
       -e "s|^output_file_path.*$|output_file_path = \${odir}|" \
       -e "s/^image_centre.*$/image_centre = \$CEN /" \
       -e "s/^slices_last.*$/slices_last = \$SLI /" \
       -e "s/^backprojection_radius2_value.*$/backprojection_radius2_value = ${Rad} /" \
       ${ifile} > \${ddir}/settings_\${i}_${uniqueid}.in

#go back to the data directory
cd \${ddir}
EOF


#do the reconstruction using cpu code
if [[ gpuflag -eq 0 ]]
then
processor=" CPU "
qqueue="medium.q" 
cat >> runq.qsh <<-EOF
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
qqueue="medium.q" 
cat >> runq.qsh <<-EOF
mycuda=0
cudafound=0
tries=0
mylockdir=/dev/shm/tomo-i12/lock
mydate=\`date\`
mkdir -p \$mylockdir
#try to acquire a lock representing one of the cuda cards
while [[ \$cudafound -eq 0 ]]
do

   for mycuda in 0 1 2 3
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
          echo "Didn't get lock on \$mylockf"
       fi
   done
    if [[ \$cudafound -eq 0 ]]
    then
       (( tries ++ ))
       if [[ \$tries -gt 10 ]]
       then
            echo "Could not find an availalble CUDA device!"
            exit
       fi
     sleep 5
     fi

done


echo "using cuda \$mycuda " >> \$dfile
realcuda=\$mycuda

if [[ \$mycuda -eq 2 ]]
then
realcuda=0
fi

if [[ \$mycuda -eq 3 ]]
then
realcuda=1
fi

echo "using realcuda \$mycuda " >> \$dfile
echo "before reconstruction" >> \$dfile
date >> \$dfile
cat > input.dat <<-ENDI
settings_\${i}_${uniqueid}.in
out_\${i}_${uniqueid}.txt
ENDI
#run the reconstruction routine
dt64 \$realcuda  >& \${odir}/recon_\$i.out  
recretval=\$?
echo "reconstruction routine returned \$recretval" >> \$dfile
mv out_\${i}_${uniqueid}.txt \$odir
mv settings_\${i}_${uniqueid}.in \$odir
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
cat >>runq.qsh <<-EOF
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
qstring=`qsub ${qpflag} -t 1-$nchunks -q $qqueue $holdstring  -cwd -pe smp 2 -N "${jname}" runq.qsh`
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
	cat > finishq.qsh <<-EOF
		#!/bin/bash 
		set -x
		fdate=\`date\`

                  #check for error file from previous script
                  if [[ -e error_$mypid.txt ]]
                  then
                     errortxt="Error reported by sinogram routine .. `cat error_$mypid.txt`"
                     echo \$errortxt

                  fi
		#clean up 
		mkdir ${logdir}
                if [[ ! -e $filesdir ]]
                then
                   mkdir -p $filesdir
                fi
		mv ${jname}.* runq.qsh finishq.qsh d_${jname}_* ${logdir}
		zip -rm ${logdir}.zip  ${logdir}
                mv ${logdir}.zip ${filesdir}

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
		set +x
EOF

  #sumbit the "finish" job
echo "Submitting the 'finish' job..."
finishname="f_${jname}"
qstring=`qsub -hold_jid $jname -q medium.q -cwd -N "${finishname}" finishq.qsh`
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
