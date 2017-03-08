#from scannables.detectors.detectorAxisWrapper import _getWrappedDetector
from gdascripts.messages.handle_messages import simpleLog
from gda.scan import ConcurrentScan, ConstantVelocityScanLine
from gdascripts.pd.dummy_pds import DummyPD
from localStationScripts.shutterCommands import openEHShutter, closeEHShutter
from gda.device.scannable import ScannableBase
from gdascripts.parameters import beamline_parameters
from gdascripts.utils import caget, caput
from time import sleep
from org.slf4j import LoggerFactory

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

""" Never implemented since switch to Geobrick
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
"""

""" Pre geobrick
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

def _configureConstantVelocityMove(axis, detector):
	supportedMotors = ('dkphi', 'dkappa', 'dktheta')
	if not (axis.name in supportedMotors):
		raise Exception('Motor %r not in the list of supported motors: %r' % (axis.name, supportedMotors))

	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	continuousMoveController = detector.getHardwareTriggerProvider()

	if axis.name == "dkphi":
		continuouslyScannableViaController = jythonNameMap.dkphiZebraScannableMotor
	elif axis.name == "dkappa":
		continuouslyScannableViaController = jythonNameMap.dkappaZebraScannableMotor
	elif axis.name == "dktheta":
		continuouslyScannableViaController = jythonNameMap.dkthetaZebraScannableMotor
	else:
		raise Exception('Error configuring motor %r' % (axis.name))
	
	return continuouslyScannableViaController, continuousMoveController

""" Pre usercommands.py
def rockScan(axis, centre, rockSize, noOfRocksPerExposure, detector, exposureTime, noOfExposures=1,
		sampleSuffix="rockScan_test", d1out=True, d2out=True):
	# Based on gda-dls-beamlines-i13x.git/i13i/scripts/flyscan.py @136034c  (8.36)
	
	if noOfRocksPerExposure <> 1:
		raise Exception("noOfRocksPerExposure=%r is not supported. Only noOfRocksPerExposure=1 is currently supported, if you want multiple rocks with each in a different exposure, set noOfExposures. If you want multiple rocks in the same image, use rockScanUnsync" % noOfRocksPerExposure)
	
	hardwareTriggeredNXDetector = _configureDetector(detector, exposureTime, noOfExposures, sampleSuffix, dark=False)
	continuouslyScannableViaController, continuousMoveController = _configureConstantVelocityMove(axis, hardwareTriggeredNXDetector)
	
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	detectorShield = jythonNameMap.ds
	numExposuresPD = DummyPD("exposure")
	
	sc1=ConstantVelocityScanLine([continuouslyScannableViaController, centre, centre, abs(2*rockSize),
								  continuousMoveController,
								  hardwareTriggeredNXDetector, exposureTime,
								])
	
	scan = ConcurrentScan([numExposuresPD, 1, noOfExposures, 1,
						   detectorShield,
						   DiodeController(d1out, d2out),
						   sc1
						 ])
	scan.runScan()
	
	print "Moving %s back to %r" % (axis.name, centre)
	axis.moveTo(centre)
"""

""" Pre geobrick
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
"""

""" Requires disabled expose command
def rockScanUnsync(axis, centre, rockSize, noOfRocksPerExposure, detector, exposureTime, noOfExposures=1,
		sampleSuffix="rockScanUnsync_test", d1out=True, d2out=True):
	# Based on gda-dls-beamlines-i13x.git/i13i/scripts/flyscan.py @136034c  (8.36)
	
	if noOfExposures <> 1:
		raise Exception("noOfExposures=%r is not supported. Only noOfExposures=1 is currently supported, if you want multiple rocks with each in a different exposure, use rockScan" % noOfExposures)
	
	if   axis.name == "dkphi_rocker":
		rockScanUnsyncJythonRocker(axis, centre, rockSize, noOfRocksPerExposure, detector, exposureTime, noOfExposures, sampleSuffix, d1out, d2out)
	elif axis.name == "dkphi_rockscan":
		rockScanUnsyncEpicsRocker( axis, centre, rockSize, noOfRocksPerExposure, detector, exposureTime, noOfExposures, sampleSuffix, d1out, d2out)
	else:
		raise Exception('Unsupported motor %r, only dkphi_rocker or dkphi_rockscan supported.' % (axis.name))
	
def rockScanUnsyncJythonRocker(axis, centre, rockSize, noOfRocksPerExposure, detector, exposureTime, noOfExposures=1,
		sampleSuffix="rockScanUnsync_test", d1out=True, d2out=True):
	
	orig_speed = axis.scannable.speed
	
	#speed = float(rockSize)/float(exposureTime)*float(noOfRocksPerExposure)
	
	ACCL = 0.25
	timePerRock = float(exposureTime) / float(noOfRocksPerExposure)
	# speed   ____________
	#        /            \
	#       /              \
	#      /                \
	#     /                  \
	#    |ACCL|cruiseTime|ACCL|
	#    |    timePerRock     |
	#    cruiseTime = timePerRock - 2.*ACCL
	#    speed = rockSize / (cruiseTime + ACCL)
	speed = float(rockSize*2) / (timePerRock - ACCL)
	
	# Old calc							New calc
	# rockSize = 5						
	# exposureTime = 300				
	# noOfRocksPerExposure = 100		accl = 0.25

	# speed = 1.666						timePerRock = 3
	# timePerRock = 3+0.25				speed = 1.818

	speed_min = 0.1
	speed_max = 8.0
	if speed > speed_max:
		raise Exception('Speed %r too high (max= %r), reduce noOfRocksPerExposure.' % (speed, speed_max))
	elif speed < speed_min:
		raise Exception('Speed %r too low (min= %r), increase noOfRocksPerExposure.' % (speed, speed_min))
	
	print "Moving %s at speed %r" % (axis.name, speed)
	
	axis.scannable.speed = speed
	axis.moveTo( [centre, rockSize] )
	
	expose(detector, exposureTime=exposureTime, noOfExposures=noOfExposures,
		sampleSuffix=sampleSuffix, d1out=d1out, d2out=d2out)
	
	print "Stopping %s and setting speed back to %r" % (axis.name, orig_speed)
	axis.stop()
	sleep(1) # The speed setting fails if immediately after a stop!
	axis.scannable.speed = orig_speed
	print "Moving %s back to %r" % (axis.name, centre)
	axis.moveTo( [centre, 0] )

def rockScanUnsyncEpicsRocker(axis, centre, rockSize, noOfRocksPerExposure, detector, exposureTime, noOfExposures=1,
		sampleSuffix="rockScanUnsync_test", d1out=True, d2out=True):

	print "Moving %s to start position %r" % (axis.name, centre-rockSize)
	axis.scannable.moveTo(centre-rockSize) # Go to start position

	axis.setupScan(centre, rockSize, noOfRocksPerExposure)

	_configureDetector(detector, exposureTime, noOfExposures, sampleSuffix, dark=False)

	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	detectorShield = jythonNameMap.ds
	numExposuresPD = DummyPD("exposure")
	zebraFastShutter = jythonNameMap.zebraFastShutter
	
	scan = ConcurrentScan([numExposuresPD, 1, noOfExposures, 1,
						   detectorShield,
						   DiodeController(d1out, d2out),
						   detector, exposureTime,
						   zebraFastShutter, exposureTime,
						   axis, exposureTime ])
	scan.runScan()
	
	print "Moving %s back to %r" % (axis.name, centre)
	axis.scannable.moveTo(centre) # Go back to centre
"""

""" Pre geobrick
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

def _configureDetector(detector, exposureTime, noOfExposures, sampleSuffix, dark):
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	LoggerFactory.getLogger("detector_scan_commands.py").trace(
		"configureDetector(detector=%r, exposureTime=%r, noOfExposures=%r, sampleSuffix=%r, dark=%r)" % (
							detector, exposureTime, noOfExposures, sampleSuffix, dark))

	supportedDetectors = {'mar':    jythonNameMap.marHWT
						, 'marHWT': detector
						, 'pe':     detector
						, 'mpx':    jythonNameMap.mpxHWT
						, 'mpxHWT': detector
						, 'mpxc':   jythonNameMap.mpxcHWT
						, 'mpxcHWT':detector
						, 'mpxthr':   jythonNameMap.mpxthrHWT
						, 'mpxthrHWT':detector
						, 'pil3':    jythonNameMap.pil3HWT
						, 'pil3HWT': detector
						, 'atlas':   detector
						, 'atlasOverflow': detector
						}
	
	# Since the interface changed, check that noOfExposures is numeric
	if not isinstance(noOfExposures, (int, long, float)):
		raise TypeError("noOfExposures=%r (%s), but expected it to be numeric!" % (noOfExposures, type(noOfExposures),))
	
	if supportedDetectors.has_key(detector.name):
		hardwareTriggeredNXDetector = supportedDetectors[detector.name]
	else:
		raise Exception('Detector %r not in the list of supported detectors: %r' % (detector.name, supportedDetectors.keys()))
	
	# Configure single file filewriters first
	
	filePathTemplate="$datadir$/"
	if detector.name in ("pe"):
		fileNameTemplate="%s-%s-$scan$" % (detector.name, sampleSuffix)
		print "%s detector now using filenames where detector and sample names come before scan number." % detector.name
	else:
		fileNameTemplate="$scan$-%s-%s" % (detector.name, sampleSuffix)
		print "%s has not been tested with using filenames where detector and sample names come before scan number." % detector.name

	fileTemplate="%s%s"
	
	if 'hdfwriter' in [p.getName() for p in detector.getPluginList()]:
		detector.hdfwriter.setFileTemplate(fileTemplate+".hdf5")
		detector.hdfwriter.setFilePathTemplate(filePathTemplate)
		detector.hdfwriter.setFileNameTemplate(fileNameTemplate)

	# Then configure multi-file filewriters
	
	collectionStrategy = detector.getCollectionStrategy()

	if noOfExposures != 1:
		filePathTemplate="$datadir$/$scan$-%s-files-%s/" % (detector.name, sampleSuffix)
		fileNameTemplate=""
		fileTemplate="%s%s%05d"	# One image per file
	
	if 'marwriter' in [p.getName() for p in detector.getPluginList()]:
		# Since the mar doesn't like underscores and replaces all characters after the underscore with a three
		# digit sequence number, we have to strip out any underscores and ensure that a sequence number is added.
		if "_" in sampleSuffix:
			raise Exception('Detector %r does not support underscores in sampleSuffix: %s' % (detector.name, sampleSuffix))
		fileTemplate="%s%s_%03d" # Breaks GDA because it expects the file to be called blah and it is blah.mar3450 on the filesystem
		#fileTemplate="%s%s_%03d.mar3450" # Breaks Area detector because it expects the file to be called blah.mar3450.mar3450 and it is blah.mar3450 on the filesystem
		
		detector.marwriter.setFileTemplate(fileTemplate)
		detector.marwriter.setFilePathTemplate(filePathTemplate)
		detector.marwriter.setFileNameTemplate(fileNameTemplate)
	
	if 'tifwriter' in [p.getName() for p in detector.getPluginList()]:
		detector.tifwriter.setFileTemplate(fileTemplate+".tif")
		detector.tifwriter.setFilePathTemplate(filePathTemplate)
		detector.tifwriter.setFileNameTemplate(fileNameTemplate)
	
	from gda.device.detector.odccd.collectionstrategy import ODCCDSingleExposure
	if isinstance(collectionStrategy, ODCCDSingleExposure):
		filePathTemplate="$datadir$/_$scan$-%s-files-%s/" % (detector.name, sampleSuffix) # Atlas directories cannot start with a number.
		collectionStrategy.setFileTemplate(fileTemplate+".img")
		collectionStrategy.setFilePathTemplate(filePathTemplate)
		collectionStrategy.setFileNameTemplate("_" + fileNameTemplate) # Atlas filenames cannot start with a number.
	elif detector.name == 'atlas':
		print "'ODCCD' not in Plugin List!"
	
	darkSubtractionPVs=_darkSubtractionPVs(hardwareTriggeredNXDetector)
	if darkSubtractionPVs:
		darkSubtractionArray = caget(darkSubtractionPVs['array']+"EnableBackground_RBV")
		darkSubtractionLive =  caget(darkSubtractionPVs['live'] +"EnableBackground_RBV")
		print "Dark subtraction %r on array and %r on live for detector %s " % (
			darkSubtractionArray, darkSubtractionLive, hardwareTriggeredNXDetector.name)

	return hardwareTriggeredNXDetector

""" Replaced with new user_commands expose
def expose(detector, exposureTime=1, noOfExposures=1,
		sampleSuffix="expose_test", d1out=True, d2out=True):
	
	_configureDetector(detector, exposureTime, noOfExposures, sampleSuffix, dark=False)

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
"""

def _darkExpose(detector, exposureTime=1, 
		sampleSuffix="expose_test", d1out=True, d2out=True):
	
	_configureDetector(detector, exposureTime, 1, "%s(%rs_dark)" % (sampleSuffix, exposureTime), dark=True)

	darkSubtractionPVs = _darkSubtractionPVs(detector)
	if not darkSubtractionPVs:
		raise Exception('No support for dark subtraction on detector %r' % (detector.name))
	
	print "Dark subtraction is " + caget(darkSubtractionPVs['array']+"EnableBackground_RBV") + " on array"
	print "Dark subtraction is " + caget(darkSubtractionPVs['live'] +"EnableBackground_RBV") + " on live"

	print "Disabling dark subtraction before dark collection"
	caput(darkSubtractionPVs['array']+"EnableBackground", 0)
	caput(darkSubtractionPVs['live' ]+"EnableBackground", 0)
	
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	detectorShield = jythonNameMap.ds
	numExposuresPD = DummyPD("exposure")

	scan = ConcurrentScan([numExposuresPD, 1, 1, 1,
						   detectorShield,
						   DiodeController(d1out, d2out, exposeDarkFlag=True),
						   detector, exposureTime ])
	scan.runScan()

	print "Saving dark image into area detector after dark collection"
	caput(darkSubtractionPVs['array']+"SaveBackground", 1)
	caput(darkSubtractionPVs['live' ]+"SaveBackground", 1)

	print "Enabling dark subtraction"
	caput(darkSubtractionPVs['array']+"EnableBackground", 1)
	caput(darkSubtractionPVs['live' ]+"EnableBackground", 1)

def _darkSubtractionPVs(detector):
	if detector.name in ("pe"):
		return {'array':"BL15I-EA-DET-01:PROC3:", 'live':"BL15I-EA-DET-01:PROC4:"}
	else:
		return None
""" Pre geobrick
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