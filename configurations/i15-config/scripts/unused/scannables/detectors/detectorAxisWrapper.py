import ruby_scripts
import pd_pilatus
from time import sleep
from gdascripts.messages.handle_messages import simpleLog
from ccdScanMechanics import setMaxVelocity
from ccdScanMechanics import scanGeometryCheck
from gda.device.scannable import PseudoDevice
from gdascripts.parameters import beamline_parameters
from gda.util import VisitPath
from gda.device.detector.mar345 import Mar345Detector
from scannables.detectors.perkinElmer import PerkinElmer
from gda.epics import CAClient

class DetectorAxisWrapper(PseudoDevice):
	def __init__(self, pause, prop_threshold, exposureTime, step):
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.pause = pause
		self.prop_threshold =prop_threshold
		self.exposureTime = float(exposureTime)
		self.step = float(step)
		self.velocity = float(abs(self.step)) / self.exposureTime
		
		self.prop = jythonNameMap.qbpm1total
		self.feabsb = jythonNameMap.feabsb
		self.feabsb_pos = self.feabsb.getPosition()
		self.fmfabsb = jythonNameMap.fmfabsb
		self.fmfabsb_pos=self.fmfabsb.getPosition()
		
		self.caclient = CAClient()
		self.max_time_to_injection = exposureTime + 1.
		self.wait_after_injection = exposureTime + 4.

	def atScanStart(self):
		scanGeometryCheck(self.axis, self.velocity, 0, self.step)
		#if self.pause:
		#	simpleLog("Scan will pause if proportional counter %f is below " +
		#		"threshold value %f" % (self.prop(), self.prop_threshold))
		self.visitPath = VisitPath.getVisitPath()
		if self.axis:
			self.originalPosition = self.axis()

	def atScanEnd(self):
		if self.axis:
			setMaxVelocity(self.axis)
			self.axis.asynchronousMoveTo(self.originalPosition)

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

from ISCCDAxisWrapper import RubyAxisWrapper, AtlasAxisWrapper
from pilatusAxisWrapper import PilatusAxisWrapper
from MarAxisWrapper import MarAxisWrapper

def _getWrappedDetector(axis, start, stop, step, detector, exposureTime,
		noOfExpPerPos, fileName, sync, diff=0., pause=False, rock=False,
		overflow=False, multiFactor=1, exposeDark=False, fixedVelocity=False):
	
	from gdascripts.scannable.detector.ProcessingDetectorWrapper import \
									   ProcessingDetectorWrapper
	from scannables.detectors.perkinElmerAxisWrapper import \
						      PerkinElmerAxisWrapper
	from scannables.detectors.areaDetectorAxisWrapper import \
						      AreaDetectorAxisWrapper
	from gdascripts.scannable.detector.ProcessingDetectorWrapper import \
		  SwitchableHardwareTriggerableProcessingDetectorWrapper
	from gda.device.detector import NXDetector
	
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	#isccd = jythonNameMap.ruby
	isccd = jythonNameMap.atlas
	
	wrappedDetector = None
	
	if isinstance(detector, ruby_scripts.Atlas):
		# Not used: start, stop, rock=False
		wrappedDetector = AtlasAxisWrapper(detector, exposureTime,
			axis, start, stop, step, sync=sync, fileName=fileName,
			noOfExpPerPos=noOfExpPerPos, diff=diff, pause=pause,
			overflow=overflow, multiFactor=multiFactor)
	
	elif isinstance(detector, ruby_scripts.Ruby):
		# Not used: start, stop, rock=False
		wrappedDetector = RubyAxisWrapper(detector, exposureTime,
			axis, step, sync=sync, fileName=fileName,
			noOfExpPerPos=noOfExpPerPos, diff=diff, pause=pause,
			overflow=overflow, multiFactor=multiFactor)
	
	elif isinstance(detector, pd_pilatus.Pilatus) or \
		 isinstance(detector, pd_pilatus.DummyPilatus):
		# Not used: start, stop, diff=0., pause=False, rock=False, overflow=False, multiFactor=1
		wrappedDetector = PilatusAxisWrapper(detector, isccd, exposureTime,
			axis, step, sync=sync, fileName=fileName,
			noOfExpPerPos=noOfExpPerPos)
	
	elif isinstance(detector, ProcessingDetectorWrapper) and \
		 isinstance(detector.det, pd_pilatus.EpicsPilatus):
		# Not used: start, stop, diff=0., pause=False, rock=False, overflow=False, multiFactor=1
		wrappedDetector = PilatusAxisWrapper(detector.det, isccd, exposureTime,
			axis, step, sync=sync, fileName=fileName, noOfExpPerPos=noOfExpPerPos)
	
	elif isinstance(detector, Mar345Detector):
		# Not used: start, stop, diff=0., overflow=False, multiFactor=1
		wrappedDetector = MarAxisWrapper(detector, isccd, exposureTime,
			axis, step, sync=sync, fileName=fileName,
			noOfExpPerPos=noOfExpPerPos, rock=rock, pause=pause, fixedVelocity=fixedVelocity)
	
	elif isinstance(detector, PerkinElmer):
		# Not used: start, stop, diff=0., overflow=False, multiFactor=1
		wrappedDetector = PerkinElmerAxisWrapper(detector, isccd,
			jythonNameMap.prop, jythonNameMap.feabsb, jythonNameMap.fmfabsb,
			exposureTime, axis, step, sync=sync, fileName=fileName,
			noOfExpPerPos=noOfExpPerPos, rock=rock, pause=pause,
			exposeDark=exposeDark)
	
	elif isinstance(detector, ProcessingDetectorWrapper) and \
		 isinstance(detector.det, PerkinElmer):
		# Not used: start, stop, diff=0., overflow=False, multiFactor=1
		wrappedDetector = PerkinElmerAxisWrapper(detector.det, isccd,
			jythonNameMap.prop, jythonNameMap.feabsb, jythonNameMap.fmfabsb,
			exposureTime, axis, step, sync=sync, fileName=fileName,
			noOfExpPerPos=noOfExpPerPos, rock=rock, pause=pause,
			exposeDark=exposeDark)
	
	elif isinstance(detector, SwitchableHardwareTriggerableProcessingDetectorWrapper) and \
		 isinstance(detector.det, NXDetector):
		# Not used: start, stop, diff=0., overflow=False, multiFactor=1
		wrappedDetector = AreaDetectorAxisWrapper(detector.det, isccd,
			jythonNameMap.prop, jythonNameMap.feabsb, jythonNameMap.fmfabsb,
			exposureTime, axis, step, sync=sync, fileName=fileName,
			noOfExpPerPos=noOfExpPerPos, rock=rock, pause=pause,
			exposeDark=exposeDark)
	else:
		raise "Unknown detector passed into scan" + str(type(detector))
	return wrappedDetector
