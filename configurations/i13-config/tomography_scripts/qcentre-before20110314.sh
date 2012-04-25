#!/bin/bash
#$Id: qcentre.sh 116 2010-08-31 15:33:46Z kny48981 $
#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh
#add the modules required 
module add /dls_sw/i12/modulefiles/local-64
module add global/cluster >& /dev/null

nsteps=20
step=1
cstart=1985
chunkstart=5
chunkstop=5
slicenum=25
gpu=0

if [[ $# -lt 1 ]]
then
   echo "$0 usage:"
   echo "$0 cstart nsteps stepsize [chunk-start chunk-stop slicenumber]"
   echo " defaults:  nsteps $nsteps stepsize $step chunk-start $chunkstart chunk-stop $chunkstop slicenumber $slicenum"
   exit
fi

if [[ $# -ge 1 ]]
then
   cstart=$1
fi

if [[ $# -ge 2 ]]
then
   nsteps=$2
fi

if [[ $# -ge 3 ]]
then
   step=$3
fi


if [[ $# -ge 4 ]]
then
   chunkstart=$4
fi

if [[ $# -ge 5 ]]
then
   chunkstop=$5
fi


if [[ $# -ge 6 ]]
then
   slicenum=$6
fi


myjob=$$
echo "The JOB NUMBER is $myjob"
echo " inputs:  nsteps $nsteps stepsize $step chunk-start $chunkstart chunk-stop $chunkstop slicenumber $slicenum"

umask -S u=rwx,g=rwx,o=rx 

settingspath="./ctr/qc_output_$myjob"
outpath=qc_job_$myjob

if [[ -e $settingspath ]]
then
   echo "Warning: settings folder $settingspath exists already!"
   echo "If it was written by a different user then the job may fail!"
fi

mkdir -p $settingspath


for (( chunknum=$chunkstart; chunknum <= chunkstop; chunknum++ ))
do
   echo "chunknum: $chunknum"

dfolder=`printf "./sinograms/%03d/" $chunknum`

if [[ ! -e $dfolder ]]
then
   echo "sinogram folder $dfolder not found"
   exit
fi

ifolder="./ctr/$outpath"

pfx=`printf "c%03d" $chunknum`

if [[ ! -e $ifolder ]]
then
   mkdir -p $ifolder
fi
   sfile="${settingspath}/settings_tmp$chunknum.in"
   echo $sfile
   cp settings_ctr.in $sfile
   cat >> $sfile <<EOF

input_file_path = $dfolder
input_file_prefix = ${pfx}_s
output_file_path = $ifolder 
dark_noise_file = $dfolder/dark.tif
flat_field_file = $dfolder/flat.tif
slices_first = $slicenum 
slices_last = $slicenum

EOF

#    image_centre = $ctr
# __end__
cat > runqctr$chunknum.qsh <<EOF
set -x
umask -S u=rwx,g=rwx,o=rx
uname -a
tasknum=\$SGE_TASK_ID
#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh
#add the modules required 
module add /dls_sw/i12/modulefiles/local-64
module add global/cluster
echo \${tasknum} $cstart $step  
c="\`echo \$tasknum | awk '{print \$0 }'\`"
echo "c=\$c"
ctr=\`echo \${tasknum} $cstart $step  | awk "{ printf \"%07.2f\", ($cstart + ( \$tasknum - 1 ) * $step )}i" \`
(( gpu = \$tasknum - 2 * ( \$tasknum / 2 ) ))
echo "tasknum = \$tasknum"
echo "gpu = \$gpu"
echo "chunk = $chunknum ctr = \$ctr"
cp $settingspath/settings_tmp$chunknum.in $settingspath/settings_\${ctr}_$chunknum.in
echo "image_centre = \$ctr" >> $settingspath/settings_\${ctr}_$chunknum.in
echo "output_file_prefix = ${pfx}_ctr\$ctr"  >> $settingspath/settings_\${ctr}_$chunknum.in
echo "__end__" >> $settingspath/settings_\${ctr}_$chunknum.in

/home/kny48981/progs/tomo_recon_pipe/tesla/dt64 -c $settingspath/settings_\${ctr}_$chunknum.in -o $settingspath/out_\${ctr}_$chunknum.txt -G \$gpu
EOF
qsub -P i12 -q high.q -N qcentre_$chunknum -e $settingspath -o $settingspath -t 1-$nsteps -pe smp 4 -cwd runqctr$chunknum.qsh
done
#(cd $ifolder; for i in *.tif; do echo $i; convert $i `basename $i .tif`.jpg ; done; zip jpegs.zip *.jpg )


