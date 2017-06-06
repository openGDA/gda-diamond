#Auxiliary MAR Scripts:

import time
import shutil
import sys
from time import sleep
import time
import glob
import os
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
from util_scripts import doesFileExist
from shutterCommands import openEHShutter, closeEHShutter
from gda.jython.commands.GeneralCommands import pause
global configured, mar, beamline
configured = False
def configure(jythonNameMap, beamlineParameters):
	global configured, mar, beamline
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	mar = jythonNameMap.mar
	beamline = jythonNameMap.beamline
	configured = True
######################################################################################
	
def marErase(N):
	"""
	marErase(N)
	erases image plate N times.
	"""
	checkMarIsReady()
	
	marEraseTimeout = 250
	
	#Make sure EH shutter is closed.
	closeEHShutter()
	for i in range(0,N,1):
		simpleLog("==============")
		
		# Wait for mar to be ready before starting erase
		timeTaken = waitForMarStatus(marEraseTimeout, 0)
		if (timeTaken == -1):
			simpleLog("Timed out waiting for mar to be ready, so erase not performed")
		else:
			# Send erase command and Wait for mar to start erasing
			simpleLog( "Mar ready, so start erasing " + str(i+1) + " of " + str(N) )
			mar.erase()
			timeTaken = waitForMarStatus(marEraseTimeout, 1)
			if (timeTaken == -1):
				simpleLog("Timed out waiting for mar to start, so erase not performed")
			else:
				# Scan erasing and wait for mar to be ready
				timeTaken = waitForMarStatus(marEraseTimeout, 0)
				if (timeTaken == -1):
					simpleLog("Timed out waiting for mar to stop erasing")
				else:
					simpleLog("Erased in time %.2f" % timeTaken + "s")
	
	simpleLog("Erasures complete")

#######################################################################################
def waitForMarStatus(timeout, status):
	"""
	waitForMarStatus(timeout, status) waiting for mar status
	returns time taken or -1 if timed out
	"""

	t0 = time.clock()
	t1 = t0
	while ( (t1 - t0) < timeout ): 
		if (mar.getStatus() == status):
			#simpleLog("Mar status of " + str(status) + " reached in time %.2f" % (t1 - t0) + "s")
			return (t1 - t0)
		t1 = time.clock()
		pause()                     # ensures script can be stopped promptly

	simpleLog("Timed out waiting for mar status of " + str(status) + " (waited " + str(timeout) + "s)")
	return -1

#######################################################################################
def checkMarIsReady():
	"""
	If mar not ready, then display message and abort
	"""
	status = mar.getStatus() 
	if (status != 0):
		raise "Mar is not ready. Please wait or restart the mar. Value = " +`status`

#######################################################################################
def getScanNumberPath(pathStub):

	# Try to read from pathStub location
	pathToNextCCDNumberList = glob.glob(pathStub + ".*")
	
	# If no such file, create one
	if (len(pathToNextCCDNumberList)==0):
		h=open(pathStub + '.0','w')
		h.close()
		return pathStub + '.0'
	else:
		return pathToNextCCDNumberList[0]

#######################################################################################
def getMarScanNumberPath():

	return getScanNumberPath("/dls_sw/i15/var/nextMarScanNumber")

#######################################################################################
def getNextMarScanNumber():
	
	path = getMarScanNumberPath()
	return int(path[path.find(".")+1:])

######################################################################################
def incrementMarScanNumber():

	path = getMarScanNumberPath()
	nextNumber = int(path[path.find(".")+1:]) + 1
	pathUpToNumber =  path[:path.find(".")+1]
	os.rename(path, pathUpToNumber + str(nextNumber))

	return nextNumber

######################################################################################
def resetMarScanNumber():

	path = getMarScanNumberPath()
	pathUpToNumber =  path[:path.find(".")+1]
	os.rename(path, pathUpToNumber + str(0))

def remove_001Suffix(filePaths):
	"""
	remove_001Suffix(filePaths)
	For each filePath in list, look for actual file with suffix '_001.mar345'. If exists
	remove the '_001' (appended by mar software)
	"""
	simpleLog("remove '_001' suffix from files...")
	filesCreated = []
	for filePath in filePaths:
		fileWithSuffix = filePath + "_001.mar3450"
		if (doesFileExist(fileWithSuffix)):
			newName = filePath + ".mar3450"
			os.rename(fileWithSuffix, newName)
			filesCreated.append(newName)
		else:
			simpleLog("Could not find file " + fileWithSuffix + " to rename")
	return filesCreated

# This now acts as openPEShield and openDetectorShield
def openMarShield():
	"""
	Open Detector shield
	"""
	try:
		status = beamline.getValue(None,"Top","-RS-ABSB-06:CON")
		if (status == 0):
			simpleLog("Detector shield already open")
		else:
			beamline.setValue("Top","-RS-ABSB-06:CON", 0)
			
			# wait and check shield has opened
			sleep(3)
			status = beamline.getValue(None,"Top","-RS-ABSB-06:CON")
			if (status == 0):
				simpleLog("Detector shield opened")
			else:
				simpleLog("Detector shield failed to open - status is: " + `status`)
	except:
		typ, exception, traceback = sys.exc_info()
		handle_messages.log(None, "Problem opening Detector shield - ", typ, exception, traceback)

######################################################################################
# This now acts as closePEShield and closeDetectorShield
def closeMarShield():
	"""
	Close Detector shield
	"""
	try:
		status = beamline.getValue(None,"Top","-RS-ABSB-06:CON")
		if (status == 1):
			simpleLog("Detector shield already closed")
		else:
			beamline.setValue("Top","-RS-ABSB-06:CON", 1)
			
			# wait and check shield has closed
			sleep(3)
			status = beamline.getValue(None,"Top","-RS-ABSB-06:CON")
			if (status == 1):
				simpleLog("Detector shield closed")
			else:
				simpleLog("Detector shield failed to close - status is: " + `status`)
	except:
		typ, exception, traceback = sys.exc_info()
		handle_messages.log(None, "Problem closing mar shield - ", typ, exception, traceback)