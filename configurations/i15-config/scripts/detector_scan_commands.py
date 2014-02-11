#from scannables.detectors.detectorAxisWrapper import _getWrappedDetector
from gdascripts.messages.handle_messages import simpleLog
from gda.scan import ConcurrentScan, ConstantVelocityScanLine
from gdascripts.pd.dummy_pds import DummyPD
from shutterCommands import openEHShutter, closeEHShutter
from gda.device.scannable import ScannableBase
from gdascripts.parameters import beamline_parameters

# If the functions or defaults values below change, please update the user wiki
# page: http://wiki.diamond.ac.uk/Wiki/Wiki.jsp?page=Exposures%20and%20scans%20using%20mar%2C%20ccd%2C%20Pilatus%2C%20etc.
class DiodeController(ScannableBase):
	def __init__(self, d1out, d2out, exposeDarkFlag=False):
		self.setName("diodes")
		self.setInputNames([])
		self.setExtraNames([]);
		self.setOutputFormat([])
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.d1out = jythonNameMap.d1out if d1out else None
		self.d2out = jythonNameMap.d2out if d2out else None
		self.d3out = jythonNameMap.d3out
		self.zebraFastShutter = jythonNameMap.zebraFastShutter
		self.openEHShutter = jythonNameMap.openEHShutter
		self.exposeDarkFlag = exposeDarkFlag
		
	def atScanStart(self):
		if self.d1out:
			self.d1out()
		else:
			simpleLog("DiodeController: d1out disabled.")
		
		if self.d2out:
			self.d2out()
		else:
			simpleLog("DiodeController: d2out disabled.")
		
		self.d3out()
		
		self.zebraFastShutter.forceOpenRelease()
		
		if (self.exposeDarkFlag):
			simpleLog("Dark expose, so closing the EH shutter...")
			closeEHShutter()
		else:
			openEHShutter()
		
	def atScanEnd(self):
		self.zebraFastShutter.forceOpenRelease()
		closeEHShutter()

	def rawGetPosition(self):
		return None

	def rawIsBusy(self):
		return False

"""
def simpleScan(axis, start, stop, step, detector, exposureTime,
		noOfExpPerPos=1, fileName="scan_test",
		pause=False, d1out=True, d2out=True):
	
	wrappedDetector = _getWrappedDetector(axis,
		start, stop, step, detector, exposureTime,
		noOfExpPerPos=noOfExpPerPos, fileName=fileName, sync=True, pause=pause)
	scan = ConcurrentScan([DiodeController(d1out, d2out), 1, 1, 1,
						   wrappedDetector, start, stop-step, step])
	scan.runScan()
	
def simpleScanOverflow(axis, start, stop, step, detector, exposureTime,
		noOfExpPerPos=1, fileName="scan_test", multiFactor=2, pause=False,
		overflow=True, d1out=True, d2out=True):
	
	wrappedDetector = _getWrappedDetector(axis,
		start, stop, step, detector, exposureTime,
		noOfExpPerPos=noOfExpPerPos, fileName=fileName, sync=True, pause=pause,
		overflow=overflow, multiFactor=multiFactor)
	scan = ConcurrentScan([DiodeController(d1out, d2out), 1, 1, 1,
						   wrappedDetector, start, stop-step, step])
	scan.runScan()
	
def simpleScanDel(axis, start, stop, step, detector, exposureTime,
		noOfExpPerPos=1, fileName="scan_test", delay=0, d1out=True, d2out=True):
	
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
	
	wrappedDetector = _getWrappedDetector(axis,
		start, stop, step, detector, exposureTimeD,
		noOfExpPerPos=noOfExpPerPos, fileName=fileName, sync=True, diff=diff)
	scan = ConcurrentScan([DiodeController(d1out, d2out), 1, 1, 1,
						   wrappedDetector, start, stop-step, step])
	scan.runScan()

def simpleScanUnsync(axis, start, stop, step, detector, exposureTime,
		noOfExpPerPos=1, fileName="scan_unsync_test", d1out=True, d2out=True):
	wrappedDetector = _getWrappedDetector(axis,
		start, stop, step, detector,  exposureTime,
		noOfExpPerPos=noOfExpPerPos, fileName=fileName, sync=False)
	scan = ConcurrentScan([DiodeController(d1out, d2out), 1, 1, 1,
		wrappedDetector, start, stop-step, step])
	scan.runScan()

def rockScan(axis, centre, rockSize, noOfRocks, detector, exposureTime,
		fileName="rock_scan_test", d1out=True, d2out=True):
	wrappedDetector = _getWrappedDetector(
		axis, centre - abs(rockSize), centre + abs(rockSize), abs(2*rockSize),
		detector,  exposureTime, noOfExpPerPos=noOfRocks, fileName=fileName,
		sync=True, rock=True)
	scan = ConcurrentScan([DiodeController(d1out, d2out), 1, 1, 1,
		wrappedDetector, centre - abs(rockSize), centre - abs(rockSize),
			abs(2*rockSize)])
	scan.runScan()
"""

def _configureConstantVelocityMove(axis):
	supportedMotors = ('dkphi',)
	if not (axis.name in supportedMotors):
		raise Exception('Motor %r not in the list of supported motors: %r' % (axis.name, supportedMotors))
	
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	
	if axis.name == "dkphi":
		continuouslyScannableViaController = jythonNameMap.dkphiZebraScannableMotor
		continuousMoveController = jythonNameMap.zebraContinuousMoveController
	else:
		raise Exception('Error configuring motor %r' % (axis.name))
	
	return continuouslyScannableViaController, continuousMoveController

def rockScan(axis, centre, rockSize, noOfRocks, detector, exposureTime,
		sampleSuffix="rockScan_test", d1out=True, d2out=True):
	# Based on gda-dls-beamlines-i13x.git/i13i/scripts/flyscan.py @136034c  (8.36)
	
	hardwareTriggeredNXDetector = _configureDetector(detector, noOfRocks, sampleSuffix)
	continuouslyScannableViaController, continuousMoveController = _configureConstantVelocityMove(axis)
	
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	detectorShield = jythonNameMap.ds
	numExposuresPD = DummyPD("exposure")
	
	sc1=ConstantVelocityScanLine([continuouslyScannableViaController, centre, centre, abs(2*rockSize),
								  continuousMoveController,
								  hardwareTriggeredNXDetector, exposureTime,
								])
	
	scan = ConcurrentScan([numExposuresPD, 1, noOfRocks, 1,
						   detectorShield,
						   DiodeController(d1out, d2out),
						   sc1
						 ])
	scan.runScan()

"""
def rockScanUnsync(axis, centre, rockSize, noOfRocks, detector, exposureTime,
		fileName="rock_scan_test", d1out=True, d2out=True, fixedVelocity=False):
	wrappedDetector = _getWrappedDetector(
		axis, centre - abs(rockSize), centre + abs(rockSize), abs(2*rockSize),
		detector,  exposureTime, noOfExpPerPos=noOfRocks, fileName=fileName,
		sync=False, fixedVelocity=fixedVelocity)
	scan = ConcurrentScan([DiodeController(d1out, d2out), 1, 1, 1,
		wrappedDetector, centre - abs(rockSize), centre - abs(rockSize),
			abs(2*rockSize)])
	scan.runScan()

def expose(detector, exposureTime=1, noOfExposures=1,
		fileName="expose_test", d1out=True, d2out=True):
	wrappedDetector = _getWrappedDetector(None, 1, 1, 1,
		detector, exposureTime, noOfExpPerPos=1, fileName=fileName,
		sync=False, rock=True)
	# We say noOfExpPerPos=1 in _getWrappedDetector as we are going to use
	# a DummyPD to count the number of exposures.
	numExposuresPD = DummyPD("exposure")
	scan = ConcurrentScan([DiodeController(d1out, d2out), 1, 1, 1,
						   numExposuresPD, 1, noOfExposures, 1,
						   wrappedDetector, 1, 1, 1])
	scan.runScan()
"""

def _configureDetector(detector, numberOfExposures, sampleSuffix):
	supportedDetectors = ('mar', 'pe')
	if not (detector.name in supportedDetectors):
		raise Exception('Detector %r not in the list of supported detectors: %r' % (detector.name, supportedDetectors))
	
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	
	if detector.name == "mar":
		hardwareTriggeredNXDetector = jythonNameMap.marHWT
	elif detector.name == "pe":
		hardwareTriggeredNXDetector = jythonNameMap.peHWT
	else:
		raise Exception('Error configuring detector %r' % (detector.name))
	
	detector.hdfwriter.setFileTemplate(		"%s%s.hdf5")
	detector.hdfwriter.setFilePathTemplate(	"$datadir$")
	detector.hdfwriter.setFileNameTemplate(	"$scan$-%s-" % detector.name + sampleSuffix)
	
	detector.tifwriter.setFileTemplate(		"%s%s%05d.tif")
	if numberOfExposures == 1:
		detector.tifwriter.setFilePathTemplate(	"$datadir$/")
		detector.tifwriter.setFileNameTemplate(	"$scan$-%s-" % detector.name + sampleSuffix)
	else:
		detector.tifwriter.setFilePathTemplate(	"$datadir$/$scan$-%s-files-" % detector.name + sampleSuffix)
		detector.tifwriter.setFileNameTemplate(	"")
	
	return hardwareTriggeredNXDetector

def expose(detector, exposureTime=1, noOfExposures=1,
		sampleSuffix="expose_test", d1out=True, d2out=True):
	
	_configureDetector(detector, noOfExposures, sampleSuffix)

	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	detectorShield = jythonNameMap.ds
	numExposuresPD = DummyPD("exposure")
	zebraFastShutter = jythonNameMap.zebraFastShutter
	
	scan = ConcurrentScan([numExposuresPD, 1, noOfExposures, 1,
						   detectorShield,
						   DiodeController(d1out, d2out),
						   detector, exposureTime,
						   zebraFastShutter, exposureTime ])
	scan.runScan()

def darkExpose(detector, exposureTime=1, 
		sampleSuffix="darkExpose_test", d1out=True, d2out=True):
	
	_configureDetector(detector, 1, sampleSuffix)

	scan = ConcurrentScan([DiodeController(d1out, d2out, exposeDarkFlag=True), 1, 1, 1,
						   detector, exposureTime,
						 ])
	scan.runScan()

"""
def darkExpose(detector, exposureTime=1, noOfExposures=1,
		fileName="dark_expose_test", d1out=True, d2out=True):
	wrappedDetector = _getWrappedDetector(axis=None,
		start=1, stop=1, step=1, detector=detector, exposureTime=exposureTime,
		noOfExpPerPos=1, fileName=fileName, sync=False, exposeDark=True)
	# We say noOfExpPerPos=1 in _getWrappedDetector as we are going to use
	# a DummyPD to count the number of exposures.
	numExposuresPD = DummyPD("exposure")
	scan = ConcurrentScan([DiodeController(d1out, d2out, exposeDarkFlag=True), 1, 1, 1,
						   numExposuresPD, 1, noOfExposures, 1,
						   wrappedDetector, 1, 1, 1])
	scan.runScan()
"""