#!/bin/bash
#$Id: qunstack-allq.sh 214 2012-02-13 15:46:36Z kny48981 $
#set up some version tracking
svnid='$Id: qunstack-allq.sh 214 2012-02-13 15:46:36Z kny48981 $ '
svnurl='$URL: file:///home/kny48981/SVN/progs/tomo_recon_pipe/scripts/qunstack-allq.sh $ '
#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh
#add the modules required 
module add /dls_sw/i12/modulefiles/local-64
module add global/cluster

#initialize some default values
sdate=`date`
mypid=$$
mydir=$PWD
nchunks=16
inputfolder="."
outputfolder="."

printusage(){
echo " usage:"
echo "$0 [ etc. etc.]"
echo "-b <base-name>"
echo "-i <input-folder>"
echo "-o <output-folder>"

}

#print usage message if no options are selected
if [[ $# -le 1 ]]
then 
printusage;
exit;
fi

nproc=16;
qqueue=medium.q
jname=unstack
qfolder="$outputfolder/queue_output"
gpuflag=1 #default

echo "queue ouptut is saved in $qfolder"

#parse the options
while getopts "i:o:b:vGgh" flag
do
  case $flag in
  "g")
  echo "not GPU"
  gpuflag=0
  ;;
  "G")
  echo "GPU"
  gpuflag=1
  ;;
  "b")
  echo "base name " $OPTARG
  basenamestring=$OPTARG
  basename=`basename $basenamestring .tif`
  echo "base name " $basename
  ;;
  "i")
  echo "input folder" $OPTARG
  inputfolder=$OPTARG
  ;;
  "o")
  echo "output folder" $OPTARG
  outputfolder=$OPTARG
  oflag=1
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

#find out how many image are in a stack (first stack) 
nimages=`tiffdump $inputfolder/$basename.tif | grep Directory | wc -l`
echo "$nimages images in the first stack $basename.tif"
mynum=0;

if [[ ! -e $outputfolder ]]
then
   mkdir -p $outputfolder
else
   if [[ ! -d $outputfolder ]]
   then
      echo "ERROR $outputfolder exists and is not a directory"
      exit
   fi
fi

if [[ gpuflag -eq 1 ]]
then
   gpustring="-P i12"
else
   gpustring=" "
fi

mkdir -p $qfolder


for mystack in $inputfolder/$basename*.tif
do
   echo $mynum $mystack

   mysecs=`date +%s`
   echo $mysecs
   myscript=` printf "runqunstack_%d_%d_n%04d.sh" $$ $mysecs $mynum `
   echo $myscript

   cat >> $myscript <<-EOF
#!/bin/bash 
set -x
#add the modules required 
source /dls_sw/i12/modulefiles/modules.sh
module add i12
myjob=\$JOB_ID

startsec=\`date +%s\`
startdate="\`date\`"
logname="\`printf "stamp_%03d_j%06d.log" $mynum \$myjob  \` "
tiff_stack_stamp  -i $inputfolder -b $basename  -o $outputfolder -f $mynum -n 1  -S $nimages -v -s \$logname -w /dev/null -x 
finishdate="\`date\`"
finishsec=\`date +%s\`
echo "started at \$startdate finished at \$finishdate"
(( elapsed = \$finishsec - \$startsec ))
echo "elapsed: \$elapsed on \$HOSTNAME"
EOF

   #submit the script to the queue
   declare -a qout
   echo "submitting queue job at `date`"
   set -x
   qstring=`qsub -v I12STRIPBYTES $gpustring  -q $qqueue -e $qfolder -o $qfolder  -cwd  -N "${jname}" "${myscript}" `
   retval=$?
   set +x
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
   echo "stack $mystack: queue task number: ${qtask}"
   IFS=$oifs

   ((mynum++))
done

