# Scripts for pilatus scans
import sys
from time import sleep
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
import pd_pilatus
from shutterCommands import openEHShutter, closeEHShutter
from ccdScanMechanics import scanGeometry
from ccdScanMechanics import setMaxVelocity
from ccdScanMechanics import deactivatePositionCompare

global configured, pilatus, beamline
configured = False
def configure(jythonNameMap, beamlineParameters):
	global configured, pilatus, beamline
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	beamline = jythonNameMap.beamline
	pilatus = jythonNameMap.pilatus
	configured = True
	
def checkConfigured():
	if not configured:
		raise "pilatus_scripts not configured"

######################################################################################
def pilatusExpose(exposureTime, fileName, N):
	"""
	pilatusExpose(exposureTime, fileName, N)
	Take 'N' Exposures of 'exposureTime' seconds.
	"""
	checkConfigured()	
	simpleLog("pilatusExpose(...) is depreciated - please use expose(pilatus, exposureTime, noOfExposures, fileName)")
	return expose(pilatus, exposureTime, N, fileName)

def pilatusScan(exposureTime, fileName, axis, start, stop, step):
	checkConfigured()	
	simpleLog("pilatusScan(...) is depreciated - please use simpleScan(axis, start, stop, step, pilatus, exposureTime, fileName)")
	return simpleScan(axis, start, stop, step, pilatus, exposureTime, fileName)

def pilatusNScan(exposureTime, fileName, axis, A, B, N):
	checkConfigured()	
	simpleLog("pilatusNScan(...) is depreciated - please use singleStepScan(axis, start, stop, noOfExposures, pilatus, exposureTime, fileName)")
	return singleStepScan(axis, A, B, N, pilatus, exposureTime, fileName)

def pilatusRock(exposureTime, fileName, axis, centre, rock, N):
	checkConfigured()	
	simpleLog("pilatusRock(...) is depreciated - please use rockScan(axis, centre, rockSize, noOfRocks, pilatus, exposureTime, fileName)")
	return rockScan(axis, centre, rock, N, pilatus, exposureTime, fileName)

def genericPilatusScan(exposureTime, fileName, axis, start, stop, step, N):
	"""
	pilatusScan(exposureTime, fileName, axis, start, stop, step)
	"""
	checkConfigured()	
	#Checks
	filesCreated = []
	if (start == stop):
		raise "Start and stop must take different values"
	if (step == 0):
		raise "Step must be non-zero"

	#Work out no of steps
	M = int(round( abs(stop-start)/step , int(5) ))
	if (M < 1):
		raise "Step size is too big - number of steps must be greater than 5"

	#Reset and open EH shutter
	ruby.closeS()
	openEHShutter()
	initialPosition = axis.getPosition()		#Store initial Position to return to 
	setMaxVelocity(axis)				#Max velocity to move...

	#Do the scan
	overwriteFlag = ""
	pilatus.setFilename(fileName + "_")
	for i in range(0,M,1):
		
		if (stop>start):
			A=start+i*step
			B=A+step
		else: 
			A=start-i*step
			B=A-step
		
		for j in range(0,N,1):
			openEHShutter()
			pilatusScanElement(exposureTime, pilatus, axis, A, B)
			closeEHShutter()
			fullFilename = pilatus.getFullFilename()
			filesCreated.append(fullFilename)
			simpleLog("Data Filename: "+ fullFilename)
			simpleLog("===========")
		
	#Set back to initial position and velocity
	closeEHShutter()                	#Ensure EH shutter is closed
	setMaxVelocity(axis)			#Max velocity to move...
	axis(initialPosition)			#...back to initial Position
	
	simpleLog("================SCRIPT COMPLETE=================")
	return filesCreated
######################################################################################		
def pilatusScanElement(exposureTime, pilatus, axis, A, B):
	"""
	Move from A to B in exposureTime seconds, and take an exposure of exposureTime seconds using 
	ccd shutter.
	"""
	checkConfigured()	
	#User Feedback.
	simpleLog("Scanning from " + str(A) + "->" + str(B) + " in " + str(exposureTime) + " seconds.")
	velocity = float(abs(B-A))/float(exposureTime)	#Set velocity
	runUp = velocity/10				#Acceleration Runup Allowance (degrees)

	deactivatePositionCompare()		#Prevent false triggers when debounce on
	axis(A-runUp)					#Move to run up position before/after A.

	geometry = scanGeometry(axis, velocity, A, B)	#Set up XPS for scan. Not save geometry
	
	sleep(0.2)					#Just in case...
	ruby.xpsSync()				#Scan with fast shutter and dump ccd data

	pilatus.expose(exposureTime)

	axis(B+runUp)					# Move axis to a point before/after B.

	if (axis.name!='testLinearDOF1'):
		deactivatePositionCompare()			#Exposure complete (deactivates all position compares...)

	return

######################################################################################		
def resetPilatusScanNumber():
	"""
	Resets the next Pilatus file number to zero
	"""
	checkConfigured()	
	pilatus.setFileNumber(0)