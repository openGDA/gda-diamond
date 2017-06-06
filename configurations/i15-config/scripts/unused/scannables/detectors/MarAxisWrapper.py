import os
from time import sleep
from time import time
from threading import Thread, Timer
from gdascripts.messages.handle_messages import simpleLog
from gda.jython.commands.GeneralCommands import pause
from operationalControl import moveMotor
from ccdScanMechanics import setMaxVelocity
from ccdScanMechanics import deactivatePositionCompare
from ccdScanMechanics import scanGeometry
from ccdScanMechanics import setVelocity
from marAuxiliary import checkMarIsReady
from marAuxiliary import openMarShield, closeMarShield
from marAuxiliary import incrementMarScanNumber
from marAuxiliary import getNextMarScanNumber
from marAuxiliary import marErase
from shutterCommands import openEHShutter#, closeEHShutter, getShutterStatus, sh
from gdascripts.parameters import beamline_parameters
from util_scripts import doesFileExist
from gda.util import VisitPath
from gda.data.fileregistrar import FileRegistrarHelper
from glob import glob

from detectorAxisWrapper import DetectorAxisWrapper

class MarAxisWrapper(DetectorAxisWrapper):
	def __init__(self, detector, isccd, exposureTime=1, axis=None, step=None, sync=False, fileName="mar_scan", noOfExpPerPos=1, rock=False, pause=False, fixedVelocity=False):
		DetectorAxisWrapper.__init__(self, pause, -11, exposureTime, step)
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
		self.files = []
		self.originalPosition = 0
		#self.nextScanNo = getNextMarScanNumber()
		self.inc = 1;
		self.setName("mar wrapper")
		self.rock=rock
		self.fixedVelocity = fixedVelocity
		
		self.exposureNo = 1

		if self.sync:
			self.setInputNames(["exposure time"])
			self.setOutputFormat(["%2d", "%2d", "%s"])
			self.setExtraNames(["dkphi","file name"])
		else:
			self.setInputNames(["Exposure Time"])
			self.setOutputFormat(["%6.4f", "%s"])
			self.setExtraNames(["file name"])

	def atScanStart(self):
		DetectorAxisWrapper.atScanStart(self)
		
		incrementMarScanNumber()
		
		simpleLog("MAR: Force setting of full user dir to " + self.visitPath)
		self.detector.setDirectory(self.visitPath)
			
		self.isccd.flush()
		
		checkMarIsReady()
		openMarShield()
	
	def atScanEnd(self):
		closeMarShield()
		
		DetectorAxisWrapper.atScanEnd(self)

	def _closeS_and_Log_timer_factory(self):
		return Timer(self.exposureTime, self._closeS_and_Log)

	def _closeS_and_Log(self):
		self.isccd.closeS()
		simpleLog("Shutter closed")

	def rawAsynchronousMoveTo(self, position):
		if type(position) == list:
			if self.sync:
				simpleLog("rawAsynchronousMoveTo(%r) returning..." % position)
				setMaxVelocity(self.axis)
				moveMotor(self.axis, position[1])
			else:
				simpleLog("rawAsynchronousMoveTo(%r) returning early." % position)
			return
		
		self.files = []
		
		self.fileName = self.file + "_%03d" % getNextMarScanNumber()
		
		for exp in range(self.noOfExpPerPos):
			runUp = ((self.velocity*.25)/2) + 0.1 # acceleration time .25 may change. This seems to solve the problem of the fast shutter not staying open.
			
			simpleLog("rawAsynchronousMoveTo(%r) %r sync %r runUp %r exp %r" %
					(position, self.axis, self.sync, runUp, exp))
			
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
				
				elif self.fixedVelocity:
					simpleLog("(fast shutter not synchronised with fixed velocity motor)")
					setMaxVelocity(self.axis)
					moveMotor(self.axis, position)
					
					close_timer = self._closeS_and_Log_timer_factory()
					
					self.isccd.openS()
					close_timer.start()
					
					moveMotor(self.axis, position + self.step)
					if not close_timer.isAlive():
						simpleLog("Warning: Shutter closed before the end of the first rock!")
					
					while close_timer.isAlive():
						simpleLog("Completed one fast rock, starting another...")
						moveMotor(self.axis, position)
						moveMotor(self.axis, position + self.step)
					
					simpleLog("Completed last fixed velocity rock.")
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
					for fil in filesAtLocation:
						newFile = fil.replace("_001.","_bak.")
						try:
							os.rename(fil, newFile)
						except OSError:
							simpleLog("Error renaming file %s to %s" %
									  (fil, newFile))
				
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
		
		t0 = time()
		t1 = t0
		while ((t1 - t0) < timeout): 
			if (self.detector.getStatus() == status):
				simpleLog("Mar status of " + str(status) + " reached in time %.2f" % (t1 - t0) + "s")
				return (t1 - t0)
			t1 = time()
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

class modMarName(Thread):
	def __init__(self, filename):
		Thread.__init__(self)
		self.file = filename
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
