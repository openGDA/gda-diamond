

visit="ee7076-1"
rootfolder="/dls/i12/data/2011/"
rawfolder="processing/rawdata"
reconfolder="processing/recon"
mywd=`pwd`

echo "Using : "
echo "raw data in $rootfolder/$visit/$rawfolder/"
echo "reconstruction into $rootfolder/$visit/$reconfolder/"
if [[ $# -lt 1 ]]
then
   echo $#
   echo "Usage: $0 [sample-name]"
   exit

fi
sname=$1


   echo $sname
   pfolder=$rootfolder/$visit/$rawfolder/$sname/projections
   ffolder=$rootfolder/$visit/$rawfolder/ff$sname/projections
   rfolder=$rootfolder/$visit/$reconfolder/$sname
   mkdir $rfolder
   #ls $pfolder | tail
   ls $ffolder | tail
   # average the flat field file
   echo "averaging the flat field file"
   cd $rfolder
   flat_capav -i $ffolder -o flat -a 24
   cp $mywd/settings.xml $rfolder

   datestring=`date +"%m%d%H%M%S"`
   jstring=`/dls_sw/i12/software/tomography_scripts/sino_listener.py  -J $sname -U $datestring -i $pfolder  -l 1140 -p 6000 -n 14 | tee out$datestring.txt |  grep "JOB NAME IS"`
   rv=$?
   echo "return value" $rv
   declare -a jobline
   echo "Submitting the job for the sinograms"
   echo "JSTRING:" $jstring
   jobline=($jstring)
   nm=${jobline[3]}
   echo "HOLDNAME: " $nm

   set -x
   echo "Submitting the job for the test slice -- held in the queue for the sinograms to finish"
   qcentrexml.py 2083 28 0.5  500 1 1 $nm
   #recon_arrayxml.py -I settings.xml -C 2090.6 -p 6000 -n 14 -F 100 -L 2000 -S 50 -H $nm -J $sname
   set +x


