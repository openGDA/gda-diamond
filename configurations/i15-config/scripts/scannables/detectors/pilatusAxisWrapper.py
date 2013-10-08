from time import sleep
from gdascripts.messages.handle_messages import simpleLog
from operationalControl import moveMotor
from ccdScanMechanics import setMaxVelocity
from ccdScanMechanics import deactivatePositionCompare
from ccdScanMechanics import scanGeometry
from ccdScanMechanics import setVelocity

from detectorAxisWrapper import DetectorAxisWrapper

class PilatusAxisWrapper(DetectorAxisWrapper):
	def __init__(self, detector, isccd, exposureTime=0, axis=None, step=1, sync=False, fileName="P100K_scan", noOfExpPerPos=1):
		DetectorAxisWrapper.__init__(self, False, -11, exposureTime, step)
		self.isccd = isccd
		self.detector = detector
		self.sync = sync
		self.fileName = fileName
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
		DetectorAxisWrapper.atScanStart(self)
		
		self.detector.setFilePath(self.visitPath)
		self.isccd.flush()
		
		if self.detector.getFilePath()[-1:] != "/":
			self.detector.setFilePath(self.detector.getFilePath() + "/")
	
	def atScanEnd(self):
		DetectorAxisWrapper.atScanEnd(self)

	def rawAsynchronousMoveTo(self, position):
		if type(position) == list:
			# Pilatus rawGetPosition never records self.axis position.
			simpleLog("rawAsynchronousMoveTo(%r) returning early." % position)
			return
		
		self.files = []
		self.fullFileLocation = ""
		self.detector.setFilename(self.fileName + "_")
		runUp = self.velocity / 10
		axisRunUpAndDownDelay = 2
		
		for exp in range(self.noOfExpPerPos):
			simpleLog("rawAsynchronousMoveTo(%r) %r sync %r runUp %r exp %r" %
					(position, self.axis, self.sync, runUp, exp))
			
			self.isccd.flush()
			
			if self.sync:
				setMaxVelocity(self.axis)
				deactivatePositionCompare() #Prevent false triggers when debounce on
				moveMotor(self.axis, position - runUp)
				scanGeometry(self.axis, self.velocity, position, position + self.step)
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
					setVelocity(self.axis, self.velocity)
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
