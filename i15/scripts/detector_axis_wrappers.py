import ruby_scripts
import pd_pilatus
import os
from time import sleep
from time import clock
from time import time
from threading import Thread
from gdascripts.messages.handle_messages import simpleLog
from gda.jython.commands.GeneralCommands import pause
from operationalControl import moveMotor
from ccdScanMechanics import setMaxVelocity
from ccdScanMechanics import deactivatePositionCompare
from ccdScanMechanics import scanGeometry
from ccdScanMechanics import setVelocity
from ccdAuxiliary import incrementCCDScanNumber
from ccdAuxiliary import openCCDShield, closeCCDShield
from marAuxiliary import checkMarIsReady
from marAuxiliary import openMarShield, closeMarShield
from marAuxiliary import incrementMarScanNumber
from marAuxiliary import getNextMarScanNumber
from marAuxiliary import marErase
from shutterCommands import openEHShutter#, closeEHShutter, getShutterStatus, sh
from gda.device.scannable import PseudoDevice
from gdascripts.parameters import beamline_parameters
from util_scripts import doesFileExist
from dataDir import getDir, setFullUserDir#, setDir 
from gda.util import VisitPath
from gda.device.detector.odccd import ModifyCrysalisHeader
from gda.device.detector.mar345 import Mar345Detector
from scannables.detectors.perkinElmer import PerkinElmer
from gda.data.fileregistrar import FileRegistrarHelper
from gda.epics import CAClient
from glob import glob

class DetectorAxisWrapper(PseudoDevice):
	def __init__(self, pause, prop_threshold, exposureTime):
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.pause = pause
		self.prop_threshold =prop_threshold
		self.exposureTime = float(exposureTime)
		
		self.prop = jythonNameMap.qbpm1total
		self.feabsb = jythonNameMap.feabsb
		self.feabsb_pos = self.feabsb.getPosition()
		self.fmfabsb = jythonNameMap.fmfabsb
		self.fmfabsb_pos=self.fmfabsb.getPosition()
		
		self.caclient = CAClient()
		self.max_time_to_injection = exposureTime + 1.
		self.wait_after_injection = exposureTime + 4.

	def absorberOpen(self):
		self.feabsb_pos = self.feabsb.getPosition()
		return self.feabsb_pos == 'Open'

	def fastMaskOpen(self):
		self.fmfabsb_pos=self.fmfabsb.getPosition()
		return self.fmfabsb_pos == 'Open'

	def waitForAbsorberAndMaskOpen(self):
		delayMinutes=20
		reasons = []
		
		absorberOpen = self.absorberOpen()
		fastMaskOpen = self.fastMaskOpen()
		if (absorberOpen and fastMaskOpen):
			return
		
		if not absorberOpen:
			reasons.append("absorber is " + self.feabsb_pos)
		if not fastMaskOpen:
			reasons.append("fast mask is " + self.fmfabsb_pos)
		simpleLog("Paused because " + " and ".join(reasons))
		
		minutesRemain = delayMinutes
		secondsRemain = 60
		
		while(not (absorberOpen and fastMaskOpen) or minutesRemain > 0):
			sleep(1)
			absorberOpen_new = self.absorberOpen()
			fastMaskOpen_new = self.fastMaskOpen()
			# If nothing changed, keep counting down/showing updates.
			if absorberOpen == absorberOpen_new and fastMaskOpen == fastMaskOpen_new:
				if absorberOpen and fastMaskOpen:
					if secondsRemain == 0:
						secondsRemain = 60 
						minutesRemain -= 1
						print "%d" % (minutesRemain),
					else:
						secondsRemain -= 1
						if not (secondsRemain % 30):
							print ""
						else:
							print ".",
				else:
					print "!",
			else: # Something changed
				reasons = []
				if not absorberOpen == absorberOpen_new:
					reasons.append("absorber is now " + self.feabsb_pos)
				if not fastMaskOpen == fastMaskOpen_new:
					reasons.append("fast mask is now " + self.fmfabsb_pos)
				simpleLog("\n" + " and ".join(reasons))
				
				absorberOpen = absorberOpen_new
				fastMaskOpen = fastMaskOpen_new
				
				if absorberOpen and fastMaskOpen:
					minutesRemain = delayMinutes
					secondsRemain = 60
					simpleLog("Both absorber and fast mask now open." +
						"\nStarting %d minute timer..." % minutesRemain)
		#simpleLog("\nTimer completed...")

	def waitForPropCounter(self):
		pause_prompt = True	
		while (self.prop() < self.prop_threshold):
			if pause_prompt:
				simpleLog("Paused because beam proportional counter " +
					"(%f)" % self.prop() + " is below threshold level " +
					"(%f)" % self.prop_threshold)
				pause_prompt = False
			sleep(1)
			print ".",
		if not pause_prompt:
			print ""

	def time_to_injection(self):
		return float(self.caclient.caget("SR-CS-FILL-01:COUNTDOWN"))

	def waitForInjection(self):
		time_to_injection = self.time_to_injection()
		
		if (time_to_injection < self.max_time_to_injection):
			simpleLog("Only %fs to top-up..." % time_to_injection)
			
			while (time_to_injection < self.max_time_to_injection):
				sleep(1)
				time_to_injection = self.time_to_injection()
				print time_to_injection,
			
			simpleLog("\nSettle %fs after top-up..." %
				self.wait_after_injection)
			
			while (self.wait_after_injection > 0):
				if self.wait_after_injection < 1:
					sleep(self.wait_after_injection)
				else:
					sleep(1)
				print ".",
				self.wait_after_injection -= 1
			print ""

	def preExposeCheck(self):
		if self.pause:
			# We should really loop around these until none of them fail.
			self.waitForAbsorberAndMaskOpen()
			self.waitForPropCounter()
			self.waitForInjection()

	def postExposeCheckFailed(self):
		reasons = []
		if self.pause:
			if not self.absorberOpen():
				reasons.append("absorber is " + self.feabsb_pos)
			if not self.fastMaskOpen():
				reasons.append("fast mask is " + self.fmfabsb_pos)
			if (self.prop() < self.prop_threshold):
				reasons.append("beam proportional counter " +
					"(%f)" % self.prop() + " is below threshold level " +
					"(%f)" % self.prop_threshold)
			
			time_to_injection = self.time_to_injection()
			if (time_to_injection < 0):
				reasons.append("top-up (%fs) is negative!" % time_to_injection)
		
		if (len(reasons) > 0):
			simpleLog("\nRepeat collection because " + " and ".join(reasons))
			return True
		return False


class ISCCDAxisWrapper(DetectorAxisWrapper):
	def __init__(self, detector, isccd, exposureTime=0, axis=None, step=None, sync=False, scanDoubleFlag=False, fileName="isccd_scan", noOfExpPerPos=1, diff=0., pause=False, overflow=False, multiFactor=1):
		DetectorAxisWrapper.__init__(self, pause, -11, exposureTime)
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.isccd = isccd
		self.prop = jythonNameMap.prop
		#self.prop = jythonNameMap.dummy1
		self.detector = detector
		self.sync = sync
		self.fileName = fileName
		self.step = float(step)	
		self.noOfExpPerPos = noOfExpPerPos
		self.i0_mca = jythonNameMap.d1_mca
		self.readOutDelay = 1.5 * detector.getReadOutDelay()
		self.exposureNo = 1
		self.fullFileName = ""
		self.scanDoubleFlag = scanDoubleFlag
		self.originalPosition = 0
		self.files = []
		self.ionc1_val = jythonNameMap.ionc1
		self.diff = diff
		self.i0_mca = jythonNameMap.d1_mca
		self.axis = axis
		self.nextScanNo = incrementCCDScanNumber()
		self.done = False
		self.setInputNames(["exposure time"])
		self.overflow=overflow
		self.multiFactor=multiFactor
		self.detectorName="Unknown"
		
		if self.axis:
			self.setOutputFormat(["%2d", "%2d", "%s"])
			self.setExtraNames(["dkphi","file name"])
		else:
			self.setOutputFormat(["%2d", "%s"])
			self.setExtraNames(["file name"])

	def atScanStart(self):
		
		if self.pause:
			simpleLog("Scan will pause if proportional counter " +
					"(%f) is below threshold value " % self.prop() +
					"(%f)." % self.prop_threshold)
		
		userDir = VisitPath.getVisitPath()
		if userDir != getDir():
			simpleLog("Switching to visit directory: " + userDir)
			setFullUserDir(userDir)
			simpleLog("To use a different visit dir a user on that visit must take the baton.")
		
		supportedDir = "X:/currentdir"
		if self.detector.getDir() <> supportedDir:
			simpleLog(self.detectorName  + " doesn't support numeric directory names, using currentdir.")
			self.detector.setDir(supportedDir)
		
		if self.axis:
			self.originalPosition = self.axis()
		
		self.detector.flush()
		openCCDShield()

	def atScanEnd(self):
		if self.axis:
			setMaxVelocity(self.axis)
			self.axis.asynchronousMoveTo(self.originalPosition)
		closeCCDShield()

	def syncExpose(self, position, runUp, velocity, filename, log_message):
		samples = []
		
		if self.sync:
			setMaxVelocity(self.axis)
			deactivatePositionCompare() #Prevent false triggers when debounce on
			moveMotor(self.axis, position - runUp - self.diff)
			
			if self.step>0:
				geometry = scanGeometry(self.axis, velocity, position, position + self.step)
			else:
				geometry = scanGeometry(self.axis, velocity, position + self.step, position)
			
			setVelocity(self.axis, velocity)
			
			self.preExposeCheck()
			
			simpleLog(log_message % self.detectorName)
			self.detector.expsSaveIntensityA(float(self.exposureTime))
			self.axis.asynchronousMoveTo(position + self.step + runUp)
			
			while self.axis.isBusy():
				if float(position) <= float(self.axis()) <= float(position + self.step):
					sleep(0.1)
					samples.append(self.ionc1_val())
					#simpleLog("ionc1="+str(self.ionc1_val()))
			
		else:
			if self.axis:
				setMaxVelocity(self.axis)
				moveMotor(self.axis, position - runUp - self.diff)
				setVelocity(self.axis, velocity)
				self.axis.asynchronousMoveTo(position + self.step + runUp)
				simpleLog("(fast shutter not synchronised with motor)")
			else:
				simpleLog("(%s expose for %fs)" % (self.detectorName, self.exposureTime))
			
			before_time = time()
			self.detector.expose(self.exposureTime, filename)
			after_time = time()
			
			if self.axis:
				while self.axis.isBusy():
					if float(position) <= float(self.axis()) <= float(position + self.step):
						sleep(0.1)
						samples.append(self.ionc1_val())
						#simpleLog("ionc1="+str(self.ionc1_val()))
			else:
				simpleLog("(expose() %f > %f = %fs)" % (
					before_time, after_time, after_time-before_time))
				end_time = after_time + self.exposureTime
				simpleLog("Monitoring ionc1 until %f secs" % end_time)
				
				while after_time < end_time:
					sleep(0.1)
					samples.append(self.ionc1_val())
					after_time = time()
					#simpleLog("ionc1=%f @ %f" % 
					#	(self.ionc1_val(), after_time-before_time))
		
		imonTotal = 0.
		samples = samples[1:-1] # Strip first and last samples
		for s in samples:
			imonTotal = imonTotal + s
		
		imonAverage = 0
		if len(samples)>0 and imonTotal>0:
			imonAverage = imonTotal / (len(samples))
		
		if self.sync:
			self.detector.expsSaveIntensityB(filename, float(self.exposureTime), geometry, 0)
		
		simpleLog("imonAverage="+str(imonAverage) + " " + repr(samples))
		
		return imonAverage

	def performMove(self, position, fast=False):
		velocity = float(abs(self.step)) / float(self.exposureTime)
		
		if self.step > 0:
			runUp = velocity / 10
		else:
			runUp = -1*(velocity / 10)
		
		if self.axis and self.axis.getName() == "dktheta":
			runUp = runUp * 2
		
		for exp in range(self.noOfExpPerPos):
			simpleLog("performMove %r sync %r runUp %r exp %r" %
					(self.axis, self.sync, runUp, exp))
			
			self.isccd.flush()
			filename = self.fileName + "_%01d" % self.nextScanNo + "_%01d" % self.exposureNo
			
			if fast:
				filename += "_fast"
			
			self.fullFileName = self.detector.path + "/" + filename + ".img"
			if fast==False:
				self.exposureNo += 1
			
			imonAverage = self.syncExpose(position, runUp, velocity, filename,
					"Exposing %s")
			
			if self.postExposeCheckFailed():
				imonAverage = self.syncExpose(position, runUp, velocity, filename,
					"Re-exposing %s because of beam loss during expose")
				
			self.files.append(filename)
			linuxFilename = getDir() + "/" + filename + ".img"	
			imonScaledAvg = imonAverage * 100000
			crysalisFile = ModifyCrysalisHeader(linuxFilename)
			names = ["imon1", "imon2", "dexposuretimeinsec"]
			values = [imonScaledAvg,imonScaledAvg,float(self.exposureTime)]
			mod1 = modHeader(crysalisFile, names, values)
			mod1.start()
			deactivatePositionCompare()
			FileRegistrarHelper.registerFile(linuxFilename)

	def rawAsynchronousMoveTo(self, position):
		self.files = []
		if self.overflow:
			normalTime = self.exposureTime
			self.exposureTime = float(normalTime)/float(self.multiFactor)
			simpleLog("performing at fast speed")
			self.performMove(position, True)
			simpleLog("performing at normal speed")
			self.exposureTime=normalTime
			self.performMove(position)
		else:
			self.performMove(position)
		#simpleLog("Completed collection at position %f" % position)

	def rawIsBusy(self):
		return 0

	def rawGetPosition(self):
		if self.axis:
			return [self.exposureTime, self.axis(), self.files]
		else:
			return [self.exposureTime, self.files]


class RubyAxisWrapper(ISCCDAxisWrapper):
	def __init__(self, detector, exposureTime=0, axis=None, step=None, sync=False, scanDoubleFlag=False, fileName="ruby_scan", noOfExpPerPos=1, diff=0., pause=False, overflow=False, multiFactor=1):
		ISCCDAxisWrapper.__init__(self, detector, detector, exposureTime, axis, step, sync, scanDoubleFlag, fileName, noOfExpPerPos, diff, pause, overflow, multiFactor)
		self.setName("ruby wrapper")
		self.detectorName = "Ruby"


class AtlasAxisWrapper(ISCCDAxisWrapper):
	def __init__(self, detector, exposureTime=0, axis=None, step=None, sync=False, scanDoubleFlag=False, fileName="atlas_scan", noOfExpPerPos=1, diff=0., pause=False, overflow=False, multiFactor=1):
		ISCCDAxisWrapper.__init__(self, detector, detector, exposureTime, axis, step, sync, scanDoubleFlag, fileName, noOfExpPerPos, diff, pause, overflow, multiFactor)
		self.setName("atlas wrapper")
		self.detectorName = "Atlas"


class PilatusAxisWrapper(DetectorAxisWrapper):
	def __init__(self, detector, isccd, exposureTime=0, axis=None, step=1, sync=False, fileName="P100K_scan", noOfExpPerPos=1):
		DetectorAxisWrapper.__init__(self, False, -11, exposureTime)
		self.isccd = isccd
		self.detector = detector
		self.sync = sync
		self.fileName = fileName
		self.step = float(step)	
		self.noOfExpPerPos = noOfExpPerPos
		self.axis = axis
		self.originalPosition = 0
		self.files = []
		self.setName("pilatus wrapper")
		
		if self.sync:
			self.setInputNames([axis.getInputNames()[0]])
			self.setOutputFormat(["%6.4f", "%s"])
			self.setExtraNames(["File Name"])
		else:
			self.setInputNames(["Exposure Time"])
			self.setOutputFormat(["%6.4f", "%s"])
			self.setExtraNames(["File Name"])

	def atScanStart(self):
		userDir = VisitPath.getVisitPath() 
		if userDir != getDir():
			simpleLog("User  full user dir to " + userDir)
			setFullUserDir(userDir)
		
		self.isccd.flush()
		
		if self.axis:
			self.originalPosition = self.axis.getPosition()
		if self.detector.getFilePath()[-1:] != "/":
			self.detector.setFilePath(self.detector.getFilePath() + "/")
	
	def atScanEnd(self):
		if self.axis:
			setMaxVelocity(self.axis)
			self.axis.asynchronousMoveTo(self.originalPosition)

	def rawAsynchronousMoveTo(self, position):
		
		self.files = []
		self.fullFileLocation = ""
		self.detector.setFilename(self.fileName + "_")
		velocity = float(abs(self.step)) / float(self.exposureTime)
		runUp = velocity / 10
		axisRunUpAndDownDelay = 2
		
		for exp in range(self.noOfExpPerPos):
			simpleLog("rawAsynchronousMoveTo %r sync %r runUp %r exp %r" %
					(self.axis, self.sync, runUp, exp))
			
			self.isccd.flush()
			
			if self.sync:
				setMaxVelocity(self.axis)
				deactivatePositionCompare() #Prevent false triggers when debounce on
				moveMotor(self.axis, position - runUp)
				scanGeometry(self.axis, velocity, position, position + self.step)
				sleep(0.2)
				self.isccd.xpsSync("dummy", self.exposureTime + axisRunUpAndDownDelay)
				self.detector.expose(self.exposureTime)
				moveMotor(self.axis, position + self.step + runUp)
				deactivatePositionCompare()
				sleep(7) # Todo Why such a long wait?
				
			else:
				if self.axis:
					simpleLog("(fast shutter not synchronised with motor)")
					setMaxVelocity(self.axis)
					moveMotor(self.axis, position - runUp)
					setVelocity(self.axis, velocity)
				else:
					simpleLog("Pilatus expose for " + str(self.exposureTime) + "s")
		
				self.isccd.openS()
				self.detector.expose(position)
			
				if self.axis:
					moveMotor(self.axis, position + self.step + runUp)
				else:
					sleep(position + 1)
				
				self.isccd.closeS()
			
			self.files.append(self.detector.getFullFilename())

	def rawIsBusy(self):
		return 0;

	def rawGetPosition(self):
		return [self.exposureTime, self.files]

class MarAxisWrapper(DetectorAxisWrapper):
	def __init__(self, detector, isccd, exposureTime=1, axis=None, step=None, sync=False, fileName="mar_scan", noOfExpPerPos=1, rock=False, pause=False):
		DetectorAxisWrapper.__init__(self, pause, -11, exposureTime)
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.isccd = isccd
		self.detector = jythonNameMap.mar
		self.axis = axis
		self.sync = sync
		self.fileName = fileName
		self.file = fileName
		self.fullFileName = ""
		self.exposureNo = 0
		self.noOfExpPerPos = noOfExpPerPos
		self.step = float(step)
		self.files = []
		self.originalPosition = 0
		#self.nextScanNo = getNextMarScanNumber()
		self.inc = 1;
		self.setName("mar wrapper")
		self.rock=rock
		
		self.exposureNo = 1

		if self.sync:
			self.setInputNames(["exposure time"])
			self.setOutputFormat(["%2d", "%2d", "%s"])
			self.setExtraNames(["dkphi","file name"])
		else:
			self.setInputNames(["Exposure Time"])
			self.setOutputFormat(["%6.4f", "%s"])
			self.setExtraNames(["file name"])
			
		self.velocity = float(abs(self.step)) / float(self.exposureTime)

	def atScanStart(self):
		
		incrementMarScanNumber()
		
		userDir = VisitPath.getVisitPath() 
		#if userDir != getDir():
		simpleLog("User  full user dir to " + userDir)
		setFullUserDir(userDir)
			
		self.isccd.flush()
		
		if self.axis:
			self.originalPosition = self.axis()
			
		checkMarIsReady()
		openMarShield()
	
	def atScanEnd(self):
		closeMarShield()
		
		if self.axis:
			setMaxVelocity(self.axis)
			self.axis.asynchronousMoveTo(self.originalPosition)

	def rawAsynchronousMoveTo(self, position):
		self.files = []
		
		self.fileName = self.file + "_%03d" % getNextMarScanNumber()
		
		for exp in range(self.noOfExpPerPos):
			runUp = ((self.velocity*.25)/2) + 0.1 # acceleration time .25 may change. This seems to solve the problem of the fast shutter not staying open.
			
			simpleLog("rawAsynchronousMoveTo %r sync %r runUp %r exp %r" %
					(self.axis, self.sync, runUp, exp))
			
			if self.velocity <= 8.0:
			
				self.isccd.flush()
				
				if self.sync:
				
					setMaxVelocity(self.axis)
					deactivatePositionCompare() #Prevent false triggers when debounce on
					moveMotor(self.axis, position - runUp)
					scanGeometry(self.axis, self.velocity, position , position + self.step)
					sleep(0.2)
					self.isccd.xpsSync("dummy", self.exposureTime + 5)
					
					self.preExposeCheck()
					
					moveMotor(self.axis, position + self.step + runUp)
					
					if self.postExposeCheckFailed():
						
						marErase(1)
						openEHShutter()
						deactivatePositionCompare()
						sleep(10)
						
						self.preExposeCheck()
							
						setMaxVelocity(self.axis)
						deactivatePositionCompare() #Prevent false triggers when debounce on
						moveMotor(self.axis, position - runUp)
						scanGeometry(self.axis, self.velocity, position , position + self.step)
						sleep(0.2)
						self.isccd.xpsSync("dummy", self.exposureTime + 5)
						moveMotor(self.axis, position + self.step + runUp)
					
					deactivatePositionCompare()
					sleep(10)
				
				else:
					if self.axis:
						simpleLog("(fast shutter not synchronised with motor)")
						setMaxVelocity(self.axis)
						moveMotor(self.axis, position - runUp)
						setVelocity(self.axis, self.velocity)
				
					self.isccd.openS()
				
					if self.axis:
						moveMotor(self.axis, position + self.step + runUp)
					else:
						sleep(self.exposureTime)
					self.isccd.closeS()
				
				if self.noOfExpPerPos > 1:
					self.fullFileName = self.fileName + "_%03d" % self.exposureNo
				elif self.rock:
					self.fullFileName = self.fileName
				else:
					self.fullFileName = self.fileName + "_%03d" % self.inc
				
				# Make sure that any output files do not exist before we start:
				expectedFile = VisitPath.getVisitPath() + "/" + self.fullFileName
				expectedGlob =expectedFile + "_001.*"
				filesAtLocation = glob(expectedGlob)
				
				if len(filesAtLocation) > 0:
					simpleLog("Warning, files found matching %s: \n%s\nRenaming..." %
							  (expectedGlob, "\n".join(filesAtLocation)))
					for file in filesAtLocation:
						newFile = file.replace("_001.","_bak.")
						try:
							os.rename(file, newFile)
						except OSError:
							simpleLog("Error renaming file %s to %s" %
									  (file, newFile))
				
				self.scanTheMarWithChecks(300)
				
				# There should now be only one file which starts with fullFileName
				filesAtLocation = glob(expectedGlob)
				
				if len(filesAtLocation) == 1:
					# Rename it to strip out the 
					self.fullFileLocation = filesAtLocation[0].replace("_001.",".")
					try:
						#simpleLog("Renaming file %s to %s" %
						#		  (filesAtLocation[0], self.fullFileLocation))
						os.rename(filesAtLocation[0], self.fullFileLocation)
						self.files.append(self.fullFileLocation)
						FileRegistrarHelper.registerFile(self.fullFileLocation)	
					except OSError:
						simpleLog("Error renaming file %s to %s" %
										  (filesAtLocation[0], self.fullFileLocation))
						# Since  we can't rename it, register the unrenamed file. 
						self.files.append(filesAtLocation[0])
						FileRegistrarHelper.registerFile(filesAtLocation[0])	
						
				# If there are no or 2+ matching files, try to fail gracefully.
				elif len(filesAtLocation) == 0:
					simpleLog("Error, no file(s) found matching %s" % expectedGlob)
					
				else:
					simpleLog("Error, multiple files found matching %s: \n%s" %
							  (expectedGlob, "\n".join(filesAtLocation)))
				
				#modMar = modMarName(self.fullFileLocation)
				#modMar.start()
			else:
				simpleLog("velocity too high, please specify a longer exposure time (max velocity of kphi=8.0 deg/sec)")
		
			self.exposureNo += 1
		self.inc +=1
				
	def rawIsBusy(self):
		return 0;

	def rawGetPosition(self):
		if self.sync:
			return [self.exposureTime, self.axis(), self.files]
		else:
			return [self.exposureTime, self.files]

	def scanTheMarWithChecks(self, timeout):
		"""
		Scan the mar, checking for correct status 
		"""
		self.detector.setRootName(self.fullFileName)
		
		mar_mode = self.detector.getMode()
		if (mar_mode != 4):
			simpleLog( "Mar mode is %d not the default 4, use 'mar.setMode(X)' to change mode to X or mar.setMode(-1) to list modes." % mar_mode)
		
		# Wait for mar to be ready before starting scan
		timeTaken = self.waitForStatus(timeout, 0)
		if (timeTaken == -1):
			raise "Timed out waiting for mar to be ready, so scan not performed"
		
		simpleLog("mar ready in time %.2f" % timeTaken + "s")
		# Wait for mar to start scanning
		simpleLog("Scan command sent to mar... (timeout = " + str(timeout) + ")") 
		self.detector.scan()
		timeTaken = self.waitForStatus(timeout, 1)
		if (timeTaken == -1):
			raise "Timed out waiting for mar to start, so scan not performed"
		
		simpleLog("mar busy in time %.2f" % timeTaken + "s")
		# Scan scanning and wait for mar to be ready
		timeTaken = self.waitForStatus(timeout, 0)
		if (timeTaken == -1):
			raise "Timed out waiting for mar to stop scanning"
		
		simpleLog("Scanned in time %.2f" % timeTaken + "s")

	def waitForStatus(self, timeout, status):
		
		t0 = clock()
		t1 = t0
		while ((t1 - t0) < timeout): 
			if (self.detector.getStatus() == status):
				simpleLog("Mar status of " + str(status) + " reached in time %.2f" % (t1 - t0) + "s")
				return (t1 - t0)
			t1 = clock()
			pause()					 # ensures script can be stopped promptly
	
		simpleLog("Timed out waiting for mar status of " + str(status) + " (waited " + str(timeout) + "s)")
		return - 1

	def remove_001Suffix(self):
		"""
		Remove '_001' suffix from file paths (added by mar software)
		"""
		simpleLog("removing '_001' suffix from all files created...")
		for filePath in self.filePaths:
			print filePath
			fileWithSuffix_001 = filePath.replace(".mar3450", "_001.mar3450")
			if (doesFileExist(fileWithSuffix_001)):
				os.rename(fileWithSuffix_001, filePath)
			else:
				simpleLog("Could not find file " + fileWithSuffix_001 + " to rename")

def _getWrappedDetector(axis, start, stop, step, detector, exposureTime,
		noOfExpPerPos, fileName, sync, diff=0., pause=False, rock=False,
		overflow=False, multiFactor=1, exposeDark=False):
	
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	#isccd = jythonNameMap.ruby
	isccd = jythonNameMap.atlas
	
	wrappedDetector = None
	
	if isinstance(detector, ruby_scripts.Atlas):
		# Not used: start, stop, rock=False
		wrappedDetector = AtlasAxisWrapper(detector, exposureTime, axis, step, sync=sync,
								fileName=fileName, noOfExpPerPos=noOfExpPerPos, diff=diff, pause=pause, overflow=overflow, multiFactor=multiFactor)
	
	elif isinstance(detector, ruby_scripts.Ruby):
		# Not used: start, stop, rock=False
		wrappedDetector = RubyAxisWrapper(detector, exposureTime, axis, step, sync=sync,
								fileName=fileName, noOfExpPerPos=noOfExpPerPos, diff=diff, pause=pause, overflow=overflow, multiFactor=multiFactor)
	
	elif isinstance(detector, pd_pilatus.Pilatus) or isinstance(detector, pd_pilatus.DummyPilatus):
		# Not used: start, stop, diff=0., pause=False, rock=False, overflow=False, multiFactor=1
		wrappedDetector = PilatusAxisWrapper(detector, isccd, exposureTime, axis, step, sync=sync,
							   fileName=fileName, noOfExpPerPos=noOfExpPerPos)
	
	elif isinstance(detector, Mar345Detector):
		# Not used: start, stop, diff=0., overflow=False, multiFactor=1
		wrappedDetector = MarAxisWrapper(detector, isccd, exposureTime, axis, step, sync=sync,
							   fileName=fileName, noOfExpPerPos=noOfExpPerPos, rock=rock, pause=pause)
	
	elif isinstance(detector, PerkinElmer):
		from scannables.detectors.perkinElmerAxisWrapper import PerkinElmerAxisWrapper
		# Not used: start, stop, diff=0., overflow=False, multiFactor=1
		wrappedDetector = PerkinElmerAxisWrapper(detector, isccd,
			jythonNameMap.prop, jythonNameMap.feabsb, jythonNameMap.fmfabsb,
			exposureTime, axis, step, sync=sync, fileName=fileName,
			noOfExpPerPos=noOfExpPerPos, rock=rock, pause=pause,
			exposeDark=exposeDark)
	else:
		raise "Unknown detector passed into scan" + str(type(detector))
	return wrappedDetector

class modHeader(Thread):
	def __init__(self, file, names, values):
		Thread.__init__(self)
		self.names = names
		self.values = values
		self.file = file

	def run(self):
		for (names,values) in zip(self.names, self.values):
			self.file.editDoubleHeader(names, values)
		self.file.close()

class modMarName(Thread):
	def __init__(self, file):
		Thread.__init__(self)
		self.file = file
		self.fileToChange = self.file.replace(".mar3450", "_001.mar3450")
		self.timeout=50
		self.time_gone=0
		
	def run(self):
		
		while not os.path.isfile(self.fileToChange):
			sleep(2)
			self.time_gone+=2
			if self.time_gone>=self.timeout:
				return
		
		os.rename(self.fileToChange, self.file)	
		FileRegistrarHelper.registerFile(self.file)	