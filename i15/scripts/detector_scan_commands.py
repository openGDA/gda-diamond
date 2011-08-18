import sys
import gda
import ruby_scripts
import pd_pilatus
import detector_axis_wrappers
import dummy_scan_objects
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
from time import sleep
from time import clock
from gda.jython.commands.GeneralCommands import pause
from gda.scan import ConcurrentScan
from gdascripts.pd.dummy_pds import DummyPD
from ccdScanMechanics import setMaxVelocity
from ccdScanMechanics import deactivatePositionCompare
from operationalControl import moveMotor
from ccdAuxiliary import openCCDShield
from ccdScanMechanics import scanGeometry
from ccdAuxiliary import incrementCCDScanNumber
from marAuxiliary import checkMarIsReady
from marAuxiliary import openMarShield
from marAuxiliary import incrementMarScanNumber
from shutterCommands import openEHShutter, closeEHShutter
from gda.device.scannable import PseudoDevice
from gdascripts.parameters import beamline_parameters

class DiodeController(PseudoDevice):
	def __init__(self, exposeDarkFlag=False, rubyNotAtlas=False):
		self.setName("diodes")
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.d1out = jythonNameMap.d1out
		self.d2out = jythonNameMap.d2out
		self.d3out = jythonNameMap.d3out
		if rubyNotAtlas:
			self.isccd = jythonNameMap.ruby
		else:
			self.isccd = jythonNameMap.atlas
		self.openEHShutter = jythonNameMap.openEHShutter
		self.exposeDarkFlag = exposeDarkFlag
		
	def atScanStart(self):
		self.d1out()
		self.d2out()
		self.d3out()
		
		self.isccd.closeS()

		if (self.exposeDarkFlag):
			simpleLog("Dark expose")
			closeEHShutter()
		else:
			openEHShutter()
		
	def atScanEnd(self):
		self.isccd.closeS()
		closeEHShutter()

	def rawGetPosition(self):
		return 1

	def rawIsBusy(self):
		return 0

	def rawAsynchronousMoveTo(self,position):
		pass
	
	
def simpleScan(axis, start, stop, step, detector, exposureTime, noOfExpPerPos=1, fileName="scan_test", pause=False):
	
	wrappedDetector = detector_axis_wrappers._getWrappedDetector(axis, start, stop, step, detector, exposureTime, noOfExpPerPos=noOfExpPerPos, fileName=fileName, sync=True, pause=pause)
	scan = ConcurrentScan([DiodeController(), 1, 1, 1, wrappedDetector, start, stop-step, step])
	scan.runScan()
	
def simpleScanOverflow(axis, start, stop, step, detector, exposureTime, noOfExpPerPos=1, fileName="scan_test", multiFactor=2, pause=False, overflow=True):
	
	wrappedDetector = detector_axis_wrappers._getWrappedDetector(axis, start, stop, step, detector, exposureTime, noOfExpPerPos=noOfExpPerPos, fileName=fileName, sync=True, pause=pause, overflow=overflow, multiFactor=multiFactor)
	scan = ConcurrentScan([DiodeController(), 1, 1, 1, wrappedDetector, start, stop-step, step])
	scan.runScan()
	
def simpleScanDel(axis, start, stop, step, detector, exposureTime, noOfExpPerPos=1, fileName="scan_test", delay=0):
	
	if delay>0:
		speed = float(step)/float(exposureTime)
		exposureTimeD = float(exposureTime) + float(delay)
		stepD = float(speed)*float(exposureTimeD)
		startD = float(start) + float(step) - float(stepD)
		diff = stepD-step
		
		simpleLog( "speed=" + `speed`)
		simpleLog( "startD=" + `startD`)
		simpleLog( "stepD=" + `stepD`)
		simpleLog( "diffexposureTimeD=" + `exposureTimeD`)
		simpleLog( "diff=" + `diff`)
	
	wrappedDetector = detector_axis_wrappers._getWrappedDetector(axis, start, stop, step, detector, exposureTimeD, noOfExpPerPos=noOfExpPerPos, fileName=fileName, sync=True, diff=diff)
	scan = ConcurrentScan([DiodeController(), 1, 1, 1, wrappedDetector, start, stop-step, step])
	scan.runScan()

def simpleScanUnsync(axis, start, stop, step, detector, exposureTime, noOfExpPerPos=1, fileName="scan_unsync_test"):
	wrappedDetector = detector_axis_wrappers._getWrappedDetector(axis, start, stop, step, detector,  exposureTime, noOfExpPerPos=noOfExpPerPos, fileName=fileName, sync=False)
	scan = ConcurrentScan([DiodeController(), 1, 1, 1, wrappedDetector, start, stop-step, step])
	scan.runScan()

def rockScan(axis, centre, rockSize, noOfRocks, detector, exposureTime, fileName="rock_scan_test"):
	wrappedDetector = detector_axis_wrappers._getWrappedDetector(axis, centre - abs(rockSize), centre + abs(rockSize), abs(2*rockSize), detector,  exposureTime, noOfExpPerPos=noOfRocks, fileName=fileName, sync=True, rock=True)
	scan = ConcurrentScan([DiodeController(), 1, 1, 1, wrappedDetector, centre - abs(rockSize), centre - abs(rockSize), abs(2*rockSize)])
	scan.runScan()
	
def rockScanUnsync(axis, centre, rockSize, noOfRocks, detector, exposureTime, fileName="rock_scan_test"):
	wrappedDetector = detector_axis_wrappers._getWrappedDetector(axis, centre - abs(rockSize), centre + abs(rockSize), abs(2*rockSize), detector,  exposureTime, noOfExpPerPos=noOfRocks, fileName=fileName, sync=False)
	scan = ConcurrentScan([DiodeController(), 1, 1, 1, wrappedDetector, centre - abs(rockSize), centre - abs(rockSize), abs(2*rockSize)])
	scan.runScan()

def doubleScan(axis, start, stop, step, detector, exposureTime, fileName="double_scan_test"):
	if isinstance(detector, ruby_scripts.Ruby):
		wrappedDetector = detector_axis_wrappers.RubyAxisWrapper(detector, exposureTime, axis, start, stop, step, sync=True, fileName=fileName, scanDoubleFlag=True)
	else:
		raise "Detector must be Ruby"
	
	scan = ConcurrentScan([DiodeController(), 1, 1, 1, wrappedDetector, start, stop-step, step])
	scan.runScan()

def expose(detector, exposureTime=1, noOfExposures=1, fileName="expose_test"):
	wrappedDetector = detector_axis_wrappers._getWrappedDetector(None, 1, 1, 1, detector,  exposureTime, noOfExpPerPos=noOfExposures, fileName=fileName, sync=False, rock=True)
	numExposuresPD = DummyPD("exposure")
	scan = ConcurrentScan([DiodeController(), 1, 1, 1, numExposuresPD, 1, noOfExposures, 1, wrappedDetector])
	scan.runScan()
	
def darkExpose(detector, exposureTime=1, noOfExposures=1, fileName="dark_expose_test"):
	wrappedDetector = detector_axis_wrappers._getWrappedDetector(axis=None,
		start=1, stop=1, step=1, detector=detector, exposureTime=exposureTime,
		noOfExpPerPos=noOfExposures, fileName=fileName, sync=False, exposeDark=True)
	numExposuresPD = DummyPD("exposure")
	#scan = ConcurrentScan([DiodeController(exposeDarkFlag=True), 1, 1, 1, numExposuresPD, 1, noOfExposures, 1, wrappedDetector, exposureTime]) # Is this needed for non pe?
	scan = ConcurrentScan([DiodeController(exposeDarkFlag=True), 1, 1, 1, numExposuresPD, 1, noOfExposures, 1, wrappedDetector])
	scan.runScan()
	
