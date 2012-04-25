#!/bin/bash

caput "BL12I-PS-SHTR-02:CON" 0
/dls_sw/i12/software/tomography_scripts/flat_tif_areadetector.py ffBalls130_10s 25 10
/dls_sw/i12/software/tomography_scripts/tomo_tif_areadetector.py Balls130_10s 6000 10
/dls_sw/i12/software/tomography_scripts/flat_tif_areadetector.py faBalls130_10s 25 10
caput "BL12I-PS-SHTR-02:CON" 1
/dls_sw/i12/software/tomography_scripts/flat_tif_areadetector.py dfBalls130_10s 25 10

caput "BL12I-PS-SHTR-02:CON" 0
/dls_sw/i12/software/tomography_scripts/flat_tif_areadetector.py ffBalls130_2p5s 25 2.5
/dls_sw/i12/software/tomography_scripts/tomo_tif_areadetector.py Balls130_2p5s 6000 2.5
/dls_sw/i12/software/tomography_scripts/flat_tif_areadetector.py faBalls130_2p5s 25 2.5
caput "BL12I-PS-SHTR-02:CON" 1
/dls_sw/i12/software/tomography_scripts/flat_tif_areadetector.py dfBalls130_2p5s 25 2.5



