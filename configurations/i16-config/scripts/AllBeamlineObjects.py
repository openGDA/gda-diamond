# This module will in the furutr be dynamically filled to contain all the
# scannables in the main namespace. IT also contains a flag to say wether
# the software is running as a simulation or not.

# This setting should later be set in java.properties
isDummySimulationFlag = 0

if isDummySimulationFlag:
	print "WARNING: Simulataion mode set in AllBeamlineObjects.py.Some devices not loaded, and energy set from file"

def isDummySimulation():
	return isDummySimulationFlag

def isLiveBeamline():
	return not(isDummySimulationFlag)

def addAllMainNamespaceScannables():
	print "STUB" 
