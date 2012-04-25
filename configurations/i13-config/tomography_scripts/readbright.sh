#!/bin/bash 
#modules don't work for gda user
source /dls_sw/i12/modulefiles/modules.sh
#add the modules required 

module add i12

printusage(){
echo ""
echo "$0 "
echo "Read in a series of tiff files and calculate the "
echo "overall brightness for each image"
echo "averaging all pixels below the PCO time stamp (row 8)"
echo "and report the PCO time stamp, saving the results into"
echo "the specified file under the following headings:"
echo ""
echo "processingtime processingstamp imagedate filename imagetime brightness" 
echo ""
echo "imagedate is the date stored in the PCO image"
echo "imagetime is the microsecond value stored in the PCO image"
echo "brightness is the result of the averaging calculation"
echo ""
echo " usage:"
echo "`basename $0` -f first  -l last -s step -o outputfolder -i inputfolder"
echo " -f first projection"
echo " -l last projection"
echo " -s step between projections"
echo " -i folder containing the projection data "
echo " -o folder in which to place the output file"
echo " -N name of output text list file"
}

if [[ $# -le 1 ]]
then 
printusage;
exit;
fi

first=0
last=10000
step=100
name="list.txt"
indir="."
outdir="."

while getopts "i:f:l:s:ho:N:" flag
do
  #echo "$flag" $OPTIND $OPTARG
  case $flag in
  "N")
  echo "output filename:" $OPTARG
  name=$OPTARG
  ;;
  "i")
  echo "input folder:" $OPTARG
  indir=$OPTARG
  ;;
  "f")
  echo "first filenumber:" $OPTARG
  first=$OPTARG
  ;;
  "l")
  echo "last filenumber:" $OPTARG
  last=$OPTARG
  ;;
  "s")
  echo "filenumber step:" $OPTARG
  step=$OPTARG
  ;;
  "o")
  echo "output folder" $OPTARG
  outdir=$OPTARG
  oflag=1
  ;;
  "h")
  printusage;
  exit
  ;;
  "?")
  printusage;
  exit
  ;;
  esac
done

mydir=$PWD
cd $indir
fullindir=$PWD
cd $mydir

if [[ ! -d $outdir ]]
then
   mkdir -p $outdir
fi
if [[ ! -d $outdir ]]
then
   echo "ERROR Output folder $outdir could not be created! "
   exit
fi


echo "processing files from $fullindir on  `date` " 
echo "processing files from $fullindir on  `date` " >> $outdir/$name
echo "ptime pstamp imagedate filename imagetime brightness" >> $outdir/$name

declare -a oput
for ((f=$first;f<=$last;f+=$step))
   do
      fnum=$f
      fname=`printf "%s/p_%05d.tif" $indir $fnum`
      pdate=`date`
      oput=(`tifbright $fname`)
      b=${oput[11]} # brightness
      d=${oput[14]} # date string
      t=${oput[13]} # time stamp in microseconds

      ptime=${oput[0]}
      pstamp=${oput[1]}

      echo `date` $fname $ptime 

      bright=`echo $b | sed -e's/\..*//'`
      echo "$pdate $ptime $pstamp $d ${oput[3]} $t $b " >> $outdir/$name
   done

