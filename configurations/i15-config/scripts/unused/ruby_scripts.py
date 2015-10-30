from time import sleep
import sys
import struct
from gda.analysis.io import CrysalisLoader
from gda.analysis import ScanFileHolder, Plotter, RCPPlotter

		
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog

class ISCCD:

	def __init__(self,ccd):
		self.time = 2
		self.fileName = "test"
		self.path = "X:/currentdir/"
		self.suffix = ".img"
		self.binning = 1
		self.detector = ccd
		self.verbose = False
		
		self.corrections = ["repair","floodm", "unwarp", "floodp"]
		self.correctionNames = { "repair": "repair correction", "floodm": "flood mscalar correction", "unwarp" :"unwarp correction", "floodp": "flood poly correction"}
		self.correctionVals = { "repair": True, "floodm": False, "unwarp" :False, "floodp": False}

		self.detectorDistance = 0
		
		self.exportAll = 0
		self.subtractDark = 0
		self.exportCompressed = 0

################# SETUP COMMANDS ####################

# Set directory from command line
	def setDir(self, directory):
		"""
		Sets the CCD data directory. 
		Examples include: "C:/Data/ee1/" and "X:/data/2008/ee0/".
		"""
		simpleLog ("Path currently:  " + self.path )
		self.path = directory.replace("/dls/i15/data/","X:/y")
		simpleLog ("Path changed to: " + self.path )
		return

# Set directory from command line
	def getDir(self):
		"""
		Gets the CCD data directory. 
		"""
		simpleLog ("CCD path currently:  " + self.path )
	
	def getFileName(self,fileName):
		return fileName+self.suffix

# Set directory from command line
#	def setXDir(self, directory):
#		"""
#		Sets the CCD data directory to i15 storage server 'directory' in the current year in the /dls/i15/data dir.
#		"""
#		simpleLog ("Path currently " + self.path )
#		currDir = self.path
#		currentTime = time.localtime()
#		currentYear = currentTime[0]
#		self.path = "X:/data/" + str(currentYear) + "/" + directory
#		simpleLog ("CCD path changed to " + self.path)
##		self.path = currDir

# Set Bin (default is 2).
	def setBin(self, binning):
		if  binning < 1 or binning > 3:
			raise Exception("Binning can only be 1, 2 or 3")
		simpleLog ("Binning is currently " + str(self.binning) )
		self.binning = binning
		simpleLog ("CCD binning set to " + str(self.binning) )

# Get Bin (default is 2).

	def getBin(self):
		return self.binning

	def getReadOutDelay(self):
		"""
		setReadOutDelay() sets the ccd readout sleep for the current binning.
		Binning schemes 1x1, 2x2, 4x4 are currently implemented.
		"""
		bin = self.getBin()
		if (bin==4):
			readOutDelay=2.5
		if (bin==3):
			readOutDelay=2.5
		if (bin==2):
			readOutDelay=3.5
		if (bin==1):
			readOutDelay=10
		simpleLog( "Binning is currently "+str(bin)+"x"+str(bin)+"=> readout time of "+str(readOutDelay))
		return readOutDelay

	def applyCorr(self, correction):
		self.switchCorrection(correction, True)

	def removeCorr(self, correction):
		self.switchCorrection(correction, False)

	def switchCorrection(self, correction, on):
		if (not self.correctionNames.keys().__contains__(correction)):
			simpleLog("Incorrect usage - please type:")
			simpleLog(self.name + ".applyCorr(correction) / " + self.name + ".removeCorr(correction) where correction is one of:")
			for corr in self.corrections:
				simpleLog(" '" + corr + "': " + self.correctionNames[corr])
		else:
			self.correctionVals[correction] = on
			if (on):
				simpleLog("--> Correction '" + self.correctionNames[correction] + "' applied")
			else:
				simpleLog("--> Correction '" + self.correctionNames[correction] + "' removed")
		
		self.showCorrections()

	def showCorrections(self):
		corrs = []
		for corr in self.corrections:
			if (self.correctionVals[corr]):
				corrs.append(self.correctionNames[corr])
		
		if (len(corrs) == 0):
			simpleLog("No corrections currently applied")
		else:
			simpleLog("Corrections currently applied:")
			simpleLog(str(corrs))

	def getDetectorDist(self):
		return self.detectorDistance

	def setDetectorDist(self, newDist, file=""):
		"""
		Image file is optional: if present, detector distance in file header will be updated too.
		E.g. setDetectorDist(122, "myFile")
		"""
		simpleLog("Detector distance was: " + str(self.detectorDistance) )
		self.detectorDistance = newDist
		simpleLog("Detector distance is now: " + str(self.detectorDistance) )
		
		if (file != ""):
			self.runCommand('call ' + self.setDetectorDist_script + ' "' +  self.path + "/" +  file + '" ' + str(self.detectorDistance))
			simpleLog("Detector distance set in header on: " + file)

	def getFloodFile(self):
		simpleLog("Relative file name on IS machine (at C:\IS_v18A\) for flood field correction:")
		return self.floodFile

	def setFloodFile(self, newFile):
		simpleLog("Flood field correction file was: " + self.floodFile )
		self.floodFile = newFile
		self.runCommand('call ' + self.setFloodFile_script + ' "' + self.floodFile + '"')
		simpleLog("File is now: " + self.floodFile + " (at C:\IS_v18A\)")

	def getFileParametersString(self):
		"""
		Returns string of corrections to be used, plus 'exportAll', 'subtractDark' and 'exportCompressed'. These parameters can 
		then be passed to IS scripts in one go.
		"""
		paramStr = ""
		for corr in self.corrections:
			if self.correctionVals[corr]:
				paramStr += '1' + " "
			else:
				paramStr += '0' + " "
		
		return paramStr + `self.exportAll` + " " + `self.subtractDark` + " " + `self.exportCompressed`
	
	def getExportAll(self):
		if (self.exportAll == 1):
			simpleLog("All intermediate images generated by scripts will be exported" )
		else:
			simpleLog("Intermediate images generated by scripts will not be exported" )

	def setExportAll(self, newExportAll):
		if (newExportAll != 0 and newExportAll != 1):
			simpleLog("Usage: 1 = export all intermediate images, 0 = don't export")
		else:
			self.exportAll = newExportAll
			self.getExportAll()

	def getSubtractDark(self):
		if (self.subtractDark == 1):
			simpleLog("Correlated dark will be subtracted from all exposures" )
		else:
			simpleLog("Correlated dark will not be subtracted from exposures" )

	def setSubtractDark(self, newSubtractDark):
		if (newSubtractDark != 0 and newSubtractDark != 1):
			simpleLog("Usage: 1 = subtract correlated dark from all exposures, 0 = don't subtract")
		else:
			self.subtractDark = newSubtractDark
			self.getSubtractDark()

	def getExportCompressed(self):
		if (self.exportCompressed == 1):
			simpleLog("Images will be exported in compressed format" )
		else:
			simpleLog("Images will be exported in uncompressed format" )

	def setExportCompressed(self, newExportCompressed):
		if (newExportCompressed != 0 and newExportCompressed != 1):
			simpleLog("Usage: 1 = export images in compressed format, 0 = export images uncompressed")
		else:
			self.exportCompressed = newExportCompressed
			self.getExportCompressed()

	def info(self):
		simpleLog("----------------------------")
		self.getDir()
		simpleLog("Binning: " + str(self.binning))
		self.showCorrections()
		simpleLog("Flood field correction file: " + self.floodFile)
		simpleLog("Detector distance: " + str(self.detectorDistance))
		self.getExportAll()
		self.getSubtractDark()
		self.getExportCompressed()
		simpleLog("----------------------------")

################# SHUTTER COMMANDS ####################

	def connectIfNeeded(self):
		if not self.detector.isConnected():
			self.connect()

# Open the shutter. This typically takes 0.055 seconds to execute.
	def openS(self):
		"""
		Open fast shutter
		"""
		self.connectIfNeeded()
		self.detector.openShutter() 
		simpleLog ("Fast Shutter told to Open" )

# Close the shutter. This typically takes 0.042 seconds to execute.
	def closeS(self):
		"""
		Close fast shutter
		"""
		self.connectIfNeeded()
		self.detector.closeShutter()
		simpleLog ("Fast Shutter told to Close" )

	def getS(self):
		self.connectIfNeeded()
		status = self.detector.shutter()
		simpleLog ("Shutter status = " + `status` )
		return status


################# CONNECTION COMMANDS ####################

# Kill the detector connection.
	def kill(self):
		self.detector.runScript("logout gda")
		self.detector.disconnect()
		self.detector.runScript("logout gda")

# Reset the Detector and read electronics.
	def reset(self):
		self.connectIfNeeded()
		self.detector.runScript('Detector reset')
		self.detector.runScript('f60 reset')
		simpleLog ("Reset Sent..." )

# Auto connect GDA at login.
	def connect(self):
		"""
		Connect GDA to IS on OD PC (No, I'm not actively trying to use acronyms).
		eg/ ruby.connect()
		"""
#		host = "i15-control"
		host = "172.23.115.193"
		try:
			self.detector.connect(host)
			simpleLog ("Setup GDA-IS Connection: 						[Done]"  )
		except:
			type, exception, traceback = sys.exc_info()
			try:
				handle_messages.log(None, self.name + ".connect error -", type, exception, traceback, False) 		
				simpleLog ("Setup GDA-IS Connection: 						[Fail]" ) 
				simpleLog ("GDA-IS Connection Diagnostics..." )
				self.detector.runScript("logout gda")
				self.detector.disconnect()
				sleep(5)
				self.detector.runScript("logout gda")
				self.detector.connect(host)
				simpleLog ("Setup GDA-IS Connection:						[Done]" ) 
			except:
				type, exception, traceback = sys.exc_info()
				msg = "GDA could not connect to IS.\n" + \
				"Ensure IS is running on 172.23.115.193 and there are no existing telnet sessions open.\n" + \
				"Then run command " + self.name + ".connect()"
				handle_messages.log(None, msg, type, exception, traceback, True) 		
# Resetting namespace causes localStation.py to run again recursively. Which has caused much confusion in the past.
# Instead issue a message to the logger.				
#				simpleLog ("Reseting GDA Client..."
#				reset_namespace

################# METHODS CALLING IS SCRIPTS ####################
# Following methods call IS scripts which can be found on 172.23.115.193 in C:\IS18A\userscripts\

	def runCommand(self, command):
		""" Connect to IS if required, stop any currently running scripts and run command """
		self.connectIfNeeded()
#		self.detector.runScript('api script stop')		# stop any scripts that might still be running on api object
#		self.detector.runScript('cr script stop')		# stop any scripts that might still be running on cr object
		#simpleLog("runCommand:" + command)
		self.detector.runScript(command)
#		self.detector.readInputUntil("blah blah - this should be removed")

	def expose(self,time,fileName):
		"""
		Expose ruby for given time saving in fileName using current binning and applying current corrections
		E.g. expose(5, "X:/currentdir/test.img")
		"""
		thisFile = self.getFileName(fileName)
		paramStr = self.getFileParametersString()
		self.runCommand('call ' + self.expose_script + ' '+str(time)+' "'+  self.path +"/"+ thisFile +'" '+str(self.binning) + ' ' + paramStr)
		return thisFile

	def exps(self,fileName,time,geometry):
		"""
		Expose ruby for given time to given file while scanning through geometry (using current binning and corrections)
		E.g. exps("X:/currentdir/test.img", 5, geometryString)
		
		[N.B. THIS METHOD IS NO LONGER CALLED BY rubyScan - INSTEAD expsSaveIntensityA FOLLOWED BY expsSaveIntensityB]
		"""
		thisFile = self.getFileName(fileName)
		paramStr = self.getFileParametersString()
		self.runCommand('call ' + self.smi_exps_script + ' "' + self.path + "/" + thisFile  + '" ' + str(time) + ' ' + geometry + ' ' + str(self.binning) + ' ' + paramStr)
		return thisFile

	def expsSaveIntensityA(self, exposureTime):
		self.runCommand('call ' + self.expsSaveIntensityA_script + ' ' + str(self.binning) + ' ' + str(exposureTime))

	def expsSaveIntensityB(self,fileName,time,geometry, i0_val):
		"""
		Expose ruby for given time to given file while scanning through geometry (using current binning and corrections). First IS script
		takes and saves exposure, while the second one updates header with intensity over scan and geometry, and exports file 
		E.g. exps("X:/currentdir/test.img", 5, geometryString, intensityIntegral)
		"""
		"""
		Setup mca to average every .1s with ROI setuo to cover all 200000 points which gives a max exposure to 20000s
		"""
		sleep(.2)
		thisFile = self.getFileName(fileName)
		paramStr = self.getFileParametersString()
		self.detector.readInputUntil("api:IMAGE TAKEN")
		self.detector.flush()
		self.runCommand('call ' + self.expsSaveIntensityB_script + ' "' + self.path + "/" + thisFile  + '" ' + geometry + ' ' + paramStr + ' ' + `i0_val` + ' ' + `time` + ' ' + `self.binning`)
		self.detector.readInputUntil("api:IMAGE EXPORTED")
		self.detector.flush()
		return thisFile

	def expsSaveIntensityB2(self, fileName, time, geometry, i0_val,
			multifactor, final_filename, run_filename, experiment_name):
		"""
		Expose ruby for given time to given file while scanning through geometry (using current binning and corrections). First IS script
		takes and saves exposure, while the second one updates header with intensity over scan and geometry, and exports file 
		E.g. exps("X:/currentdir/test.img", 5, geometryString, intensityIntegral)
		"""
		"""
		Setup mca to average every .1s with ROI setuo to cover all 200000 points which gives a max exposure to 20000s
		"""
		sleep(.2)
		thisFile = self.getFileName(fileName)
		paramStr = self.getFileParametersString()
		self.detector.readInputUntil("api:IMAGE TAKEN")
		self.detector.flush()
		command = 'call %s "%s" %s %s ' % (
			self.expsSaveIntensityB2_script, self.path + "/" + thisFile,
			geometry, paramStr) + `i0_val` + ' ' + `time` + ' ' + \
			`self.binning` + ' 220000 %f "%s" "%s" "%s"' % (
			multifactor, final_filename, run_filename, experiment_name)
		simpleLog (command)
		self.runCommand(command)
		
		self.detector.readInputUntil("api:IMAGE EXPORTED")
		self.detector.flush()
		return thisFile

	def expA(self, intensity, geometry, fileName):
		"""
		Part1 of double scan: expose ruby for given time scanning through geometry and take off correlated dark image if it exists, 
		saving the intensity integral 
		"""
		# TODO: NEEDS TO BE SORTED OUT TO SAVE INTENSITY IN THE SAME WAY AS A SINGLE SCAN
		
		paramStr = self.getFileParametersString()
		self.runCommand('call ' + self.smi_expA_script + ' ' + str(self.binning) + ' ' + str(intensity) + ' ' + geometry + ' ' + str(self.time) + ' ' + self.path + fileName + ' ' + paramStr)

	def expB(self, fileName, exposureTime):
		"""
		Part2 of double scan: expose ruby for given time scanning through geometry and take off correlated dark image if it exists.
		Correlate image with image obtained by expB and export.
		"""
		# TODO: NEEDS TO BE SORTED OUT TO SAVE INTENSITY IN THE SAME WAY AS A SINGLE SCAN
		
		thisFile = self.getFileName(fileName)
		self.time = exposureTime
		paramStr = self.getFileParametersString()
		self.runCommand('call ' + self.smi_expB_script + ' "' + self.path + fileName  + '" ' + str(self.binning) + ' ' + str(self.time) + ' ' + paramStr + ' ' + str(intensityIntegral.getPosition()))
		return thisFile

	def xpsSync(self, dummyFileName, timeout):
		"""
		Opens the ruby fast shutter synchronised with the movement of the motor set in ccdScanMechanics.scanGeometry() (using XPS). 
		Used to synchronise scans with mar, pilatus, etc., producing a dummy ruby file. 
		"""
		self.runCommand('call ' + self.smi_xps_script + ' "C:/Data/SyncDump/' + dummyFileName + self.suffix + '"' + ' ' + '"' + str(timeout)+ '"')

	def runlistAdd(self, scantype, domegaindeg, ddetectorindeg, dkappaindeg,
			dphiindeg, dscanstartindeg, dscanendindeg, dscanwidthindeg,
			dscanspeedratio, dwnumofframes, dwnumofframesdone,
			dexposuretimeinsec, experiment_name, run_filename):
		"""
		Create a new runlist or add a new run to the current runlist
		"""
		command ='call %s %i %f %f %f %f %f %f %f %f %i %i %f "%s" "%s"' % (
			self.runlistAdd_script, scantype, domegaindeg, ddetectorindeg,
			dkappaindeg, dphiindeg, dscanstartindeg, dscanendindeg,
			dscanwidthindeg, dscanspeedratio, dwnumofframes, dwnumofframesdone,
			dexposuretimeinsec, experiment_name, run_filename)
		simpleLog (command)
		self.runCommand(command)

	def importAndCorrect(self, fileName, exportSuffix):
		"""
		Import file, set current ruby detector distance in header, apply currently set corrections and export to file: 
		fileName + exportSuffix
		E.g.  importAndCorrect("x:/testsDec18/ee863_p03_1_1", "_corrected"):
		"""
		self.runCommand('call ' + self.importAndCorrect_script + ' "' + fileName + '" ' + self.getFileParametersString() + ' ' + str(self.detectorDistance) + ' "' + exportSuffix + '"')

	def exportUpdatedFloodFile(self, polyCoefficients, exportFileName):
		"""
		Imports the current flood field correction file self.floodFile, sets the polynomial coefficients within the 
		header and exports to file path exportFileName
		E.g. exportUpdatedFloodFile( [0.9809, 0.0, 2.63e-5, 0.0, -9.57e-9], "C:\newFloodFieldFile.ffiinf")
		"""
		polyStr = polyCoefficients.join(" ")
		self.runCommand('call ' + self.exportUpdatedFloodFile_script + ' "' + self.floodFile + '" ' + polyStr + ' "' + exportFileName + '"')

################# SCRIPTS FOR CREATION OF FLOOD FIELD CORRECTION FILE ##############
# (used in ccdFloodCorrections.py)
#
# Create initial image
	def correctFlood1(self, exposureTime, subDarksAtEnd, filename):
		"""
		Creates initial image.
		"""
		self.time = exposureTime
		self.fileName = filename
		self.runCommand('call ' + self.correctFlood1_script + ' ' + str(self.time) + ' ' + str(self.binning) + ' "' + self.path + self.fileName + '" ' + self.getFileParametersString() + ' ' + subDarksAtEnd)

	def correctFlood2(self, exposureTime, subDarksAtEnd, filename):
		"""
		Create another image, correlate with one taken in correctFlood1 and add to sum
		"""
		self.time = exposureTime
		self.fileName = filename
		self.runCommand('call ' + self.correctFlood2_script + ' ' + str(self.time) + ' ' + str(self.binning) +' "' + self.path + self.fileName + '" ' + self.getFileParametersString() + ' ' + subDarksAtEnd)

# Unwarp summed image and export 
	def correctFlood3(self, filename, noOfDarksToSubtract, exposureTime):
		"""
		Apply corrections 'poly mscalar' and 'unwarp' to summed image if set (each image has already been 'repaired'), and export.
		"""
		self.time = exposureTime
		self.fileName = filename
		self.runCommand('call ' + self.correctFlood3_script + ' "' + self.path + self.fileName + '"' + ' ' + noOfDarksToSubtract + ' ' + str(self.time) + ' ' + self.getFileParametersString() + ' ' + str(self.binning))

	def takeDarksAndCorrelate(self, exposureTime, filename):
		"""
		Take 2 dark images and correlate.
		"""
		self.time = exposureTime
		self.fileName = filename
		#self.runCommand('call correlateDark ' + str(self.time) + ' ' + str(self.binning) + ' ' + str(self.exportAll) + ' "' + self.path + '/' + self.fileName + '" ' + str(override))
		self.runCommand('call ' + self.correlateDark_script + ' ' + str(self.time) + ' ' + str(self.binning) + ' "' + self.path + '/' + self.fileName + '" ' + ' ' + self.getFileParametersString())
		#self.detector.readInputUntil("DARKS TAKEN")

##################################################################################

	def readImage(self, filename=None):
		"""Read image until timeout"""
		nativeSock = None
		timeout = None
		file = None
		try:
			try:
				if filename != None:
					file = open(filename,"wb")
				datalen = 0
				nativeSock = self.detector.getODCCDNativeSock()
				timeout = nativeSock.getSocketTimeOut()
				nativeSock.setSocketTimeOut(1000);
				self.detector.readBinaryFrameUntilData()
#				print self.detector.mBinaryHeader
				dataName = self.detector.getDataName()
				print dataName
				if( not dataName.startswith("Image'integer") ):
					raise "dataName is invalid  - " + dataName
				data = self.detector.readBinaryFrame()
				if file != None:
					# write height and width
					if dataName == "Image'integer(array(1042,1042))":
						dim = 1042
					elif dataName == "Image'integer(array(2084,2084))":
						dim = 2084
					elif dataName == "Image'integer(array(695,695))":
						dim = 695
					elif dataName == "Image'integer(array(524,524))":
						dim = 524
					else:
						raise Exception("Unknown size for "+dataName) 
					d = struct.pack("<l",dim)
					file.write(d)
					file.write(d)
					data.tofile(file)
					datalen += len(data)
				while True:
					self.detector.readBinaryFrameUntilData()
#					print self.detector.mBinaryHeader
					dataName = self.detector.getDataName()
					if(dataName != "Image"):
						raise "dataName != Image - " + dataName
					data = self.detector.readBinaryFrame()
					if file != None:
						data.tofile(file)
					datalen += len(data)
					if( self.detector.mBinaryHeader.mFlags>>12 == 4):
						break
			except:
				#java.net.SocketTimeoutException
				type, exception, traceback = sys.exc_info()
				handle_messages.log(None, self.name + ".readImage error -", type, exception, traceback, True)		
		finally:
			if nativeSock != None:
				nativeSock.setSocketTimeOut(timeout)
			if file != None:
				file.close()
		simpleLog("Successful read image of size " + `datalen`)

	def plot(self,filename=""):
		simpleLog("Plotting " + self.name + " image " + filename)
		data = ScanFileHolder()
		data.load(CrysalisLoader(filename))
		Plotter.plotImage("Data Vector",data[0])
		RCPPlotter.imagePlot("Plot 1",data[0])

	def flush(self):
		#simpleLog(self.name + " flush, please wait...")
		datalen = self.detector.flush()
		#simpleLog(self.name + " socket flushed. no. of chars read = "+ `datalen`)


class Ruby(ISCCD):
	
	def __init__(self,ccd):
		ISCCD.__init__(self, ccd)
		self.name = "ruby"
		# IS scripts:
#		self.setDetectorDist_script        = "setDetectorDist"
#		self.setFloodFile_script           = "setFloodFile"
#		self.expose_script_script          = "expose"
#		self.smi_exps_script_script        = "smi_exps"
#		self.expsSaveIntensityA_script     = "smi_exps1" 
#		self.expsSaveIntensityB_script     = "smi_exps2"
#		self.smi_expA_script               = "smi_expA"
#		self.smi_expB_script               = "smi_expB"
#		self.smi_xps_script                = "smi_xps"
#		self.importAndCorrect_script       = "importAndCorrect"
#		self.exportUpdatedFloodFile_script = "exportUpdatedFloodFile"
#		self.correctFlood1_script          = "correctFlood1"
#		self.correctFlood2_script          = "correctFlood2"
#		self.correctFlood3_script          = "correctFlood3"
#		self.correlateDark_script          = "correlateDark"

#		self.floodFile = "lib/bin/crysalis/floodmo_ruby_6_120905.ffiinf"

class Atlas(ISCCD):
	
	def __init__(self,ccd):
		ISCCD.__init__(self, ccd)
		self.name = "atlas"
		# IS scripts:
		self.setDetectorDist_script        = "setDetectorDist"
		self.setFloodFile_script           = "setFloodFile_atlas"
		self.expose_script                 = "expose_atlas"
		self.expsSaveIntensityA_script     = "smi_exps1_atlas" 
		self.expsSaveIntensityB_script     = "smi_exps2_atlas"
		self.expsSaveIntensityB2_script     = "smi_exps2b_atlas"
		self.correlateDark_script          = "correlateDark_atlas"
		self.smi_xps_script                = "smi_xps_atlas"
		self.runlistAdd_script             = "runlistAdd"

		self.floodFile = "lib/bin/crysalis/floodmo_a_80_calib_090311.ffiinffit"

	def exps(self,fileName,time,geometry):
		raise "Atlas support for exps() has not been tested."

	def expA(self, intensity, geometry, fileName):
		raise "Atlas support for expA() has not been tested."
		
	def expB(self, fileName, exposureTime):
		raise "Atlas support for expB() has not been tested."

	def importAndCorrect(self, fileName, exportSuffix):
		raise "Atlas support for importAndCorrect() has not been tested."

	def exportUpdatedFloodFile(self, polyCoefficients, exportFileName):
		raise "Atlas support for exportUpdatedFloodFile() has not been tested."

	def correctFlood1(self, exposureTime, subDarksAtEnd, filename):
		raise "Atlas support for correctFlood1() has not been tested."
#
	def correctFlood2(self, exposureTime, subDarksAtEnd, filename):
		raise "Atlas support for correctFlood2() has not been tested."

	def correctFlood3(self, filename, noOfDarksToSubtract, exposureTime):
		raise "Atlas support for correctFlood3() has not been tested."

	def openS(self):
		"""
		Open fast shutter
		This typically takes 0.055? seconds to execute.
		"""
		self.connectIfNeeded()
		#self.runCommand('ppcpnp misc shutter = on') # NO!
		self.runCommand('call sh 1') # YES!
		simpleLog ("Fast Shutter told to Open (ignored if EXT. not Atlas)" )

	def closeS(self):
		"""
		Close fast shutter
		This typically takes 0.042? seconds to execute.
		"""
		self.connectIfNeeded()
		#self.runCommand('ppcpnp misc shutter = off') NO!
		#self.runCommand('cmd=ppcpnp misc shutter = off') NO!
		self.runCommand('call sh 0') # YES!
		simpleLog ("Fast Shutter told to Close (ignored if EXT. not Atlas)" )

	def getS(self):
		self.connectIfNeeded()
		# TODO: Work out how to get find out whether the shutter is open
		# on the Atlas. For now, just assume it is closed.
		status = 'CLOSED' #self.detector.shutter()
		simpleLog ("Shutter status = " + `status` )
		return status

	def clearError(self):
		"""
		Clear error by deleting the last failed image acquisition.
		"""
		self.connectIfNeeded()
		# One side effect of calling setup_node is that if the node exists, it
		# gets deleted first. Deleting the node removes it's invalid state.
		self.runCommand('call echo "Clearing image data"')
		self.runCommand('call setup_node "/ppcdirpnp/data/Image"')
		simpleLog ("IS told to clear error by deleting the last failed image "+
			"acquisition.")