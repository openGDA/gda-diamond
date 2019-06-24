#!/bin/bash
	
	
# The PV used for delay of disable/enable pattern
	
#caput SR06I-MO-SERVC-01:BLDISABLEDLY.DLY1 10

#Old : SR06I-MO-SERVC-01:BLDISABLEDLY.DLY1 20
#New : SR06I-MO-SERVC-01:BLDISABLEDLY.DLY1 10

#The ID control softmotor edm lanucher

cd /dls_sw/prod/R3.14.8.2/support/motor/6-2-2dls3/data
edm -x -m "motor=SR06I-MO-SERVC-01:BLGAPMTR" motor.edl &

