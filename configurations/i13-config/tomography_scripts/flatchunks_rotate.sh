set -x
#print out a basic usage message
if [[ $# -ne 2 ]]
then
echo "flatchunks [flatfnumber] [scannumber]"
echo "split the flat field files in [flatfnumber] into chunks and store with the scan [scannumber] sinograms"
exit
fi


#set up the folder paths

flatnumber=$1
scannumber=$2
visitfolder="/dls/i12/data/2010/ee2213-1"
tmpfolder=$visitfolder/spool/flattmp/
mkdir -p $tmpfolder
flatimage=$visitfolder/$flatnumber/projections/min_flat.tif
#rflatimage=$tmpfolder/r_00000.tif
#convert -median 1 -rotate 0.17 +matte $flatimage $rflatimage
#this line actually does all the work
convert -rotate 0.15 -crop 4015x167 -median 1 +matte $flatimage $tmpfolder/flat%03d.tif

#move the resulting chunks into the correct folders
#unfortunately SGE queue doesn't like zero-indexed sequences ! 
#but ImageMagic does...

for i in {1..16}
do
#create a zero-indexed sequence for the auto-split filenames
(( zidx = $i - 1 ))
odir="$visitfolder/processing/$scannumber/rsinograms/`printf "%03d" $i`/"
fname=`printf "flat%03d.tif" $zidx`
echo "$fname --> $odir"

#move to the 1-indexed folder for the sinograms input for queued reconstruction on the 16-tesla cluster
mv $tmpfolder/$fname $odir/flat.tif
done

set +x
