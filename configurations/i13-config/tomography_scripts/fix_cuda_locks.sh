#!/bin/bash 
#$Id: recon_cpu_array.qsh 69 2010-01-18 17:36:51Z kny48981 $
timestamp=`date +%y%m%d%H%M%S%N`
#set up some version tracking
svnid='$Id: recon_cpu_array.qsh 69 2010-01-18 17:36:51Z kny48981 $ '
svnurl='$URL: file:///home/kny48981/SVN/progs/tomo_recon_pipe/scripts/recon_cpu_array.qsh $ '
source /etc/profile.d/modules.sh
#add the modules required 
module add /dls/i12/modulefiles/local-64
module add global/cluster

#submit the script to the queue
declare -a qout
mylockdir=/dev/shm/tomo-i12/lock
qstring=`echo "chmod -R a+rwX ${mylockdir} && ls -lR ${mylockdir}" | qsub -P i12 -t 1-8 -q medium.q  -cwd -pe smp 8 -N "cuda-fix" `
retval=$?
echo $qstring
echo "Script returned: " $?
if [[ $retval -ne 0 ]]
then 
  echo "ERROR: The script returned a bad status for the queue submission."
  echo "ERROR: Please check the output of the queue submission above for problems."
  exit
fi
