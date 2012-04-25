#!/bin/bash
#$Id: qstampstack.sh 214 2012-02-13 15:46:36Z kny48981 $
#set up some version tracking
svnid='$Id: qstampstack.sh 214 2012-02-13 15:46:36Z kny48981 $ '
svnurl='$URL: file:///home/kny48981/SVN/progs/tomo_recon_pipe/scripts/qstampstack.sh $ '
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
qqueue=high.q
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

#find out how many stacks are in the folder
nstacks=`ls -1 $inputfolder/${basename}*.tif | wc -l`
echo "$nstacks stacks"
#find out how many image are in a stack (first stack) 
nimages=`tiffdump $inputfolder/$basename.tif | grep Directory | wc -l`
echo "$nimages images in the first stack $basename.tif"

((nperjob = nstacks / $nproc))
echo "$nperjob stacks in $nproc jobs"
((rdr = nstacks - ($nproc * nperjob) ))
echo "$rdr stacks left over"
((bigjob = $nperjob + 1 ))
((nbigjob = $bigjob * $rdr))


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

mkdir -p $qfolder

mysecs=`date +%s`
echo $mysecs
myscript=` printf "${outputfolder}/runqunstack_%d_%d.sh" $$ $mysecs `
echo $myscript

cat >> $myscript <<-EOF
#!/bin/bash 
set -x
#add the modules required 
source /dls_sw/i12/modulefiles/modules.sh
module add i12
module add global/cluster
myjob=\$JOB_ID
tasknum=\${SGE_TASK_ID}  
#shift to zero index
((myidx=\$tasknum - 1))
if [[ \$myidx -lt $rdr ]]
then
   #need to do an extra job
   ((thisfirst = $bigjob * \$myidx))
   thisnum=$bigjob
   echo "btask,thisfirst: \$tasknum \$thisfirst"
else
   ((thisfirst =  $nbigjob + ((\$myidx - $rdr)* $nperjob ) ))
   echo "task,thisfirst: \$tasknum \$thisfirst"
   thisnum=$nperjob
fi
startsec=\`date +%s\`
startdate="\`date\`"
logname="\`printf "stamp_%03d_j%06d_t%02d.log" \$thisfirst \$myjob \${tasknum} \` "
tiff_stack_stamp  -i $inputfolder -b $basename  -o $outputfolder -f \$thisfirst -n \$thisnum  -S $nimages -v -s $outputfolder/\$logname -w /dev/null 
finishdate="\`date\`"
finishsec=\`date +%s\`
echo "started at \$startdate finished at \$finishdate"
(( elapsed = \$finishsec - \$startsec ))
echo "elapsed: \$elapsed on \$HOSTNAME"
EOF

#submit the script to the queue
declare -a qout
echo "submitting queue job at `date`"
if [[ gpuflag -eq 1 ]]
then
   gpustring="-P i12"
else
   gpustring=" "
fi
qstring=`qsub -v I12STRIPBYTES $gpustring  -t 1-$nproc -q $qqueue -e $qfolder -o $qfolder  -cwd -pe smp 4 -N "${jname}" "${myscript}" `
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



