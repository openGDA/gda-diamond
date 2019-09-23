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
	def __init__(self, d1out, d2out, d3out, exposeDarkFlag=False, suppressCloseEHShutterAtScanEnd=False):
		self.setName("diodes")
		self.setInputNames([])
		self.setExtraNames([]);
		self.setOutputFormat([])
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.d1out = jythonNameMap.d1out if d1out else None
		self.d2out = jythonNameMap.d2out if d2out else None
		self.d3out = jythonNameMap.d3out if d3out else None
		self.zebraFastShutter = jythonNameMap.zebraFastShutter
		self.openEHShutter = jythonNameMap.openEHShutter
		self.exposeDarkFlag = exposeDarkFlag
		self.suppressCloseEHShutterAtScanEnd = suppressCloseEHShutterAtScanEnd
		
	def atScanStart(self):
		if self.d1out:
			self.d1out()
		else:
			simpleLog("DiodeController: d1out disabled.")
		
		if self.d2out:
			self.d2out()
		else:
			simpleLog("DiodeController: d2out disabled.")
		
		if self.d3out:
			self.d3out()
		else:
			simpleLog("DiodeController: d3out disabled.")
		
		self.zebraFastShutter.forceOpenRelease()
		
		if (self.exposeDarkFlag):
			simpleLog("DiodeController: Dark expose, so closing the EH shutter...")
			closeEHShutter()
		else:
			openEHShutter()
		
	def atScanEnd(self):
		self.zebraFastShutter.forceOpenRelease()
		if self.suppressCloseEHShutterAtScanEnd:
			simpleLog("""%s
			  EH shutter close is suppressed.
			  You MUST ensure the shutter is closed manually after your scan:
			  >>> closeEHShutter()""" % ("DiodeController: ".ljust(80, "*")))
			simpleLog("*"*80)
		else:
			closeEHShutter()

	def getPosition(self):
		return None

	def isBusy(self):
		return False

def _configureConstantVelocityMove(axis, detector):
	supportedMotors = ('dkphi', 'dkappa', 'dktheta', 'sphi')
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
	elif axis.name == "sphi":
		continuouslyScannableViaController = jythonNameMap.sphiZebraScannableMotor
	else:
		raise Exception('Error configuring motor %r' % (axis.name))
	
	return continuouslyScannableViaController, continuousMoveController

def _configureDetector(detector, exposureTime, noOfExposures, sampleSuffix, dark):
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	LoggerFactory.getLogger("detector_scan_commands.py").trace(
		"configureDetector(detector=%r, exposureTime=%r, noOfExposures=%r, sampleSuffix=%r, dark=%r)" % (
							detector, exposureTime, noOfExposures, sampleSuffix, dark))

	supportedDetectors = {'mar':    jythonNameMap.marHWT
						, 'marHWT': detector
						, 'marTif': jythonNameMap.marTifHWT
						, 'marTifHWT': detector
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
		if "," in sampleSuffix:
			raise Exception('Detector %r does not support commas in sampleSuffix: %s' % (detector.name, sampleSuffix))
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

def _darkExpose(detector,
		exposeSuppressOpenDetectorShieldAtScanStart, exposeSuppressCloseDetectorShieldAtScanEnd,
		exposureTime=1, sampleSuffix="expose_test", d1out=True, d2out=True, d3out=True):

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
	detectorShield.suppressOpenDetectorShieldAtScanStart = exposeSuppressOpenDetectorShieldAtScanStart
	detectorShield.suppressCloseDetectorShieldAtScanEnd = exposeSuppressCloseDetectorShieldAtScanEnd

	exposure = jythonNameMap.exposure

	scan = ConcurrentScan([exposure, 1, 1, 1,
						   detectorShield,
						   DiodeController(d1out, d2out, d3out, exposeDarkFlag=True),
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
