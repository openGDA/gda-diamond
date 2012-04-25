#!/bin/bash 
declare -a vals
if [[  ! -d fixed ]]
then
   mkdir fixed
fi

frame=0 #the correct sequence number 
file=0  #the actual file number 
segctr=0
hole=0
framest=1
nlines=0
while read a
do


   vals=($a)
   ost=${vals[0]}
   newst=${vals[1]}
   echo "ost $ost newst $newst"

   echo "nlines $nlines"
   ((nlines ++))
#   if [[ nlines -eq 5 ]]
#   then
#   exit
#   fi


   if [[ $ost -gt 0 ]] #ignore first frame error
   then
      echo " $a : ost is greater than 0 "

      #### non hole segment
      if [[ $newst -le $ost ]]
      then
         echo " $a : newst is less than ost"
            if [[ $newst -eq 1 ]]
               then #must be a segment boundary  
                  echo "segment boundary approaching " 
                framest=$frame
                hole=0

            for ((i=$framest;i<=ost;i++))
            do
               echo "$a : i $i frame $frame file $file"
               oldname=`printf "p_%05d.tiff" $file`
               newname=`printf "p_%05d.tiff" $frame`
               ((frame++))
               ((file++))
               ((segctr++))
               echo "$a linking : oldname $oldname newname $newname"
               ln -s $PWD/projections/$oldname $PWD/fixed/$newname
            done #end loop segment with no hole
            else
               echo "$a : Unusual Sequence" $ost $newst
            fi
      #### end non hole segment
      else
         echo " $a : newst is greater than ost"
            framest=$frame
            hole=1
            echo " $a : must be a hole  $framest"
      fi

            segstart=segctr
            for ((i=segstart;i<=ost;i++))
            do
               echo "$a : i $i frame $frame file $file"
               oldname=`printf "p_%05d.tiff" $file`
               newname=`printf "p_%05d.tiff" $frame`
               ((frame++))
               ((file++))
               ((segctr++))
               echo "$a linking : oldname $oldname newname $newname"
               ln -s $PWD/projections/$oldname $PWD/fixed/$newname
            done #end loop before hole

            if [[ hole -eq 1 ]]
            then
               #create an averaged tiff for filling in the holes
               (( ofile = file - 1 ))
               lframe=`printf "p_%05d.tiff" $file`
               rframe=`printf "p_%05d.tiff" $ofile`
               rm -f newfile.tiff
               echo "$a : making an average file "
               convert -average +matte projections/$rframe projections/$lframe newfile.tiff

               #copy the averaged tiff into the missing files 
               echo "looping from  $ost +1 to $newst"
               for ((i=$ost+1;i<$newst;i++))
               do
                  oldname="newfile.tiff"
                  newname=`printf "p_%05d.tiff" $frame`
                  echo "$a: copying oldname $oldname newname $newname"
                  cp $PWD/$oldname $PWD/fixed/$newname
                  ((frame++))
                  ((segctr++))
               done #end loop in hole
               rm  -f newfile.tiff
            else
              #reached segment boundary
              echo "segment boundary!"
              segctr=0

            fi
         fi

   done # end reading the input file

   #continue after all the holes are filled int
   framest=$frame;
   oldname=`printf "p_%05d.tiff" $file`

   while [[ -f $PWD/projections/$oldname ]]
   do
      oldname=`printf "p_%05d.tiff" $file`
      newname=`printf "p_%05d.tiff" $frame`
      ((frame++))
      ((file++))
      echo "$a: linking oldname $oldname newname $newname"
      ln -s $PWD/projections/$oldname $PWD/fixed/$newname
      oldname=`printf "p_%05d.tiff" $file`
   done
