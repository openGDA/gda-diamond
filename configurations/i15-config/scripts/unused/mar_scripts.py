#import java
import glob
import sys
import os
import math
from math import *
import time
from time import sleep
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
from util_scripts import doesFileExist
from util_scripts import updateFileOverwriteFlag
from operationalControl import moveMotor
from shutterCommands import openEHShutter, closeEHShutter
from ccdScanMechanics import scanGeometry
from ccdScanMechanics import setMaxVelocity
from ccdScanMechanics import deactivatePositionCompare
from marAuxiliary import openMarShield, closeMarShield
from marAuxiliary import incrementMarScanNumber
from marAuxiliary import checkMarIsReady

marScanTimeout = 300

global configured, mar, beamline
configured = False
def configure(jythonNameMap, beamlineParameters):
	global configured, mar, beamline
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	beamline = jythonNameMap.beamline
	mar = jythonNameMap.mar
	configured = True
	
def checkConfigured():
	if not configured:
		raise "mar_scripts not configured"

######################################################################################
def marScan(exposureTime, fileName, axis, start, stop, step, overwriteFlag=""):
	"""
	marSync(exposureTime, fileName, axis, start, stop, step)
	Will perform a set of scans (ONLY DKPHI NOW)
	Scan of exposureTime seconds, and save in X:/OD/(fileName)_X.img.
	"""
	checkConfigured()
	simpleLog("marScan(...) is depreciated - please use simpleScan(axis, start, stop, step, mar, exposureTime, fileName)")
	return simpleScan(axis, start, stop, step, mar, exposureTime, fileName, -1, overwriteFlag)

#	try:
#		simpleLog( "====================MAR SYNC====================")
#		# Note: set runNumber = 1 to always start at _001 (required for Crysalis data analysis)
#		return marGenericScan(exposureTime, fileName, 1, axis, start, stop, abs(step), 1, True, overwriteFlag)
#	except:
#		type, exception, traceback = sys.exc_info()
#		handle_messages.log(None, "marScan error", type, exception, traceback, True)

######################################################################################
def marScanUnsync(exposureTime, fileName, axis, start, stop, step, overwriteFlag=""):
	"""
	marScan(exposureTime, fileName, axis, start, stop, step)
	Will perform a set of start -> stop scans with step size (ONLY DKPHI NOW) and exposureTime seconds.
	overwriteFlag - ya (yes to all), na ( no to all) , otherwise prompt	
	"""
	checkConfigured()
	try:
		simpleLog("====================MAR SCAN UNSYN====================")
		return marGenericScan(exposureTime, fileName, -1, axis, start, stop, abs(step), 1, False, overwriteFlag)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None, "marScan unsync error", type, exception, traceback, True)		

######################################################################################
def marNScan(exposureTime, fileName, axis, A, B, N, overwriteFlag=""):
	"""
	marNScan(exposureTime, fileName, axis, A, B, N)
	Performs N scans of A->B.
	overwriteFlag - ya (yes to all), na ( no to all) , otherwise prompt	
	"""
	checkConfigured()
	simpleLog("marNScan(...) is depreciated - please use singleStepScan(axis, start, stop, noOfExposures, mar, exposureTime, fileName)")
	return singleStepScan(axis, A, B, N, mar, exposureTime, fileName, -1, overwriteFlag)

#	try:
#		simpleLog("====================MAR N SCAN====================")
#		return marGenericScan(exposureTime, fileName, -1, axis, A, B, abs(B-A), N, True, overwriteFlag)
#	except:
#		type, exception, traceback = sys.exc_info()
#		handle_messages.log(None, "marNScan error", type, exception, traceback, True)		

######################################################################################
def marRock(exposureTime, fileName, axis, centre, rock, N, overwriteFlag=""):
	"""
	marRock(exposureTime, fileName, axis, centre, rock, N)
	Will perform N rock scans (ONLY DKPHI NOW) and exposureTime seconds.
	overwriteFlag - ya (yes to all), na ( no to all) , otherwise prompt	
	"""
	checkConfigured()
	simpleLog("marRock(...) is depreciated - please use rockScan(axis, centre, rockSize, noOfRocks, mar, exposureTime, fileName)")
	return rockScan(axis, centre, rock, N, mar, exposureTime, fileName, -1, overwriteFlag)

def marRockUnsync(exposureTime, fileName, axis, centre, rock, N, overwriteFlag=""):
	"""
	As for marRock but unsynchronised
	"""
	checkConfigured()
	try:
		simpleLog("====================MAR ROCK UNSYNC====================")
		return marGenericScan(exposureTime, fileName, -1, axis, centre-rock, centre+rock, abs(2*rock), N, False, overwriteFlag)
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None, "marRock unsync error", type, exception, traceback, True)		
######################################################################################
def marExpose(exposureTime, fileName, N, overwriteFlag=""):
	"""
	marExpose(exposureTime, fileName, N)
	Will perform N exposures of exposureTime seconds.
	overwriteFlag - ya (yes to all), na ( no to all) , otherwise prompt	
	"""
	checkConfigured()
	simpleLog("marExpose(...) is depreciated - please use expose(mar, exposureTime, noOfExposures, fileName)")
	return expose(mar, exposureTime, N, fileName)

def marExposeElement(exposureTime):
	"""
	marExpose(exposureTime, fileName)
	Take and Exposure of exposureTime seconds.
	"""
	checkConfigured()
	simpleLog( time.asctime(time.localtime()) )
	simpleLog("Starting MAR exposure of " + str(exposureTime) + " seconds.")

	# Start MAR exposure 
	#Reset and open EH shutter
	ruby.closeS()
	openEHShutter()

	# Begining openning shutter - simpleLog(  "after ruby open " + str(time.clock())
	ruby.openS()
	sleep(exposureTime)
	ruby.closeS()

	closeEHShutter()

######################################################################################
def marGenericScan(exposureTime, fileName, runNumber, axis, start, stop, step, N, sync, overwriteFlag):
	"""
	marGenericScan(exposureTime, fileName, runNumber, axis, start, stop, step, N, sync)
	Will perform a set of start -> stop scans with step size (ONLY DKPHI NOW) and exposureTime seconds, each
	step repeated N times.
	If runNumber >= 0, will append runNumber onto file name
	If sync is true then will take a ccd exposure [ marSynElement(...) in marSync.py ], else will take 
	a mar exposure.
	"""
	checkConfigured()
	#Checks
	if (start == stop):
		simpleLog( "Start and stop must take different values")
		return
	if (step == 0):
		simpleLog( "Step must be non-zero")
		return

	#Work out no of steps
	M = int(round( abs(stop-start)/step , int(5) ))
	if (M < 1):
		simpleLog( "Step size is too big")
		return

	checkMarIsReady()
	
	#Move out diodes1, 2 and 3
	d1out()
	d2out()
	d3out()
	
	#Check mar shield is open
	openMarShield()
	
	#Reset and open EH shutter
	simpleLog( "Reset fast shutter:")
	ruby.closeS()
	openEHShutter()
	initialPosition = axis.getPosition()		#Store initial Position to return to 
	setMaxVelocity(axis)				#Max velocity to move...

	#Get file name stub
	if (not sync):
		if (runNumber >= 0):	
			fileName += "_%02d" % runNumber
		else:
			nextScanNo = incrementMarScanNumber()
			fileName += "_%03d" % nextScanNo

	#Do the scan
	if( overwriteFlag != "ya" and overwriteFlag != "na"):
		overwriteFlag = ""
	filePaths = []
	for i in range(0,M,1):
		
		if (stop>start):
			A=start+i*step
			B=A+step
		else: 
			A=start-i*step
			B=A-step
		suffix1 = ""
		if (M > 1):
			suffix1 = "_%03d" % (i+1)   #Only append step number if more than one step and not marSync
			simpleLog( "==============")
			beamline.setValue("Top","-PS-SHTR-02:CON",0)
			sleep(5)

		for j in range(0,N,1):
			suffix2 = ""
			if (N > 1):
				suffix2 = "_%03d" % (j+1)   #Only append count number if count > 1 and not marSync
				simpleLog( "==============")
				beamline.setValue("Top","-PS-SHTR-02:CON",0)
				sleep(5)

			fullFilename = fileName + suffix1 + suffix2

			#If file already exists, check if can be overwritten (note, final file name with suffix _001 removed)
			overwriteFlag = updateFileOverwriteFlag(mar.getDirectory() + "/" + fullFilename + ".mar3450", overwriteFlag)
			if (overwriteFlag == 'n' or overwriteFlag == 'na'):
				break

			simpleLog( "Data Filename: "+ fullFilename)
			filePaths.append(mar.getDirectory() + "/" + fullFilename)

			mar.setRootName(fullFilename)
			if (sync):
				marSyncElement(exposureTime, axis, A, B)
			else:
				marScanElement(exposureTime, axis, A, B)

			closeEHShutter()

			simpleLog( "Exposed. Scanning Image Plate...")
			
			#scanTheMarTest()
			scanTheMarWithChecks(marScanTimeout)
			simpleLog( "================================================")
		
	#Set back to initial position and velocity
	closeEHShutter()                #Ensure EH shutter is closed
	setMaxVelocity(axis)				#Max velocity to move...
	moveMotor(axis, initialPosition)   #...back to initial Position
	closeMarShield()

	files = remove_001Suffix(filePaths)    #Remove _001 suffix added to all files by mar software
	
	simpleLog( "================SCRIPT COMPLETE=================")
	return files

######################################################################################
def marScanElement(exposureTime, axis, A, B):
	"""
	marScanElement(exposureTime, A, B, fileName, axis)
	Move from A to B in exposureTime marScanElementseconds, and take a mar exposure of exposureTime seconds.
	"""
	checkConfigured()

	#User Interface.
	simpleLog( time.asctime(time.localtime()) )
	simpleLog(str(A) + "->" + str(B) + " in " + str(exposureTime) + " seconds.")

	#Preparatory: maximum velocity.
	setMaxVelocity(axis)

	#move to start position
	moveMotor(axis, A)

	#Set up velocity
	velocity = float(abs(B-A))/float(exposureTime)
	beamline.setValue("Top","-MO-DIFF-01:SAMPLE:KPHI.VELO",velocity)

	ruby.openS()
	moveMotor(axis, B)
	ruby.closeS()
	setMaxVelocity(axis)

######################################################################################
def scanTheMarWithChecks(timeout):
	"""
	Scan the mar, checking for correct status 
	"""
	checkConfigured()
	# Wait for mar to be ready before starting scan
	timeTaken = waitForMarStatus(timeout, 0)
	if (timeTaken == -1):
		raise "Timed out waiting for mar to be ready, so scan not performed"
	
	mar_mode = mar.getMode()
	if (mar_mode != 4):
		simpleLog( "Mar mode is %d not the default 4, use 'mar.setMode()' to change mode." % mar_mode)
	
	#simpleLog("mar ready in time %.2f" % timeTaken + "s")
	# Wait for mar to start scanning
	mar.scan()
	timeTaken = waitForMarStatus(timeout, 1)
	if (timeTaken == -1):
		raise "Timed out waiting for mar to start, so scan not performed"
	
	#simpleLog("mar busy in time %.2f" % timeTaken + "s")
	# Scan scanning and wait for mar to be ready
	timeTaken = waitForMarStatus(timeout, 0)
	if (timeTaken == -1):
		raise "Timed out waiting for mar to stop scanning"

	simpleLog("Scanned in time %.2f" % timeTaken + "s")

def marSyncElement(exposureTime, axis, A, B):
	"""
	Move from A to B in exposureTime seconds, and take an ccd exposure of exposureTime seconds.
	"""
	checkConfigured()

	#User feedback
	simpleLog( time.asctime(time.localtime()) )
	simpleLog( "Scanning from " + str(A) + "->" + str(B) + " in " + str(exposureTime) + " seconds.")
	velocity = float(abs(B-A))/float(exposureTime)	#Set velocity
	runUp = velocity/10				#Acceleration Runup Allowance (degrees)

	setMaxVelocity(axis)
	deactivatePositionCompare() #Prevent false triggers when debounce on
	moveMotor(axis, A-runUp)					#Move to run up position before/after A.
	
	geometry = scanGeometry(axis, velocity, A, B)	#Set up XPS for scan. Not save geometry

	sleep(0.2)					    #Just in case...
	ruby.xpsSync("temp")				#Scan with fast shutter, save marimage, dump ccd data
	#ruby.detector.runScript("call smi_timeout0")
	
	moveMotor(axis, B+runUp)					# Move axis to a point before/after B.
	
	deactivatePositionCompare()			#Exposure complete (deactivates all position compares...)
	setMaxVelocity(axis)               # reset to max velocity
	simpleLog( "==============")
