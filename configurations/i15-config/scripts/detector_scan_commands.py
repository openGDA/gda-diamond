#from scannables.detectors.detectorAxisWrapper import _getWrappedDetector
from gdascripts.messages.handle_messages import simpleLog
from gda.scan import ConcurrentScan
from gdascripts.pd.dummy_pds import DummyPD
from shutterCommands import openEHShutter, closeEHShutter
from gda.device.scannable import PseudoDevice
from gdascripts.parameters import beamline_parameters

# If the functions or defaults values below change, please update the user wiki
# page: http://wiki.diamond.ac.uk/Wiki/Wiki.jsp?page=Exposures%20and%20scans%20using%20mar%2C%20ccd%2C%20Pilatus%2C%20etc.
class DiodeController(PseudoDevice):
	def __init__(self, d1out, d2out, exposeDarkFlag=False):
		self.setName("diodes")
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
			simpleLog("Dark expose")
			closeEHShutter()
		else:
			openEHShutter()
		
	def atScanEnd(self):
		self.zebraFastShutter.forceOpenRelease()
		closeEHShutter()

	def rawGetPosition(self):
		return 1

	def rawIsBusy(self):
		return 0

	def rawAsynchronousMoveTo(self,position):
		pass

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

def expose(detector, exposureTime=1, noOfExposures=1,
		fileName="expose_test", d1out=True, d2out=True):
	
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	zebraFastShutter = jythonNameMap.zebraFastShutter
	ds = jythonNameMap.ds
	
	if detector.name == "pe":
		detector = jythonNameMap.pedet
	elif not (detector.name in ('mar', 'pedet')):
		raise Exception('Only supports "mar" and "pedet" Area detectors!')
	
	if detector.name == 'mar':
		detector.hdfwriter.setFileTemplate(		"%s%s%05d.hdf5")
		detector.hdfwriter.setFilePathTemplate(	"$datadir$")
		detector.hdfwriter.setFileNameTemplate(	"$scan$-%s-" % detector.name + fileName)
	
	detector.tifwriter.setFileTemplate(		"%s%s%05d.tif")
	detector.tifwriter.setFilePathTemplate(	"$datadir$/$scan$-%s-files-" % detector.name + fileName)
	detector.tifwriter.setFileNameTemplate(	"")
	
	numExposuresPD = DummyPD("exposure")
	scan = ConcurrentScan([ds, 1, 1, 1,
						   DiodeController(d1out, d2out), 1, 1, 1,
						   numExposuresPD, 1, noOfExposures, 1,
						   detector, exposureTime,
						   zebraFastShutter, exposureTime ])
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