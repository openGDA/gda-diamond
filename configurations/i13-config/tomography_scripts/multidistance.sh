
scriptfolder=/dls_sw/i12/software/tomography_scripts
tomoscript=tomo_scan.py

declare -a campos

campos[1]=320
campos[2]=1000
campos[3]=1200
campos[4]=1800
campos[5]=2120
campos[6]=2170
campos[7]=2220




   
   for p in {1..7}
      do
     echo "$scriptfolder/$tomoscript smallballm3_${campos[$p]} 6000 1.2 "
     caput -c -w 600  "BL12I-MO-TAB-03:MOD1:Z.VAL" ${campos[$p]}
     $scriptfolder/$tomoscript smallballm3_${campos[$p]}  6000 1.2
    done

