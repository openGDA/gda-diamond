import os
import sys
from time import sleep
from time import time
from threading import Thread
from gdascripts.messages.handle_messages import simpleLog
from operationalControl import moveMotor
from ccdScanMechanics import setMaxVelocity
from ccdScanMechanics import deactivatePositionCompare
from ccdScanMechanics import scanGeometry
from ccdScanMechanics import setVelocity
from ccdAuxiliary import incrementCCDScanNumber
from ccdAuxiliary import openCCDShield, closeCCDShield
from gdascripts.parameters import beamline_parameters
from gda.device.detector.odccd import ModifyCrysalisHeader
from gda.data.fileregistrar import FileRegistrarHelper
from gda.epics import CAClient
from java.io import File

from detectorAxisWrapper import DetectorAxisWrapper

class ISCCDAxisWrapper(DetectorAxisWrapper):
	def __init__(self, detector, isccd, exposureTime=0, axis=None, start=None,
			stop=None, step=None, sync=False, scanDoubleFlag=False,
			fileName="isccd_scan", noOfExpPerPos=1, diff=0., pause=False,
			overflow=False, multiFactor=1):
		DetectorAxisWrapper.__init__(self, pause, -11, exposureTime, step)
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.isccd = isccd
		self.prop = jythonNameMap.prop
		#self.prop = jythonNameMap.dummy1
		self.detector = detector
		self.sync = sync
		self.fileName = fileName
		self.scan_start = float(start)
		self.scan_stop = float(stop)
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
		
		self.caclient = CAClient()
		self.diodeSum = "BL15I-DI-PHDGN-02:DIODESUM"
		# Note, this PV currently reads the BL15I-DI-PHDGN-02:I PV. If you want
		# to sum another PV, use BL15I-DI-PHDGN-02:DIODECALC.INPB to set the PV
		# you want to sum atScanStart.

	def atScanStart(self):
		
		DetectorAxisWrapper.atScanStart(self)
		
		self.detector.setDir(self.visitPath)
		
		if self.overflow and self.sync:
			experiment_name = self.fileName
			
			maxVelocity = 8. # TODO: Should be based on the self.axis.?()
			if self.multiFactor > 1 and maxVelocity < self.velocityFast():
				err = "Error checking fast move: max velocity %r" % maxVelocity \
					+ "is less than %r" % self.velocityFast() + " (velocity %r" \
					% self.velocity + " * multiFactor %r" % self.multiFactor \
					+ ") \nTry increasing exposure time or decreasing multiFactor."
				raise Exception, err
			
			if '/' in experiment_name:
				raise Exception ,"simplaScanOverflow does not support / in " + \
					"names: " + experiment_name
			
			# First make sue that the experiment directory exists
			run_path = "/spool/" + experiment_name
			frames_path = run_path + "/frames"
			self.run_file = "%s%s/%s.run" % (self.detector.path, run_path, experiment_name)
			self.frames_path = self.detector.path + frames_path
			
			targetDir = File(self.visitPath + frames_path)
			try:
				if not targetDir.exists():
					targetDir.mkdirs()
				if not targetDir.exists():
					raise Exception ,"Unable to create data directory " + \
						`targetDir` + " check permissions"
			except:
				typ, exception,  = sys.exc_info()
				raise Exception, "Error while trying to create data directory:" \
					+ `targetDir` + " " + `typ` + ":" + `exception`
			
			# Then copy over all of the template files
			template_path = self.visitPath + "/xml/atlas"
			if os.path.exists(template_path):
				target_path = self.visitPath + run_path
				par_present = False
				
				for fil in os.listdir(template_path):
					if fil == "atlas.par":
						dest = "%s/%s.par" % (target_path, experiment_name)
						par_present = True
					else:
						dest = "%s/%s" % (target_path, fil)
					
					if not os.path.exists(dest):
						command = "cp %s/%s %s" % (template_path, fil, dest)
						if os.system(command) <> 0:
							raise Exception, "Error, running command %s" % command
				
				if not par_present:
					raise Exception, "Error, missing %s/atlas.par" % template_path
			else:
				raise Exception, "Error, no template data in %s" % template_path
			
			jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
			# Add this scan to the runlist
			if self.axis.name == "dkphi":
				scantype = 4
				domegaindeg = 90. + jythonNameMap.dktheta() # Flat@dktheta=-34
				dphiindeg = 0
				dscanstartindeg = self.scan_start
				dscanendindeg = self.scan_stop
			elif self.axis.name == "dktheta":	# omega in diff terms
				scantype = 0
				domegaindeg = 0
				dphiindeg = jythonNameMap.dkphi()
				dscanstartindeg = 90. + self.scan_start	# omega = 90+dktheta
				dscanendindeg = 90. + self.scan_stop	# omega = 90+dktheta
			else:
				raise Exception, "Error, only dkphi and dktheta supported!"
			
			ddetectorindeg = jythonNameMap.ddelta()
			dkappaindeg = jythonNameMap.dkappa()			# Flat @ -134.75
			dscanwidthindeg = self.step
			dscanspeedratio = self.multiFactor
			dwnumofframes = int(abs(self.scan_stop-self.scan_start)/self.step)
			dwnumofframesdone = 0
			
			self.detector.runlistAdd(scantype, domegaindeg, ddetectorindeg,
				dkappaindeg, dphiindeg, dscanstartindeg, dscanendindeg,
				dscanwidthindeg, dscanspeedratio, dwnumofframes,
				dwnumofframesdone, self.exposureTime, experiment_name,
				self.run_file)
		
		self.detector.flush()
		openCCDShield()

	def atScanEnd(self):
		DetectorAxisWrapper.atScanEnd(self)
		closeCCDShield()

	def syncExpose(self, position, runUp, filename, log_message, fast, velocity):
		samples = []
		# Zero the diode sum we can tell if it was triggered
		self.caclient.caput(self.diodeSum, 0) 
		
		if self.sync:
			setMaxVelocity(self.axis)
			deactivatePositionCompare() #Prevent false triggers when debounce on
			moveMotor(self.axis, position - runUp - self.diff)
			
			if self.step>0:
				geometry = scanGeometry(self.axis, velocity, position, position + self.step)
			else:
				geometry = scanGeometry(self.axis, velocity, position + self.step, position)
			
			self.preExposeCheck()
			
			simpleLog(log_message % self.detectorName)
			self.detector.expsSaveIntensityA(self.exposureTime)
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
			if self.overflow:
				experiment_name = self.fileName
				if fast:
					multiFactor = self.multiFactor
					final_filename = run_filename = ""
				else:
					multiFactor = 1
					run_filename = self.run_file
					final_filename = "%s/%s_%01d_%01d.img" % (self.frames_path,
						experiment_name, self.nextScanNo, self.exposureNo)
				
				self.detector.expsSaveIntensityB2(
					filename, self.exposureTime, geometry, 0,
					multiFactor, final_filename, run_filename,
					experiment_name)
			else:
				self.detector.expsSaveIntensityB(
					filename, self.exposureTime, geometry, 0)
		
		diodeSum = float(self.caclient.caget(self.diodeSum))
		simpleLog("diodeSum="+str(diodeSum) + ", imonAverage="+str(imonAverage) + " " + repr(samples))
		
		return imonAverage, diodeSum

	def velocityFast(self):
		return self.velocity * float(self.multiFactor)

	def performMove(self, position, fast=False):
		velocity = self.velocityFast() if fast else self.velocity

		#runUp = velocity / 10 # Only pilatus uses this formula now,
		# Mar and PE now use the one below, which should work better for
		# low velocity moves:
		runUp = ((velocity*.25)/2) + 0.1 # acceleration time .25 may
		#change. This seems to solve the problem of the fast shutter not
		#staying open.
		
		if self.step < 0:
			runUp = runUp * -1
		
		if self.axis and self.axis.getName() == "dktheta":
			runUp = runUp * 2
		
		for exp in range(self.noOfExpPerPos):
			simpleLog("performMove %r sync %r runUp %r exp %r velo %r" %
					(self.axis, self.sync, runUp, exp, velocity))
			
			self.isccd.flush()
			filename = self.fileName
			
			if self.overflow and fast:
				filename += "_fast"
			elif self.overflow:
				filename += "_slow"
			
			filename += "_%01d" % self.nextScanNo + "_%01d" % self.exposureNo
			
			self.fullFileName = self.detector.path + "/" + filename + ".img"
			
			imonAverage, diodeSum = self.syncExpose(position, runUp, filename,
					"Exposing %s", fast, velocity)
			
			if self.postExposeCheckFailed():
				imonAverage, diodeSum = self.syncExpose(position, runUp, filename,
					"Re-exposing %s because of beam loss during expose", fast, velocity)
			
			self.files.append(filename)
			linuxFilename = self.visitPath + "/" + filename + ".img"
			diodeSumScaled = diodeSum * 1000
			imonScaledAvg = imonAverage * 100000
			crysalisFile = ModifyCrysalisHeader(linuxFilename)
			names = ["imon1", "imon2", "dexposuretimeinsec"]
			values = [diodeSumScaled, imonScaledAvg, self.exposureTime]
			mod1 = modHeader(crysalisFile, names, values)
			mod1.start()
			deactivatePositionCompare()
			FileRegistrarHelper.registerFile(linuxFilename)
			
			if fast==False:
				self.exposureNo += 1

	def rawAsynchronousMoveTo(self, position):
		if type(position) == list:
			if self.axis:
				simpleLog("rawAsynchronousMoveTo(%r) returning..." % position)
				setMaxVelocity(self.axis)
				moveMotor(self.axis, position[1])
			else:
				simpleLog("rawAsynchronousMoveTo(%r) returning early." % position)
			return
		
		self.files = []
		if self.overflow and self.multiFactor > 1:
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
	def __init__(self, detector, exposureTime=0, axis=None, start=None,
			stop=None, step=None, sync=False, scanDoubleFlag=False,
			fileName="ruby_scan", noOfExpPerPos=1, diff=0., pause=False,
			overflow=False, multiFactor=1):
		ISCCDAxisWrapper.__init__(self, detector, detector, exposureTime, axis,
			start, stop, step, sync, scanDoubleFlag, fileName, noOfExpPerPos,
			diff, pause, overflow, multiFactor)
		self.setName("ruby wrapper")
		self.detectorName = "Ruby"


class AtlasAxisWrapper(ISCCDAxisWrapper):
	def __init__(self, detector, exposureTime=0, axis=None, start=None,
			stop=None, step=None, sync=False, scanDoubleFlag=False,
			fileName="atlas_scan", noOfExpPerPos=1, diff=0., pause=False,
			overflow=False, multiFactor=1):
		ISCCDAxisWrapper.__init__(self, detector, detector, exposureTime, axis,
			start, stop, step, sync, scanDoubleFlag, fileName, noOfExpPerPos,
			diff, pause, overflow, multiFactor)
		self.setName("atlas wrapper")
		self.detectorName = "Atlas"

class modHeader(Thread):
	def __init__(self, filename, names, values):
		Thread.__init__(self)
		self.names = names
		self.values = values
		self.file = filename

	def run(self):
		for (names,values) in zip(self.names, self.values):
			self.file.editDoubleHeader(names, values)
		self.file.close()
