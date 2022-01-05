#!/bin/sh
 
#This script is used to run the new 'scanData' simulation.
#A new element called 'UPDATE', which user should write to this PV 
#after setting the start index and no of elements, and it will trigger
#the arrays to be updated with the new data.
#
#It supports ca_put_callback so you can tell when the arrays are ready for reading.
#
#A very quick simulation which is now running on the simulation pc (dasc-epics) on port 6064.
#It just fills the waveforms up by incrementing a counter, and there are two additional PVs 
#to start and stop the simulation.

export EPICS_CA_SERVER_PORT=6064;
#export EPICS_CA_REPEATER_PORT=6064;

totalPoint=1000;
blockSize=10;
./simFastScan.py $totalPoint $blockSize

