###########################################################################
# Contains script to used to create .ffiinf flood field correction file 
###########################################################################
import sys
from time import sleep
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog

from shutterCommands import openEHShutter, closeEHShutter
from operationalControl import moveMotor
from ccdScanMechanics import setMaxVelocity

#ccdFloodAxis = eht2theta
#ccdFloodDistance = eht2dtx

global configured, ruby, beamline, ccdFloodAxis, ccdFloodDistance
configured = False
def configure(jythonNameMap, beamlineParameters):
	global configured, ruby, beamline, ccdFloodAxis, ccdFloodDistance
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	beamline = jythonNameMap.beamline
	ruby = jythonNameMap.ruby
	ccdFloodAxis = jythonNameMap.ccdFloodAxis
	ccdFloodDistance = jythonNameMap.ccdFloodDistance
	configured = True
	
def checkConfigured():
	if not configured:
		raise "ccdFloodCorrections not configured"

########################################################################
def ccdFlood(exportedFileName, noOfImagesInSum, exposureTime, bin, noOfRuns=1, subDarksAtEnd='n'):
	"""
	Ensures axis is at zero, resets shutters, stores correlated dark image
	and exports sum of correlated images (each minus dark image) to given file.
	
	subDarksAtEnd = y : if darks to be subtracted, subtract at end
	
	e.g. ccdFlood("summedImages", 40, 10, 2, 1)
		 ccdFlood("testNov19a_1x1", 4, 10, 1, 1)
		 ccdFlood("testNov19a_1x1", 4, 10, 1, 1, 'n')		# don't subtract dark images 
		 ccdFlood("test_10", 5, 10, 1, 1, 'y', 'n')			# subtract darks and always take new dark image
	"""
	checkConfigured()
	ruby.setBin(bin)
	readOutDelay = ruby.getReadOutDelay()
	ruby.showCorrections()
	ruby.getExportAll()
		
	#Reset axis
	simpleLog ( "==============CCD_FLOOD STARTING===========")
	simpleLog ( "Distance offset is: " + str(ccdFloodDistance.getPosition()))
	maxVelocity = float(ccdFloodSetMaxVelocity())
	initialPosition = ccdFloodAxis.getPosition()
	if (initialPosition == 0):
		simpleLog ( "Angle already at 0")
	else:
		waitingTime = abs(initialPosition)/maxVelocity
		moveMotor(ccdFloodAxis, 0)
		simpleLog ( "Moved angle from " + str(initialPosition) + " to 0 in " + str(waitingTime) + "s...")
		sleep(waitingTime)
	
	#Reset shutters
	closeEHShutter()
	#ruby.closeS()
	#rubyFlush()

	for runNo in range(1, noOfRuns + 1, 1):
		exportedFileNameWithRunNo = exportedFileName
		if (noOfRuns > 1):
			simpleLog("RUN NO: " + str(runNo))
			exportedFileNameWithRunNo = exportedFileName + "_runNo" + str(runNo) 
			
		# Store correlated dark images
#		if (subDarksAtEnd == 'y' or subDarks == 'e'):
#			storeCorrelatedDarks(exportedFileNameWithRunNo, exposureTime, readOutDelay, overrideDarks)
#			if (overrideDarks == 'y'):
#				simpleLog("(New correlated dark image will overwrite any existing image)")
#		else:
#			simpleLog("(Dark images will not be subtracted)")
		ruby.getSubtractDark()
				
		# Do exposures and export to file
		openEHShutter()
		ccdFloodExpose(exportedFileNameWithRunNo, noOfImagesInSum, exposureTime, readOutDelay, subDarksAtEnd)
		
		# close shutters
		closeEHShutter()
		simpleLog ( "================SCRIPT COMPLETE=================")

########################################################################
def ccdFloodAngleScan(exportedFileName, start, stop, step, exposureTime, bin, darks='y'):
	"""
	Resets shutters, takes correlated dark image, moves axis from start to
	stop angle by given step. At each angle, it takes 2 images, correlates
	them and exports resulting image.
	
	e.g. ccdFloodAngleScan("imageAtAngle", -50, 50, 5, 10, 2)
	"""
	checkConfigured()
	ruby.setBin(bin)
	readOutDelay = ruby.getReadOutDelay()
	ruby.showCorrections()
	ruby.getExportAll()
	
	simpleLog ( "============CCD_FLOOD_SCAN STARTING===========")

	simpleLog ( "Distance offset is: " + str(ccdFloodDistance.getPosition()))
	
	#Reset shutters
	closeEHShutter()
	ruby.closeS()
	openEHShutter()
	
	# Store correlated dark images
	if (darks == 'y'):
		storeCorrelatedDarks(exportedFileName, exposureTime, readOutDelay)
	else:
		simpleLog("(Dark images will not be subtracted)")
	
	# Set max velocity for axis and calculate waiting time = travel time + 1s
	maxVelocity = float(ccdFloodSetMaxVelocity())
	initialPosition = ccdFloodAxis.getPosition()
	waitingTime = abs(start - initialPosition)/maxVelocity
	waitingTime1 = step/maxVelocity
		
	i = 1
	angle = start
	nameSuffix = "_" + str(ruby.binning) + "x" + str(ruby.binning) + "_"
	while (angle < stop):
		
		# Move axis to next position and wait for it to get there
		simpleLog ( "--------------------")
		simpleLog ( "Move to angle: " + str(angle) + " in " + str(waitingTime) + "s")
		moveMotor(ccdFloodAxis, angle)
		sleep(waitingTime)
		waitingTime = waitingTime1
		
		# Do 2 exposures and export to file
		ccdFloodExpose(exportedFileName + nameSuffix + str(i), 2, exposureTime, readOutDelay, darks)
		sleep(exposureTime + readOutDelay)			#Wait for exposure time + readout delay
		angle = angle + step
		i = i + 1
	
	# close shutters
	closeEHShutter()
	simpleLog ( "================SCRIPT COMPLETE=================")

########################################################################
def ccdFloodExpose(exportedFileName, noOfImagesInSum, exposureTime, readOutDelay, subDarksAtEnd):
	"""
	Takes a given number of exposures, correlates them, subtracts the saved correlated
	dark image, and sums them up. It then exports the resulting image to given file. 
	"""
	checkConfigured()
	# Take first image
	readOutDelay = readOutDelay *2
	totalWait = exposureTime + readOutDelay
	simpleLog("Take first image (waiting " + str(totalWait) + "s = exposureTime + readOutDelay)")
	
	#openEHShutter()
	ruby.correctFlood1(exposureTime, getFlag(subDarksAtEnd), exportedFileName + "_expNo1")
	sleep(totalWait)

	if (noOfImagesInSum == 0):
		simpleLog("Note: only one image taken, so correlation applied")
		return

	# Take remaining images, correlating and adding
	for i in range(2, noOfImagesInSum + 1, 1):
        
		message = "Take image no " + str(i) + " and correlate"
		if (i > 2):
			message = message + ". Then sum with last correlated image..." 
		message = message + " (waiting " + str(totalWait) + "s)"
		simpleLog (message)
		
		name = exportedFileName + "_expNo" + str(i)
		
		#openEHShutter()
		ruby.correctFlood2(exposureTime, getFlag(subDarksAtEnd), name)
		sleep(totalWait)

	# Export correlated, summed images
	simpleLog( "Exporting summed image: " + exportedFileName)
	noOfDarksToSubtract = 0
	if (subDarksAtEnd == 'y'):
		#noOfDarksToSubtract = noOfImagesInSum - 1
		noOfDarksToSubtract = noOfImagesInSum
		simpleLog("Subtracting " + str(noOfDarksToSubtract) + " * dark images")
		
	ruby.correctFlood3(exportedFileName, str(noOfDarksToSubtract), exposureTime)

########################################################################
def storeCorrelatedDarks(exportedFileName, exposureTime, readOutDelay, override):
	"""
	Calls IS script which takes 2 dark images, correlates them and stores the
	resulting image 
	"""
	checkConfigured()
	totalWait = 2*(exposureTime + readOutDelay)
	simpleLog ( "Take 2 dark images, correlate and save (waiting " + str(totalWait) + "s)")
	ruby.takeDarksAndCorrelate(exposureTime, exportedFileName, getFlag(override))
	sleep(totalWait)
	
def exportMultiDark(exportedFileName, exposureTimes, bin):
	"""
	e.g. exportMultiDark("darks", [1, 10, 20], 1)
	"""
	checkConfigured()
	ruby.setBin(bin)
	readOutDelay = ruby.getReadOutDelay()
	ruby.setExportAll(1)		# save all raw images
	
	for i in range(0, len(exposureTimes), 1):
		
		name = exportedFileName + "_" + str(i)
		ruby.takeDarksAndCorrelate(str(exposureTimes[i]), name)
		totalWait = 2*(exposureTimes[i] + readOutDelay) + 3
		simpleLog ( "Take 2 dark images, correlate and save (waiting " + str(totalWait) + "s)")
		sleep(totalWait)
		simpleLog ( "Exported dark1, dark2 and corr image for: " + name)

########################################################################
def getFlag(value):
	if (value == 'y'):
		return '1'
	else:
		return '0'

########################################################################
def ccdFloodSetMaxVelocity():
	"""
	Sets the maximum velocity on the flood axis motor
	"""
	checkConfigured()
	if (ccdFloodAxis.name == 'testLinearDOF1'):
		simpleLog("Testing mode: max velocity set to 5")
		return 5
	
	maxVelocity = beamline.getValue(None,"","-MO-TABLE-03:TABLE:THETAZ2.VMAX")
	beamline.setValue("","-MO-TABLE-03:TABLE:THETAZ2.VELO", maxVelocity)
	return maxVelocity

########################################################################		
def rubyFlush():
	"""
	Clear any left-over responses from ccd
	"""
	checkConfigured()
	try:
		simpleLog("Flushing ruby socket - please wait...")
		ruby.flush()
	except:
			type, exception, traceback = sys.exc_info()
			handle_messages.log(None, "rubyFlush failed.Ensure IS is properly initialised, then do: ruby.connect()", 
							type, exception, traceback, True)	
