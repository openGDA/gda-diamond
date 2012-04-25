#!/bin/bash
for i in `ls /dls_sw/i12/software/tomography_scripts/`
do
   echo $i
   svn up $i  


done
