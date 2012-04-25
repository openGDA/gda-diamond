
source /dls_sw/i12/software/modules.sh
module add global/cluster

mkdir -p gathered_images
mkdir -p q_output
for i in */frame_10/centre_output/*_images 
do
      ibase=`basename $i`
      echo $ibase
      for j in 20  
      do
         ifname=`printf "$i/ctr_01360.30_%05d.tif" $j`
         ofname=`printf "gathered_images/${ibase}_%05d.tif" $j`
         echo $ifname $ofname
         #echo "convert -resize 25%x25% $ifname $ofname" | qsub -N rsz 
         echo "cp $ifname $ofname" | qsub  -e q_output -o q_output -N gather
      done

done
