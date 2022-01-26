#!/usr/bin/env python2.4

# Usage: simFastScan.py <noScanPoints> <pointsPerBlock>

from pkg_resources import require
require("dls.ca2==2.16")

from dls.ca2.catools import *

# # PV definitions
# ################
# counterPv='BL06I-MO-FSCAN-01:ELEMENTCOUNTER'
# elementsPv='BL06I-MO-FSCAN-01:NOELEMENTS'
# indexPv='BL06I-MO-FSCAN-01:STARTINDEX'
# updatePv='BL06I-MO-FSCAN-01:UPDATE'
# ch1Pv='BL06I-MO-FSCAN-01:CH1SUBARRAY'
# # (repeat for ch2..ch6)
# 
# # Pvs used in simulation only:
# simStartPv='BL06I-MO-FSCAN-01:STARTSIM.PROC'
# simStopPv='BL06I-MO-FSCAN-01:STOPSIM.PROC'
# 
# ###############

scanPoints=float(sys.argv[1])
pointsPerBlock=float(sys.argv[2])


# Start the simulation
print("Starting simulation")
caput(simStartPv, 1, timeout=1.0)

noDataPoints=0
index=0

# Repeat until we have retrieved all of the scan data
while noDataPoints<scanPoints:
	# Keep checking counter to see if the next block is available
	print("Waiting for next data block")
	noDataPoints=noDataPoints+pointsPerBlock
	counter=caget(counterPv).value
	while counter<noDataPoints:
		counter=caget(counterPv).value
	# end while
 
	# Set start index and number of elements to read
	caput(indexPv, index, timeout=1.0)
	caput(elementsPv, pointsPerBlock, timeout=1.0)

	# Update the arrays with the new data
	# Use ca_put_callback to wait until arrays have been updated before continuing
	caput(updatePv, 1, wait=True, timeout=5.0)

	# Read the waveforms
	print(caget(ch1Pv).dbr.value)
	
	# Increment the start index for the next block
	index=index+pointsPerBlock
	
# end while	

# Stop the simulation
print("Stopping simulation")
caput(simStopPv, 1, timeout=1.0)

print("Done.")

