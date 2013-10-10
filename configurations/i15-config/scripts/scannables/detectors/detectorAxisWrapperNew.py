from time import sleep
from gdascripts.messages.handle_messages import simpleLog
from ccdScanMechanics import setMaxVelocity, scanGeometryCheck
from gda.device.scannable import PseudoDevice
from gda.util import VisitPath
from gda.epics import CAClient

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
				 pause, prop_threshold, exposureTime, step, axis, sync,
				 exposeDark=False):
		self.detector = detector
		self.isccd = isccd
		self.prop = prop # jythonNameMap.qbpm1total
		self.feabsb = feabsb # jythonNameMap.feabsb
		self.fmfabsb = fmfabsb # jythonNameMap.fmfabsb
		self.pause = pause
		self.prop_threshold =prop_threshold
		self.exposureTime = float(exposureTime)
		self.step = float(step)
		self.velocity = float(abs(self.step)) / float(self.exposureTime)
		self.axis = axis
		self.sync = sync
		self.exposeDark = exposeDark
		
		self.feabsb_pos = self.feabsb.getPosition()
		self.fmfabsb_pos=self.fmfabsb.getPosition()
		
		self.caclient = CAClient()
		self.max_time_to_injection = exposureTime + 1.
		self.wait_after_injection = exposureTime + 4.
		
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
		scanGeometryCheck(self.axis, self.velocity, 0, self.step)
		
		if self.pause:
			simpleLog("Scan will pause if proportional counter %f is below " +
				"threshold value %f" % (self.prop(), self.prop_threshold))
		
		self.visitPath = VisitPath.getVisitPath()
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
