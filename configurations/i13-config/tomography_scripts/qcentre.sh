#!/bin/bash
#$Id: qcentre.sh 214 2012-02-13 15:46:36Z kny48981 $
#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh
#add the modules required 
module add /dls_sw/i12/modulefiles/local-64
module add global/cluster >& /dev/null

nsteps=20
step=1
cstart=1985
slicestart=500
nslices=1
slicestep=167
gpu=0

if [[ $# -lt 1 ]]
then
   echo "$0 usage:"
   echo "$0 cstart nsteps stepsize [slice-start nslices slicestep]"
   echo " defaults:  nsteps $nsteps stepsize $step slice-start $slicestart nslices $nslices slicestep $slicestep"
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
   slicestart=$4
fi

if [[ $# -ge 5 ]]
then
   nslices=$5
fi


if [[ $# -ge 6 ]]
then
   slicestep=$6
fi


myjob=$$
echo "The JOB NUMBER is $myjob"
echo " inputs:  nsteps $nsteps stepsize $step slice-start $slicestart  nslices $nslices slicestep $slicestep"

umask -S u=rwx,g=rwx,o=rx 

settingspath="./ctr/qc_output_$myjob"
outpath=qc_job_$myjob
jpgpath=jpegs_$myjob

if [[ -e $settingspath ]]
then
   echo "Warning: settings folder $settingspath exists already!"
   echo "If it was written by a different user then the job may fail!"
fi

mkdir -p $settingspath


for (( nn=1; nn <= $nslices; nn++ ))
do
   (( slicenum = ( ($nn-1) * $slicestep ) + $slicestart ))
   echo "slicenum: $slicenum"
dfolder="./sinograms/" 

if [[ ! -e $dfolder ]]
then
   echo "sinogram folder $dfolder not found"
   exit
fi

ifolder="./ctr/$outpath"
jfolder="./ctr/$jpgpath"


if [[ ! -e $jfolder ]]
then
   mkdir -p $jfolder
fi

if [[ ! -e $ifolder ]]
then
   mkdir -p $ifolder
fi
   sfile="${settingspath}/settings_tmp$nn.in"
   echo $sfile
   cp settings_ctr.in $sfile
   cat >> $sfile <<EOF

input_file_path = $dfolder
input_file_prefix = sino_
output_file_path = $ifolder 
dark_noise_file = ./dark/dark.tif
flat_field_file = ./flat/flat.tif
slices_first = $slicenum 
slices_last = $slicenum

EOF

#    image_centre = $ctr
# __end__
cat > runqctr$slicenum.qsh <<EOF
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
echo "slice = $sliceum ctr = \$ctr"
cp $settingspath/settings_tmp$nn.in $settingspath/settings_\${ctr}_$slicenum.in
echo "image_centre = \$ctr" >> $settingspath/settings_\${ctr}_$slicenum.in
echo "output_file_prefix = ${pfx}_ctr\$ctr"  >> $settingspath/settings_\${ctr}_$slicenum.in
echo "__end__" >> $settingspath/settings_\${ctr}_$slicenum.in

dt64c -c $settingspath/settings_\${ctr}_$slicenum.in -o $settingspath/out_\${ctr}_$slicenum.txt -G \$gpu
for i in $ifolder/${pfx}_ctr\$ctr*.tif
do
   bname=\`basename \$i .tif\`
   convert -resize 25%x25% \$i $jfolder/\${bname}.jpg
done
EOF
qsub -P i12 -q high.q -N qcentre_$slicenum -e $settingspath -o $settingspath -t 1-$nsteps -pe smp 4 -cwd runqctr$slicenum.qsh
done
#(cd $ifolder; for i in *.tif; do echo $i; convert $i `basename $i .tif`.jpg ; done; zip jpegs.zip *.jpg )


