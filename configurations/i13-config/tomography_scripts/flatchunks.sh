set -x
#print out a basic usage message
if [[ $# -lt 2 ]]
then
echo "flatchunks flatfolder scannumber [visitfolder]"
echo "split the flat field files in [flatfolder] into chunks and store with the scan [scannumber] sinograms"
echo "[visitfolder] defaults to the current working directory"
echo "temporary folder will be in [visitfolder]/spool"
exit
fi


#set up the folder paths

flatnumber=$1
scannumber=$2
if [[ $# -eq 3 ]]
then
visitfolder="/dls/i12/data/2010/$3"
else
   visitfolder=$PWD
fi

tmpfolder=$visitfolder/spool/flattmp/
mkdir -p $tmpfolder
flatimage=$visitfolder/processing/$flatnumber/flat.tif

#this line actually does all the work
convert -crop 4008x167  $flatimage $tmpfolder/flat%03d.tif

#move the resulting chunks into the correct folders
#unfortunately SGE queue doesn't like zero-indexed sequences ! 
#but ImageMagic does...

for i in {1..16}
do
#create a zero-indexed sequence for the auto-split filenames
(( zidx = $i - 1 ))
odir="$visitfolder/processing/$scannumber/sinograms/`printf "%03d" $i`/"
fname=`printf "flat%03d.tif" $zidx`
echo "$fname --> $odir"

#move to the 1-indexed folder for the sinograms input for queued reconstruction on the 16-tesla cluster
mv $tmpfolder/$fname $odir/flat.tif
done

set +x
