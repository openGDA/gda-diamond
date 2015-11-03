######################################################################################
#
# Note that these scripts should no longer be used and have been replaced by the ones 
# in detectorScanScripts.py (7Jan 09)
#
######################################################################################
import sys
from time import sleep
from gda.jython.commands.GeneralCommands import pause
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
from operationalControl import updateFileOverwriteFlag 
from operationalControl import moveMotor
from shutterCommands import openEHShutter, closeEHShutter
from ccdAuxiliary import openCCDShield
from ccdScanMechanics import scanGeometry
from ccdScanMechanics import setMaxVelocity
from ccdAuxiliary import incrementCCDScanNumber
from ccdScanMechanics import deactivatePositionCompare
from ccdScanMechanics import setVelocity
global configured, ruby, beamline
configured = False
def configure(jythonNameMap, beamlineParameters):
	global configured, ruby, beamline
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	beamline = jythonNameMap.beamline
	ruby = jythonNameMap.ruby
	configured = True
	
def checkConfigured():
	if not configured:
		raise "ccdScripts not configured"

def ccdExpose(exposureTime,fileName,N):
	checkConfigured()
	simpleLog("ccdExpose(...) is depreciated - please use expose(ruby, exposureTime, noOfExposures, fileName)")
	return expose(ruby, exposureTime, N, fileName)
	
#	return ccdGenericExpose(exposureTime,fileName,N,False)
	
def ccdDarkExpose(exposureTime,fileName,N):
	checkConfigured()
	simpleLog("ccdDarkExpose(...) is depreciated - please use darkExpose(ruby, exposureTime, noOfExposures, fileName)")
	return darkExpose(ruby, exposureTime, N, fileName)
	
#	return ccdGenericExpose(exposureTime,fileName,N,True)
	
def ccdGenericExpose(exposureTime,fileName, numExposures,dark):
	"""
	ccdExpose(exposureTime, fileName,N,dark)
	Take 'numExposures' Exposures of 'exposureTime' seconds.
	Plot to Data Vector window
	If dark is True, EH shutter is kept closed 
	"""
	checkConfigured()
	#check diodes are out and ccd shield is open
	d1out()
	d2out()
	d3out()
	openCCDShield()
	
	#clear any left over responses from ccd
	filesCreated = []
	try:
		try:
			ruby.flush()
		except:
			type, exception, traceback = sys.exc_info()
			handle_messages.log(None, "ccdExpose error: initial flush command failed.Ensure IS is properly initialised, then do: ruby.connect()", 
							type, exception, traceback, True)			

		#Get file name stub
		nextScanNo = incrementCCDScanNumber()
		fileName += "_%03d" % nextScanNo
		readOutDelay = ruby.getReadOutDelay()					#Find current bin & readout delay.
		closeEHShutter()
		ruby.closeS()

		simpleLog( "===================CCD EXPOSE===================")
		overwriteFlag = ""
		for i in range(0, numExposures, 1):
			fullFilename = fileName
			if (numExposures > 1):
				fullFilename += "_%03d" % (i+1)   #Only append step number if more than one step
			
			#If file already exists, check if can be overwritten
			overwriteFlag = updateFileOverwriteFlag("/dls/i15/data/currentdir" + "/" + fullFilename + ".img", overwriteFlag)
			if (overwriteFlag == 'n' or overwriteFlag == 'na'):
				break
					
			ruby.flush()
			sleep(2)
			simpleLog ( "Data Filename: " + fullFilename )
			
			#TEMP. CODE:
			if (dark):
				simpleLog("Dark expose: leave EH shutter closed")
			else:
				openEHShutter()
				
			thisFile = ruby.expose(exposureTime, fullFilename)
			simpleLog ( "CCD Exposure: " + str(exposureTime) + "seconds" )
			sleep(exposureTime)
			
			closeEHShutter()     #TEMP. CODE:
			simpleLog ( "Exposure done.")
			sleep(readOutDelay)
			if (ruby.getBin() != 1):
				ruby.readImage(None)
			ruby.flush()
			ruby.getS()
			filesCreated.append("/dls/i15/data/currentdir" + "/" + thisFile)
			#do not plot due to NFS timing problems causes a long delay
#			ruby.plot("/dls/i15/data/currentdir" + "/" + thisFile)
			simpleLog ( "===============================================" )
	
		#closeEHShutter()		#TEMP. COMMENTED OUT
		simpleLog ( "================SCRIPT COMPLETE=================" )
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None, "ccdExpose error", type, exception, traceback, True)
	return filesCreated

#####################################################################################
def ccdScan(exposureTime, fileName, runNumber, axis, start, stop, step, overwriteFlag=""):
	"""
	ccdScan(exposureTime, fileName, runNumber, axis, start, stop, step)
	Will perform 1 scan of exposureTime seconds, and save to local disk on OD PC.
	overwriteFlag - ya (yes to all), na ( no to all) , otherwise prompt
	eg/
	ccdScan(1,"scanTest", 1, dkphi, -122, -121, .5)
	"""
	checkConfigured()
	simpleLog("ccdScan(...) is depreciated - please use simpleScan(axis, start, stop, step, ruby, exposureTime, fileName, runNumber)")
	return simpleScan(axis, start, stop, step, ruby, exposureTime, fileName, runNumber, overwriteFlag)
	
#	try:
#		return ccdGenericScan(exposureTime, fileName, runNumber, axis, start, stop, step, 1, 0, 0, overwriteFlag)
#	except:
#		type, exception, traceback = sys.exc_info()
#		handle_messages.log(None, "ccdScan error", type, exception, traceback, True)	

######################################################################################
def ccdDoubleScan(exposureTime, fileName, runNumber, axis, start, stop, step, overwriteFlag=""):
	"""
	ccdDoubleScan(exposureTime, fileName, runNumber, axis, start, stop, step)
	Generates correlated dark image if none exists. Then performs a scan as for ccdScan(...), except 
	that each step is scanned twice and correlated dark image subtracted from each image. 
	The correlation of these two images are then exported for each step.
	e.g.:
	ccdDoubleScan(1,"doubleScanTest", 1, dkphi, -122, -121, .5)
	"""
	checkConfigured()
	simpleLog("ccdDoubleScan(...) is depreciated - please use doubleScan(axis, start, stop, step, ruby, exposureTime, fileName, runNumber)")
	return doubleScan(axis, start, stop, step, ruby, exposureTime, fileName, runNumber, overwriteFlag)

def ccdRock(exposureTime, fileName, axis, centre, rock, N, overwriteFlag=""):
	"""
	ccdRock(exposureTime, fileName, axis, centre, rock, N)
	Will perform N rock scans of exposureTime seconds.
	"""
	checkConfigured()
	simpleLog("ccdRock(...) is depreciated - please use rockScan(axis, centre, rockSize, noOfRocks, ruby, exposureTime, fileName)")
	return rockScan(axis, centre, rock, N, ruby, exposureTime, fileName, -1, overwriteFlag)

#	try:
#		return ccdGenericScan(exposureTime, fileName, -1, axis, centre-rock, centre+rock, abs(2*rock), N, 1, 0, overwriteFlag)
#	except:
#		type, exception, traceback = sys.exc_info()
#		handle_messages.log(None, "ccdRock error", type, exception, traceback, True)	

######################################################################################
def ccdGenericScan(exposureTime, fileName, runNumber, axis, start, stop, step, N, rock, doubleScan, overwriteFlag):
	"""
	ccdGenericScan(exposureTime, fileName, runNumber, axis, start, stop, step, rock)
	Will perform a set of N scans of exposureTime seconds, and save to local disk on OD PC.
	If doubleScan is true, 2 images will be taken for each step and correlated 
	"""
	checkConfigured()
	filesCreated = []
	#Checks
	if (start == stop):
		simpleLog ( "Start and stop must take different values" )
		return
	if (step == 0):
		simpleLog ( "Step must be non-zero" )
		return

	#Work out no of steps 
	M = int(round( abs(stop-start)/step , int(5) ))
	if (M < 1):
		simpleLog ( "Step size is too big" )
		return
	
	#check diodes are out and ccd shield is open
	d1out()
	d2out()
	d3out()
	openCCDShield()

	initialPosition = axis.getPosition()		#Store initial Position to return to 
	readOutDelay = ruby.getReadOutDelay()			#Find current bin & readout delay.

	#Close shutters
	closeEHShutter()
	try:
		ruby.closeS()
	except:
		type, exception, traceback = sys.exc_info()	
		handle_messages.log(None, "ccdScan error: ccd shutter failed to close", type, exception, traceback, True)
		simpleLog("Ensure IS is properly initialised, then do: ruby.connect()")	
		return
	
	# Open EH shutter
	openEHShutter()
	
	#Get file name stub
	if (runNumber >= 0):	
#		fileName += "_%02d" % runNumber         # format _XX for run number
		fileName += "_" + str(runNumber) 	# no formatting for run number
	else:
		nextScanNo = incrementCCDScanNumber()
		fileName += "_%03d" % nextScanNo

	simpleLog ( "==================SCANNING CCD==================" )
	M = int(abs(stop - start)/step)					#Number of exposures
	if( overwriteFlag != "ya" and overwriteFlag != "na"):
		overwriteFlag = ""
	for i in range(0, M, 1):
		if (stop>start):
			A=start + i*step					#Calculate the scan step A to B, so A < B.
			B=A + step					
		else: 
			A=stop + i*step					#Always scan in positive direction.
			B=A + step
		
		suffix1 = ""	
		if (M > 1):				#Only append step number if more than one step
			if (rock):
				suffix1 = "_%03d" % (i+1)				
			else:
				suffix1 = "_" + str(i+1)	#If 'ccdScan', do not add leading zeroes

		for j in range(0,N,1):
			suffix2 = ""
			if (N > 1):
				suffix2 = "_%03d" % (j+1)   #Only append count number if count > 1
			
			print `fileName` + "-" + `suffix1` + "-" + `suffix2`	
			fullFilename = fileName + suffix1 + suffix2
			
			#If file already exists, check if can be overwritten
			overwriteFlag = updateFileOverwriteFlag("/dls/i15/data/currentdir" + "/" + fullFilename + ".img", overwriteFlag)
			if (overwriteFlag == 'n' or overwriteFlag == 'na'):
				break
			
			print "Starting file :" + fullFilename
			thisFile = ""
			if (doubleScan):
				thisFile = ccdDoubleScanElement(exposureTime, fullFilename, axis, A, B, readOutDelay)
			else:
				thisFile = ccdScanElement(exposureTime, fullFilename, axis, A, B)
				#thisFile = ccdScanElement_noSync(exposureTime, fullFilename, axis, A, B)
				
			print "================================================"
			sleep(readOutDelay)					#Wait for CCD data readout
			ruby.flush()
			filesCreated.append("/dls/i15/data/currentdir" + "/" + thisFile)
			simpleLog ( "============PAUSE FOR DETECTOR READOUT==========" )

	#Set back to initial Pos.
	closeEHShutter()
	setMaxVelocity(axis)						#Max velocity to move...
	moveMotor(axis, initialPosition)					#...back to initial Position.
	simpleLog ( "================SCRIPT COMPLETE=================")
	return filesCreated

######################################################################################

def ccdScanElement(exposureTime, fileName, axis, A, B):
	"""
	Called from ccdScan(). 
	Scans from A to B in exposureTime seconds, and takes a ccd exposure using XPS position compare.
	"""
	checkConfigured()
	velocity = float(abs(B-A))/float(exposureTime)		 #Calculate velocity
	simpleLog( "Velocity set to " + str(velocity) + " deg/s.")
	simpleLog( "Scanning from " + str(A) + "->" + str(B) + " in " + str(exposureTime) + " seconds.")

	runUp = (velocity/10)				                #Acceleration Runup Allowance (degrees)
	simpleLog("Run up:" + `runUp`)
	setMaxVelocity(axis)					                    #Max velocity to move...
	deactivatePositionCompare() #Prevent false triggers when debounce on
	moveMotor(axis, A-runUp)						            #...to start position (A).
	geometry = scanGeometry(axis, velocity, A, B)		        #Set up XPS scan, header geometry, and set scan velocity.
	fullFileName = ruby.exps(fileName, exposureTime, geometry)	#Set ruby up to trigger from XPS position compare signal.
	moveMotor(axis, B+runUp)						            #Scan to B.
	deactivatePositionCompare()				                    #Exposure complete, deactivate postion compare.

	setMaxVelocity(axis)			   # reset to max velocity

	return fullFileName
######################################################################################

def ccdScanElement_noSync(exposureTime, fileName, axis, A, B):
	"""
	Same as ccdScanElement, but exposure not synchronised with fast shutter
	"""
	checkConfigured()
	simpleLog( "Move motor to start at max velocity")
	setMaxVelocity(axis)											#Max velocity to move...
	moveMotor(axis, A)									#...to start position (A).

	velocity = float(abs(B-A))/float(exposureTime)
	simpleLog( "Velocity set to " + str(velocity) + " deg/s.")
	
	simpleLog( "Scanning (unsync'd) from " + str(A) + "->" + str(B) + " in " + str(exposureTime) + " seconds.")

	setVelocity(axis, velocity)
	fullFileName = ruby.expose(exposureTime, fullFilename)
	moveMotor(axis, B)
	
	setMaxVelocity(axis)			   # reset to max velocity

	return fullFileName
######################################################################################
def ccdDoubleScanElement(exposureTime, fileName, axis, A, B, readOutDelay):
	"""
	Called from ccdScan(). 
	Scans from A to B in exposureTime seconds, and takes a ccd exposure using XPS position compare.
	Then scans from B to A for a second image, correlates the two and subtracts the dark image 
	"""
	checkConfigured()
	readOutDelay = 1.5*readOutDelay
	
	velocity = float(abs(B-A))/float(exposureTime)		 #Calculate velocity
	simpleLog( "Velocity set to " + str(velocity) + " deg/s.")

	# Take first image while moving motor from A to B
	simpleLog( "Scanning once from " + str(A) + "->" + str(B) + " in " + str(exposureTime) + " seconds.")
	runUp = (velocity/10)
	setMaxVelocity(axis)
	deactivatePositionCompare() #Prevent false triggers when debounce on
	moveMotor(axis, A-runUp)
	geometry = scanGeometry(axis, velocity, A, B)
	ruby.expA(getIntensity(), geometry, fileName)	
	moveMotor(axis, B+runUp)					
	simpleLog( "Wait for read out: " + str(exposureTime + readOutDelay))		# imageA
	sleep(exposureTime + readOutDelay)
	
	# Pause, then take second image while moving from B to A, correlate and subtract dark
	simpleLog( "Scanning back from " + str(B) + "->" + str(A) + " in " + str(exposureTime) + " seconds.")
	fullFileName = ruby.expB(fileName, exposureTime)	   # (N.B. geometry not passed as position compare already set up)
	simpleLog( "Wait for read out: " + str(exposureTime + 2*readOutDelay))	# imageB and correlated image
	sleep(exposureTime + 2*readOutDelay)
	
	moveMotor(axis, A-runUp)	
	deactivatePositionCompare()							 
	
	return fullFileName
