from time import sleep
from gdascripts.messages.handle_messages import simpleLog
from ccdScanMechanics import setMaxVelocity
from gda.device.scannable import PseudoDevice
from dataDir import getDir, setDir, setFullUserDir 
from gda.util import VisitPath

axisWrapperBehaviour="""
Detector:	mar							pilatus						ruby/atlas

Mode:	
	sync (requires axis)
			max velocity				max velocity				max velocity
			move pos-runUp				move pos-runUp				move pos-runUp-diff
																	set velocity
			scanGeometry				scanGeometry				scanGeometry
			sleep(0.2)					sleep(0.2)					
			xpsSync						xpsSync						detector.expsSaveIntensityA()
			move pos+step+runUp			move pos+step+runUp			move pos+step+runUp
																	detector.expsSaveIntensityB()
			deactivatePositionCompare	deactivatePositionCompare	deactivatePositionCompare
			sleep(10)					sleep(7)					

	axis (no sync)
			max velocity				max velocity				n/a
			move pos-runUp				move pos-runUp				
			set velocity				set velocity				
			ruby.openS					ruby.openS					
										detector.expose(position)	
			move pos+step+runUp			move pos+step+runUp			
			ruby.closeS					ruby.closeS					

	no sync or axis
			ruby.openS					ruby.openS					n/a
										detector.expose(position)	
			sleep(exposureTime)			sleep(position+1)			
			ruby.closeS					ruby.closeS					

detector_scan_commands:
	simpleScan() 		 sync=True							=> sync
	simpleScanOverflow() sync=True	overflow=True			=> sync
	simpleScanDel()		 sync=True	diff=diff				=> sync
	simpleScanUnsync()	 sync=False							=> axis (no sync)
	rockScan()			 sync=True	rock=True				=> sync
	rockScanUnsync()	 sync=False	rock=False !			=> axis (no sync)
	doubleScan()		 sync=True	scanDoubleFlag=True		=> sync
	expose()			 sync=False	rock=True	axis=None	=> no sync or axis
	darkExpose()		 sync=False				axis=None	=> no sync or axis

"""

class DetectorAxisWrapperNew(PseudoDevice):
	def __init__(self, detector, isccd, prop, feabsb, fmfabsb,
				 pause, prop_threshold, exposureTime, axis, sync,
				 exposeDark=False):
		self.detector = detector
		self.isccd = isccd
		self.prop = prop # jythonNameMap.qbpm1total
		self.feabsb = feabsb # jythonNameMap.feabsb
		self.fmfabsb = fmfabsb # jythonNameMap.fmfabsb
		self.pause = pause
		self.prop_threshold =prop_threshold
		self.exposureTime = float(exposureTime)
		self.axis = axis
		self.sync = sync
		self.exposeDark = exposeDark
		
		self.feabsb_pos = self.feabsb.getPosition()
		self.fmfabsb_pos=self.fmfabsb.getPosition()
		
		self.originalPosition = 0
		self.files = []
		self.visitPath = ""
		
		self.setInputNames(["Exposure Time"])
		if self.sync:
			self.setOutputFormat(["%2d", "%2d", "%s"])
			self.setExtraNames(["dkphi","file name"])
		else:
			self.setOutputFormat(["%6.4f", "%s"])
			self.setExtraNames(["file name"])

	def atScanStart(self):
		if self.pause:
			simpleLog("Scan will pause if proportional counter %f is below " +
				"threshold value %f" % (self.prop(), self.prop_threshold))
		
		self.visitPath = VisitPath.getVisitPath()
		if self.visitPath != getDir():
			simpleLog("Visit path is now: " + self.visitPath)
			setFullUserDir(self.visitPath)
		
		self.isccd.flush()
		
		if self.axis:
			self.originalPosition = self.axis()

	def atScanEnd(self):
		if self.axis:
			setMaxVelocity(self.axis)
			self.axis.asynchronousMoveTo(self.originalPosition)

	def rawGetPosition(self):
		if self.sync:
			return [self.exposureTime, self.axis(), self.files]
		else:
			return [self.exposureTime, self.files]

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
			reasons.add("absorber is " + self.feabsb_pos)
		if not fastMaskOpen:
			reasons.add("fast mask is " + self.fmfabsb_pos)
		simpleLog("paused because " + " and ".join(reasons))
		
		minutesRemain = delayMinutes
		secondsRemain = 60
		
		while(not (absorberOpen and fastMaskOpen) and minutesRemain > 0):
			sleep(1)
			absorberOpen_new = self.absorberOpen()
			fastMaskOpen_new = self.fastMaskOpen()
			# If nothing changed, keep counting down/showing updates.
			if absorberOpen == absorberOpen_new and fastMaskOpen == fastMaskOpen_new:
				if absorberOpen and fastMaskOpen:
					if secondsRemain == 0:
						secondsRemain = 60 
						minutesRemain -= 1
						simpleLog("%d minute remain..." % minutesRemain)
					else:
						secondsRemain -= 1
						print "."
				else:
					print "."
			else: # Something changed
				if absorberOpen and fastMaskOpen:
					minutesRemain = delayMinutes
					secondsRemain = 60
					simpleLog("both absorber and fast mask now open, " +
						"starting %d minute timer..." % minutesRemain)
					
				reasons = []
				if not absorberOpen == absorberOpen_new:
					reasons.add("absorber is now " + self.feabsb_pos)
				if not fastMaskOpen == fastMaskOpen_new:
					reasons.add("fast mask is now " + self.fmfabsb_pos)
				simpleLog(" and ".join(reasons))

				absorberOpen = absorberOpen_new
				fastMaskOpen = fastMaskOpen_new

	def preExposeCheck(self):
		if not self.pause:
			return
		
		self.waitForAbsorberAndMaskOpen()
		
		pause_prompt = False	
		while (self.prop() < self.prop_threshold):
			if not pause_prompt:
				simpleLog("paused because beam is below proportional counter threshold level")
				pause_prompt = True
			sleep(1)

	def postExposeCheck(self):
		return (self.pause and (self.prop() < self.prop_threshold) and 
				self.absorberOpen() and self.fastMaskOpen() )