
exp=0.04
nproj=3000

declare -a horiz
declare -a vert
horiz[0]=-19.261
horiz[1]=-19.261
horiz[2]=-19.261
horiz[3]=-19.261
horiz[4]=-19.261
horiz[5]=2.944
horiz[6]=2.944
horiz[7]=2.944

vert[0]=0.53
vert[1]=5.73
vert[2]=10.93
vert[3]=16.13
vert[4]=21.33

vert[5]=0.53
vert[6]=5.73
vert[7]=10.93



for iter in {2..9}
do
echo "     "
echo "Running iteration $iter"

for step in {0..7}
   do
      height=${vert[$step]}
      hpos=${horiz[$step]}
      scanname=`printf "cheirolepis_%d_h%f_v%f_i%d" $step ${horiz[$step]} ${vert[$step]} $iter`

      echo "$step: moving to vertical $hpos  position $step"
      caput -cw 300  BL12I-MO-TAB-02:ST1:Y3.VAL ${height}
      echo "repeat $step: reached vert $height  position $step"
      echo "$step: moving to  horizontal $hpos  position $step"
      caput -cw 300  BL12I-MO-TAB-02:ST1:X.VAL ${hpos}
      echo "$step: reached horiz $hpos  position $step"
      echo "$step: scanning $scanname"
      fossil_apr_2012.py $scanname $nproj $exp

   done
done


dark.py dfcheirolepis 25 $exp 0 1
