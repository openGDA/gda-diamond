#!/bin/bash 
#$Id: remove_cuda_locks_q.sh 214 2012-02-13 15:46:36Z kny48981 $
timestamp=`date +%y%m%d%H%M%S%N`
#set up some version tracking
svnid='$Id: remove_cuda_locks_q.sh 214 2012-02-13 15:46:36Z kny48981 $ '
svnurl='$URL: file:///home/kny48981/SVN/progs/tomo_recon_pipe/scripts/remove_cuda_locks_q.sh $ '
source /etc/profile.d/modules.sh
#add the modules required 
module add /dls/i12/modulefiles/local-64
module add global/cluster

#submit the script to the queue
declare -a qout
mylockdir=/dev/shm/tomo-i12/lock
qstring=`echo "rm ${mylockdir}/cuda*" | qsub -P i12 -t 1-8 -q medium.q  -cwd -pe smp 8 -N "cuda-unlock" `
retval=$?
echo $qstring
echo "Script returned: " $?
if [[ $retval -ne 0 ]]
then 
  echo "ERROR: The script returned a bad status for the queue submission."
  echo "ERROR: Please check the output of the queue submission above for problems."
  exit
fi
