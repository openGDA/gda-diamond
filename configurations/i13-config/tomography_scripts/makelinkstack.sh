#!/bin/bash
framenum=0
firstscan=1
nscans=7
nproj=1800
nflat=21
realflag=1
vflag=0
indir="./"
outdir="./"

printusage(){
   echo " usage:"
   echo "$0 -f flatnum  -i input -o output -s nscans -p nprojections [ -v ] [ -d] "
   echo " -f number of flat field images between scans"
   echo " -F First scan number to process"
   echo " -p projections per scan"
   echo " -s number of scans"
   echo " -d dryrun (do not move files)" 
   echo " -v verbose messages " 
}
if [[ $# -le 1 ]]
then
   echo $#
   printusage;
   exit
fi

while getopts "s:p:F:f:hi:o:dv" flag
do
  echo "$flag" $OPTIND $OPTARG
  case $flag in
  "s")
  echo "scans in montage" $OPTARG
  nscans=$OPTARG
  ;;
  "p")
  echo "projections per scan" $OPTARG
  nproj=$OPTARG
  ;;
  "F")
  echo "First scan to process" $OPTARG
  firstscan=$OPTARG
  ;;
  "f")
  echo "number of flatfields between" $OPTARG
  nflat=$OPTARG
  ;;
  "i")
  echo "input folder" $OPTARG
  indir=$OPTARG
  iflag=1
  ;;
  "o")
  echo "output folder" $OPTARG
  outdir=$OPTARG
  oflag=1
  ;;
  "d")
  echo "dryrun" 
  realflag=0
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

if [[ ! -d $indir ]]
then
   echo "ERROR: input directory $indir not usable!"
   exit
fi

if [[ ! -d $outdir ]]
then
   mkdir -p $outdir
fi



mydir=$PWD
cd $indir
inpath=$PWD
cd $mydir
cd $outdir 
outpath=$PWD
echo $mydir $inpath $outpath

((framenum = ($firstscan - 1) * ($nflat + $nproj+1) ))
((sframe = ($firstscan - 1) * ($nflat + $nproj+1) + $nflat ))
((lastframe = ($nflat + $nproj+1)*($nscans) + (2*$nflat) ))

echo "first (flat$firstscan)  frame will be " $framenum
echo "first (scan$fisrtscan)  frame will be " $sframe
echo "last frame will be " $lastframe

for (( scannum=$firstscan;scannum<=$nscans;scannum++ ))
do
   echo "scan $scannum"
   mkdir -p $outpath/scan$scannum
   mkdir -p $outpath/flat$scannum

   echo "flatfield $scannum starting at $framenum"

#link the flatfield (before each scan ) files
   for (( flatframe=0;flatframe<$nflat;flatframe++))
   do
      infname=`printf "p_%05d.tif" $framenum`
      fname=`printf "p_%05d.tif" $flatframe`
      if [[ vflag -eq 1 ]]
      then
         echo "$inpath/$infname $outpath/flat$scannum/$fname"
      fi

      if [[ realflag -eq 1 ]]
      then
         ln -fs $inpath/$infname $outpath/flat$scannum/$fname
      fi
      (( framenum++ ))
   done

   echo "data $scannum starting at $framenum"

#link the scan files
   for ((scanframe =0; scanframe <= $nproj; scanframe++))
   do
      infname=`printf "p_%05d.tif" $framenum`
      fname=`printf "p_%05d.tif" $scanframe`
      if [[ vflag -eq 1 ]]
      then
      echo "$inpath/$infname $outpath/scan$scannum/$fname"
   fi
      if [[ realflag -eq 1 ]]
      then
         ln -fs $inpath/$infname $outpath/scan$scannum/$fname
      fi
      (( framenum++ ))
   done
done

#flat after
   echo "flatfield after ...  $scannum starting at $framenum"

   mkdir -p $outpath/flat$scannum
   for (( flatframe=0;flatframe<$nflat;flatframe++))
   do
      infname=`printf "p_%05d.tif" $framenum`
      fname=`printf "p_%05d.tif" $flatframe`
      if [[ vflag -eq 1 ]]
      then
         echo "$inpath/$infname $outpath/flat$scannum/$fname"
      fi
      if [[ realflag -eq 1 ]]
      then
        ln -fs $inpath/$infname $outpath/flat$scannum/$fname
      fi
      (( framenum++ ))
   done

#dark after
   echo "darkfield after ...  $scannum starting at $framenum"
   mkdir -p $outpath/dark$scannum
   for (( flatframe=0;flatframe<$nflat;flatframe++))
   do
      infname=`printf "p_%05d.tif" $framenum`
      fname=`printf "p_%05d.tif" $flatframe`
      if [[ vflag -eq 1 ]]
      then
          echo "$inpath/$infname $outpath/dark$scannum/$fname"
      fi
      if [[ realflag -eq 1 ]]
      then
         ln -fs $inpath/$infname $outpath/dark$scannum/$fname
      fi
      (( framenum++ ))
   done
   (( ll = $framenum - 1 ))
   echo "finished  at $ll"




