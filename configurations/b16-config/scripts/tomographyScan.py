"""
Performs software triggered tomography
"""

#from pcoDetectorWrapper import PCODetectorWrapper
from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import NXSubEntryWriter, NXTomoEntryLinkCreator
from gda.data.scan.datawriter.DefaultDataWriterFactory import \
	createDataWriterFromFactory
from gda.device.scannable import ScannableBase, ScannableUtils, SimpleScannable
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.jython import InterfaceProvider
from gda.jython.commands.ScannableCommands import createConcurrentScan
from gda.scan import ScanPositionProvider
from gda.util import OSCommandRunner
from gdascripts.messages import handle_messages
from gdascripts.metadata.metadata_commands import setTitle
from gdascripts.parameters import beamline_parameters
from java.lang import InterruptedException
from gdascripts.utils import caget, caput
import sys
import datetime
from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan
from gda.scan import ConstantVelocityScanLine, MultiScanItem, MultiScanRunner, ConcurrentScan
from gdascripts.metadata.metadata_commands import setTitle, getTitle, meta_add


class EnumPositionerDelegateScannable(ScannableBase):
	''' Translate positions 0 and 1 to Close and Open '''
	def __init__(self, name, delegate):
		self.name = name
		self.inputNames = [name]
		self.delegate = delegate
	def isBusy(self):
		return self.delegate.isBusy()
	def rawAsynchronousMoveTo(self, new_position):
		if int(new_position) == 0:
			self.delegate.asynchronousMoveTo("Close")
		elif int(new_position) == 1:
			self.delegate.asynchronousMoveTo("Open")
	def rawGetPosition(self):
		pos = self.delegate.getPosition()
		if pos == "Close":
			return 0
		return 1


def make_tomoScanDevice(tomography_theta, tomography_shutter, tomography_translation,
						image_key, tomography_imageIndex):
	
	tomoScanDevice = ScannableGroup()
	tomoScanDevice.addGroupMember(tomography_theta)
	tomoScanDevice.addGroupMember(EnumPositionerDelegateScannable("tomography_shutter", tomography_shutter))
	tomoScanDevice.addGroupMember(tomography_translation)
	tomoScanDevice.addGroupMember(image_key)
	tomoScanDevice.addGroupMember(tomography_imageIndex)
	tomoScanDevice.setName("tomoScanDevice")
	tomoScanDevice.configure()
	return tomoScanDevice

def generateScanPoints(inBeamPosition, outOfBeamPosition, theta_points, darkFieldInterval, flatFieldInterval,
			  imagesPerDark, imagesPerFlat, optimizeBeamInterval, pattern="default"):
	numberSteps = len(theta_points) - 1
	optimizeBeamNo = 0
	optimizeBeamYes = 1
	shutterOpen = 1 # see EnumPositionerDelegateScannable
	shutterClosed = 0
	shutterNoChange = 2
	scan_points = []
	print "Using scan-point pattern:", pattern
	if pattern == 'default' or pattern == 'DFPFD':
		theta_pos = theta_points[0]
		index = 0
		#Added shutterNoChange state for the shutter. The scan points are added using the (pseudo) ternary operator, 
		#if index is 0 then the shutterPosition is added to the scan point, else shutterNoChange is added to scan points.
		for i in range(imagesPerDark):
			scan_points.append((theta_pos, [shutterClosed, shutterNoChange][i != 0], inBeamPosition, image_key_dark, index)) #dark
			index = index + 1
		
		for i in range(imagesPerFlat): 
			scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], outOfBeamPosition, image_key_flat, index)) #flat
			index = index + 1
		
		scan_points.append((theta_pos, shutterOpen, inBeamPosition, image_key_project, index)) #first
		index = index + 1
		imageSinceDark = 1
		imageSinceFlat = 1
		optimizeBeam = 0
		for i in range(numberSteps):
			theta_pos = theta_points[i + 1]
			scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], inBeamPosition, image_key_project, index))#main image
			index = index + 1
			
			imageSinceFlat = imageSinceFlat + 1
			if imageSinceFlat == flatFieldInterval and flatFieldInterval != 0:
				for i in range(imagesPerFlat):
					scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], outOfBeamPosition, image_key_flat, index))
					index = index + 1
					imageSinceFlat = 0
			
			imageSinceDark = imageSinceDark + 1
			if imageSinceDark == darkFieldInterval and darkFieldInterval != 0:
				for i in range(imagesPerDark):
					scan_points.append((theta_pos, [shutterClosed, shutterNoChange][i != 0], inBeamPosition, image_key_dark, index))
					index = index + 1
					imageSinceDark = 0
			
			optimizeBeam = optimizeBeam + 1
			if optimizeBeam == optimizeBeamInterval and optimizeBeamInterval != 0:
				scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], inBeamPosition, image_key_project, index))
				index = index + 1
				optimizeBeam = 0
		
		#add dark and flat only if not done in last steps
		if imageSinceFlat != 0:
			for i in range(imagesPerFlat):
				scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], outOfBeamPosition, image_key_flat, index)) #flat
				index = index + 1
		if imageSinceDark != 0:
			for i in range(imagesPerDark):
				scan_points.append((theta_pos, [shutterClosed, shutterNoChange][i != 0], inBeamPosition, image_key_dark, index)) #dark
				index = index + 1
	elif pattern == 'PFD':
		theta_pos = theta_points[0]
		index = 0
		
		# Don't take any dark or flat images at the beginning
		scan_points.append((theta_pos, shutterOpen, inBeamPosition, image_key_project, index)) #first
		index = index + 1
		imageSinceDark = 1
		imageSinceFlat = 1
		optimizeBeam = 0
		for i in range(numberSteps):
			theta_pos = theta_points[i + 1]
			scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], inBeamPosition, image_key_project, index))#main image
			index = index + 1
			
			imageSinceFlat = imageSinceFlat + 1
			if imageSinceFlat == flatFieldInterval and flatFieldInterval != 0:
				for i in range(imagesPerFlat):
					scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], outOfBeamPosition, image_key_flat, index))
					index = index + 1
					imageSinceFlat = 0
			
			imageSinceDark = imageSinceDark + 1
			if imageSinceDark == darkFieldInterval and darkFieldInterval != 0:
				for i in range(imagesPerDark):
					scan_points.append((theta_pos, [shutterClosed, shutterNoChange][i != 0], inBeamPosition, image_key_dark, index))
					index = index + 1
					imageSinceDark = 0
			
			optimizeBeam = optimizeBeam + 1
			if optimizeBeam == optimizeBeamInterval and optimizeBeamInterval != 0:
				scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], inBeamPosition, image_key_project, index))
				index = index + 1
				optimizeBeam = 0
		
		#add dark and flat only if not done in last steps
		if imageSinceFlat != 0:
			for i in range(imagesPerFlat):
				scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], outOfBeamPosition, image_key_flat, index)) #flat
				index = index + 1
		if imageSinceDark != 0:
			for i in range(imagesPerDark):
				scan_points.append((theta_pos, [shutterClosed, shutterNoChange][i != 0], inBeamPosition, image_key_dark, index)) #dark
				index = index + 1
	elif pattern == 'aberration':
		theta_pos = theta_points[0]
		index = 0
		
		# Don't take any dark or flat images at the beginning
		scan_points.append((theta_pos, shutterOpen, inBeamPosition, image_key_project, index)) #first
		index = index + 1
		imageSinceDark = 1
		imageSinceFlat = 1
		optimizeBeam = 0
		aberration_flat_first = True
		aberration_dark_first = True
		for i in range(numberSteps):
			if (imageSinceFlat == flatFieldInterval and flatFieldInterval != 0) or aberration_flat_first:
				for f in range(imagesPerFlat):
					#print "theta_pos1 = ", theta_pos
					scan_points.append((theta_pos, [shutterOpen, shutterNoChange][f != 0], outOfBeamPosition, image_key_flat, index))
					index = index + 1
					imageSinceFlat = 0
					aberration_flat_first = False
			
			if (imageSinceDark == darkFieldInterval and darkFieldInterval != 0) or aberration_dark_first:
				for d in range(imagesPerDark):
					scan_points.append((theta_pos, [shutterClosed, shutterNoChange][d != 0], inBeamPosition, image_key_dark, index))
					index = index + 1
					imageSinceDark = 0
					aberration_dark_first = False
			
			theta_pos = theta_points[i + 1]
			#print "i = ", i
			#print "theta_pos2 = ", theta_pos
			scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], inBeamPosition, image_key_project, index))#main image
			index = index + 1
			
			imageSinceFlat = imageSinceFlat + 1
			imageSinceDark = imageSinceDark + 1
			
			optimizeBeam = optimizeBeam + 1
			if optimizeBeam == optimizeBeamInterval and optimizeBeamInterval != 0:
				scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], inBeamPosition, image_key_project, index))
				index = index + 1
				optimizeBeam = 0
		
		#add dark and flat only if not done in last steps
		#if imageSinceFlat != 0:
		#	for i in range(imagesPerFlat):
		#		scan_points.append((theta_pos, [shutterOpen, shutterNoChange][i != 0], outOfBeamPosition, image_key_flat, index)) #flat
		#		index = index + 1
		#if imageSinceDark != 0:
		#	for i in range(imagesPerDark):
		#	   scan_points.append((theta_pos, [shutterClosed, shutterNoChange][i != 0], inBeamPosition, image_key_dark, index)) #dark
		#	   index = index + 1
	else:
		print "Unsupported scan-point pattern:", pattern
	
	return scan_points

def addNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name):
	if scanObject is None:
		raise "Input scanObject must not be None"
	
	nxLinkCreator = NXTomoEntryLinkCreator()
	
	default_placeholder_target = "entry1:NXentry/scan_identifier:SDS"
	
	# detector independent items
	nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/source:NXsource/current:SDS")
	
	nxLinkCreator.setInstrument_detector_distance_target(default_placeholder_target)
	nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/image_key:SDS")
	nxLinkCreator.setInstrument_detector_x_pixel_size_target(default_placeholder_target)
	nxLinkCreator.setInstrument_detector_y_pixel_size_target(default_placeholder_target)
	
	nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
	
	sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/tomoScanDevice:NXpositioner/" 
	sample_rotation_angle_target += tomography_theta_name + ":SDS"
	nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);
	
	nxLinkCreator.setSample_x_translation_target(default_placeholder_target)
	nxLinkCreator.setSample_y_translation_target(default_placeholder_target)
	nxLinkCreator.setSample_z_translation_target(default_placeholder_target)
	
	nxLinkCreator.setTitle_target("entry1:NXentry/title:SDS")
	
	# detector dependent items
	if tomography_detector_name == "pco1_sw_hdf":
		# external file
		instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
		instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
		instrument_detector_data_target += "data:SDS"
		nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
	elif tomography_detector_name == "pco1_sw_tif":
		# image filenames
		instrument_detector_data_target = "entry1:NXentry/instrument:NXinstrument/"
		instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
		instrument_detector_data_target += "image_data:SDS"
		nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
	else:
		print "Default target used for unsupported tomography detector in addNXTomoSubentry: " + tomography_detector_name
		instrument_detector_data_target = default_placeholder_target
		nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
	
	nxLinkCreator.afterPropertiesSet()
	
	dataWriter = createDataWriterFromFactory()
	subEntryWriter = NXSubEntryWriter(nxLinkCreator)
	dataWriter.addDataWriterExtender(subEntryWriter)
	scanObject.setDataWriter(dataWriter)

def reportJythonNamespaceMapping():
	jns = beamline_parameters.JythonNameSpaceMapping()
	objectOfInterestSTEP = {}
	objectOfInterestSTEP['tomography_theta'] = jns.tomography_theta
	objectOfInterestSTEP['tomography_shutter'] = jns.tomography_shutter
	objectOfInterestSTEP['tomography_translation'] = jns.tomography_translation
	objectOfInterestSTEP['tomography_detector'] = jns.tomography_detector
	objectOfInterestSTEP['tomography_sample_stage'] = jns.tomography_sample_stage
	
	objectOfInterestFLY = {}
	objectOfInterestFLY['tomography_theta'] = jns.tomography_theta
	objectOfInterestFLY['tomography_flyscan_theta'] = jns.tomography_flyscan_theta
	objectOfInterestFLY['tomography_shutter'] = jns.tomography_shutter
	objectOfInterestFLY['tomography_translation'] = jns.tomography_translation
	objectOfInterestFLY['tomography_flyscan_det'] = jns.tomography_flyscan_det
	objectOfInterestFLY['tomography_flyscan_flat_dark_det'] = jns.tomography_flyscan_flat_dark_det
	
	msg = "\n These mappings can be changed by editing a file named jythonNamespaceMapping, located in"
	msg += "\n /dls_sw/b16/software/gda/config/scripts/jythonNamespaceMapping (this can be done by beamline staff)."
	
	print "\n ****** STEP-SCAN PRIMARY SETTINGS ******"
	for idx, (key, val) in enumerate(objectOfInterestSTEP.iteritems()):
		name = "object undefined!"
		if val is not None:
			name = str(val.getName())
		print(" %i. %s = %s" %(idx+1, key, name))
		#print ' {0}. {1} = {2}'.format(idx, key, name)
	print "\n"
	
	print "****** FLY-SCAN PRIMARY SETTINGS ******"
	for idx, (key, val) in enumerate(objectOfInterestFLY.iteritems()):
		name = "object undefined!"
		if val is not None:
			name = str(val.getName())
		print(" %i. %s = %s" %(idx+1, key, name))
	# epilog
	print msg

def reportTomo():
	reportJythonNamespaceMapping()
	
class   tomoScan_positions(ScanPositionProvider):
	def __init__(self, start, stop, step, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat,
			 inBeamPosition, outOfBeamPosition, optimizeBeamInterval, points):
		self.start = start
		self.stop = stop
		self.step = step
		self.darkFieldInterval = darkFieldInterval
		self.imagesPerDark = imagesPerDark
		self.flatFieldInterval = flatFieldInterval
		self.imagesPerFlat = imagesPerFlat
		self.inBeamPosition = inBeamPosition
		self.outOfBeamPosition = outOfBeamPosition
		self.optimizeBeamInterval = optimizeBeamInterval
		self.points = points

	def get(self, index):
		return self.points[index]
	
	def size(self):
		return len(self.points)
	
	def __str__(self):
		return "Start: %f Stop: %f Step: %f Darks every:%d imagesPerDark:%d Flats every:%d imagesPerFlat:%d InBeamPosition:%f OutOfBeamPosition:%f Optimize every:%d numImages %d " % \
			(self.start, self.stop, self.step, self.darkFieldInterval, self.imagesPerDark, self.flatFieldInterval, self.imagesPerFlat, self.inBeamPosition, self.outOfBeamPosition, self.optimizeBeamInterval, self.size()) 
	def toString(self):
		return self.__str__()

image_key_dark = 2
image_key_flat = 1 # also known as bright
image_key_project = 0 # also known as sample

def tomoScan(description, inBeamPosition, outOfBeamPosition, exposureTime=1., start=0., stop=180., step=0.1, darkFieldInterval=0, flatFieldInterval=0,
			  imagesPerDark=10, imagesPerFlat=10, optimizeBeamInterval=0, pattern="default", addNXEntry=True, autoAnalyse=True, additionalScannables=[]):
	# set Pixel Rate for Edge only
	if(caget("BL13I-EA-DET-01:CAM:Model_RBV") == "PCO.Camera Edge"):
		pixel_rate_bup = caget("ME07M-EA-DET-01:CAM:PIX_RATE")
		caput("ME07M-EA-DET-01:CAM:PIX_RATE", "286000000 Hz")
	createSRS = LocalProperties.get("gda.nexus.createSRS")
	try:
		LocalProperties.set("gda.nexus.createSRS", "false")
		_tomoScan(description, inBeamPosition, outOfBeamPosition, exposureTime, start, stop, step, darkFieldInterval, flatFieldInterval,
				imagesPerDark, imagesPerFlat, optimizeBeamInterval, pattern, addNXEntry, autoAnalyse, additionalScannables)
	finally:
		LocalProperties.set("gda.nexus.createSRS", createSRS)
		if(caget("BL13I-EA-DET-01:CAM:Model_RBV") == "PCO.Camera Edge"):
			caput("ME07M-EA-DET-01:CAM:PIX_RATE", pixel_rate_bup)

"""
perform a simple tomography scan
"""
def _tomoScan(description, inBeamPosition, outOfBeamPosition, exposureTime=1., start=0., stop=180., step=0.1, darkFieldInterval=0, flatFieldInterval=0,
			  imagesPerDark=10, imagesPerFlat=10, optimizeBeamInterval=0, pattern="default", addNXEntry=True, autoAnalyse=True, additionalScannables=[]):
	"""
	*Desc:
	Function to run a step scan for collecting a tomogram. 
		Note(s): 
		1. the rotation and translation stages need to be specified in /dls_sw/b16/software/gda/config/scripts/jythonNamespaceMapping
		2. use the jythonNamespaceMapping command in GDA to inspect the current values specified in the above file
	*Arg(s):
	description (string): description of the scan or the sample (this is recorded in NeXus scan file)
	inBeamPosition (float): position of the translation stage to move sample into the beam to take a projection
	outOfBeamPosition (float): position of the translation stage to move sample out of the beam to take a flat-field image
	exposureTime (float): exposure time in seconds (default = 1.0)
	start (float): first rotation angle in deg (default = 0.0)
	stop (float): last rotation angle in deg (default = 180.0)
	step (float): rotation step size in deg (default = 0.1)
	darkFieldInterval (int): number of projections between each dark-field sub-sequence. 
		Note: at least 1 dark is ALWAYS taken both at the start and the end of this scan 
		(default = 0 - use this value if you DON'T want to take any darks between projections)
	flatFieldInterval (int): number of projections between each flat-field sub-sequence. 
		Note: at least 1 flat is ALWAYS taken both at the start and the end of this scan 
		(default = 0 - use this value if you DON'T want to take any flats between projections)
	imagesPerDark (int): number of images to be taken in each dark-field sub-sequence (default = 10)
	imagesPerFlat (int): number of images to be taken in each flat-field sub-sequence (default = 10)
	
	*Comment(s):
	General scan sequence: D, F, P,..., P, F, D
	where D stands for dark field, F - for flat field, and P - for projection.
	"""
	startTm = datetime.datetime.now();
	dataFormat = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
	try:
		darkFieldInterval = int(darkFieldInterval)
		flatFieldInterval = int(flatFieldInterval)
		optimizeBeamInterval = int(optimizeBeamInterval)
		
		jns = beamline_parameters.JythonNameSpaceMapping(InterfaceProvider.getJythonNamespace())
		tomography_theta = jns.tomography_theta
		if tomography_theta is None:
			raise "tomography_theta is not defined in Jython namespace"
		tomography_shutter = jns.tomography_shutter
		if tomography_shutter is None:
			raise "tomography_shutter is not defined in Jython namespace"
		tomography_translation = jns.tomography_translation
		if tomography_translation is None:
			raise "tomography_translation is not defined in Jython namespace"
		
		tomography_detector = jns.tomography_detector
		if tomography_detector is None:
			raise "tomography_detector is not defined in Jython namespace"
		
		tomography_time = jns.tomography_time
		if tomography_time is None:
			raise "tomography_time is not defined in Jython namespace"
		
		tomography_sample_stage = jns.tomography_sample_stage
		if tomography_sample_stage is None:
			raise "tomography_sample_stage is not defined in Jython namespace"
		
		index = SimpleScannable()
		index.setCurrentPosition(0.0)
		index.setInputNames(["imageNumber"])
		index.setName("imageNumber")
		index.configure()
		
		image_key = SimpleScannable()
		image_key.setCurrentPosition(0.0)
		image_key.setInputNames(["image_key"])
		image_key.setName("image_key")
		image_key.configure()
		
		tomoScanDevice = make_tomoScanDevice(tomography_theta, tomography_shutter,
											 tomography_translation, image_key, index)
		
		#generate list of positions
		numberSteps = ScannableUtils.getNumberSteps(tomography_theta, start, stop, step)
		theta_points = []
		theta_points.append(start)
		previousPoint = start
		for i in range(numberSteps):
			nextPoint = ScannableUtils.calculateNextPoint(previousPoint, step);
			theta_points.append(nextPoint)
			previousPoint = nextPoint
		
		#generateScanPoints
		scan_points = generateScanPoints(inBeamPosition, outOfBeamPosition, theta_points, darkFieldInterval, flatFieldInterval,
			  imagesPerDark, imagesPerFlat, optimizeBeamInterval, pattern=pattern)
		
		#return None
		positionProvider = tomoScan_positions(start, stop, step, darkFieldInterval, imagesPerDark, flatFieldInterval, imagesPerFlat, \
											   inBeamPosition, outOfBeamPosition, optimizeBeamInterval, scan_points) 
		scan_args = [tomoScanDevice, positionProvider, tomography_time, tomography_detector, exposureTime, tomography_sample_stage]
		#scan_args.append(RotationAxisScannable("approxCOR", tomoRotationAxis))
		for scannable in additionalScannables:
			scan_args.append(scannable)
		#setting the description provided as the title
		if not description == None: 
			setTitle(description)
		else :
			setTitle("undefined")
		
		dataFormat = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
		if not dataFormat == "NexusDataWriter":
			handle_messages.simpleLog("Data format inconsistent. Setting 'gda.data.scan.datawriter.dataFormat' to 'NexusDataWriter'")
			LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")
		scanObject = createConcurrentScan(scan_args)
		if addNXEntry:
			addNXTomoSubentry(scanObject, tomography_detector.name, tomography_theta.name)
		scanObject.runScan()
		if autoAnalyse:
			lsdp=jns.lastScanDataPoint()
			OSCommandRunner.runNoWait(["/dls_sw/apps/tomopy/tomopy/bin/gda/tomo_at_scan_end_kz", lsdp.currentFilename], OSCommandRunner.LOGOPTION.ALWAYS, None)
		return scanObject;
	except InterruptedException:
		exceptionType, exception, traceback = sys.exc_info()
		handle_messages.log(None, "User interrupted the scan", exceptionType, exception, traceback, False)
		raise InterruptedException("User interrupted the scan")
	except:
		exceptionType, exception, traceback = sys.exc_info()
		handle_messages.log(None, "Error during tomography scan", exceptionType, exception, traceback, False)
		raise Exception("Error during tomography scan", exception)
	finally:
		handle_messages.simpleLog("Data Format reset to the original setting: " + dataFormat)
		LocalProperties.set("gda.data.scan.datawriter.dataFormat", dataFormat)
		endTm = datetime.datetime.now()
		elapsedTm = endTm - startTm
		jns=beamline_parameters.JythonNameSpaceMapping()
		print("This scan's data can be found in Nexus scan file %s." %(jns.lastScanDataPoint().currentFilename))
		print("Elapsed time (in the format [D day[s], ][H]H:MM:SS[.UUUUUU]): %s" %(str(elapsedTm)))

tomoScan.__doc__ = _tomoScan.__doc__

from java.lang import Runnable
class PreScanRunnable(Runnable):
	def __init__(self, msg, percentage, shutter, shutterPosition, xMotor, xMotorPosition, image_key, image_key_value, thetaMotor, thetaMotorPosition):
		self.msg = msg
		self.percentage = percentage
		self.shutter=shutter
		self.shutterPosition = shutterPosition
		self.xMotor = xMotor
		self.xMotorPosition =xMotorPosition
		self.image_key =image_key
		self.image_key_value =image_key_value
		self.thetaMotor = thetaMotor
		self.thetaMotorPosition =thetaMotorPosition
		
	def run(self):
		updateProgress(self.percentage, self.msg)
		updateProgress(self.percentage, "Move x")
		self.xMotor.moveTo(self.xMotorPosition)
		updateProgress(self.percentage, "Move theta")
		self.thetaMotor.moveTo(self.thetaMotorPosition)
		updateProgress(self.percentage, "Move shutter")
		self.shutter.moveTo(self.shutterPosition)
		self.image_key.moveTo(self.image_key_value)


from gda.commandqueue import JythonScriptProgressProvider
def updateProgress( percent, msg):
	JythonScriptProgressProvider.sendProgress( percent, msg)
	print "percentage %d %s" % (percent, msg)
	
def addFlyScanNXTomoSubentry(scanObject, tomography_detector_name, tomography_theta_name, externalhdf=True):
	if scanObject is None:
		raise "Input scanObject must not be None"
	
	nxLinkCreator = NXTomoEntryLinkCreator()
	
	# detector independent items
	#nxLinkCreator.setControl_data_target("entry1:NXentry/instrument:NXinstrument/ionc_i:NXpositioner/ionc_i:SDS")
	nxLinkCreator.setInstrument_detector_image_key_target("entry1:NXentry/instrument:NXinstrument/image_key:NXpositioner/image_key:SDS")
	nxLinkCreator.setInstrument_source_target("entry1:NXentry/instrument:NXinstrument/source:NXsource")
	
	#sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/zebraSM1:NXpositioner/"
	#sample_rotation_angle_target += tomography_theta_name + ":SDS"
	#nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);

	sample_rotation_angle_target = "entry1:NXentry/instrument:NXinstrument/" + tomography_theta_name + ":NXpositioner/"
	sample_rotation_angle_target += tomography_theta_name + ":NXdata"
	nxLinkCreator.setSample_rotation_angle_target(sample_rotation_angle_target);

	#nxLinkCreator.setSample_x_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplex:SDS")
	#nxLinkCreator.setSample_y_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_sampley:SDS")
	#nxLinkCreator.setSample_z_translation_target("entry1:NXentry/before_scan:NXcollection/sample_stage:NXcollection/ss1_samplez:SDS")
	
	nxLinkCreator.setTitle_target("entry1:NXentry/title:SDS")
	
	# detector dependent items
	if externalhdf:
		# external file
		instrument_detector_data_target = "!entry1:NXentry/instrument:NXinstrument/"
		instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
		instrument_detector_data_target += "data:SDS"
		nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
	else:
		# image filenames
		instrument_detector_data_target = "entry1:NXentry/instrument:NXinstrument/"
		instrument_detector_data_target += tomography_detector_name + ":NXdetector/"
		instrument_detector_data_target += "image_data:SDS"
		nxLinkCreator.setInstrument_detector_data_target(instrument_detector_data_target)
	
	nxLinkCreator.afterPropertiesSet()
	
	dataWriter = createDataWriterFromFactory()
	subEntryWriter = NXSubEntryWriter(nxLinkCreator)
	dataWriter.addDataWriterExtender(subEntryWriter)
	scanObject.setDataWriter(dataWriter)


"""
perform a continuous tomography scan
"""
def _tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
			  imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False):
	"""
	*Desc:
	Function to run a fly scan for collecting a tomogram
	*Arg(s):
	inBeamPosition (float): position of the translation drive to move sample into the beam to take a projection
	outOfBeamPosition (float): position of the translation drive to move sample out of the beam to take a flat field image
	exposureTime (float): exposure time in seconds (default = 1)
	start (float): first rotation angle (default = 0.0)
	stop (float): last rotation angle (default = 180.0)
	step (float): rotation step size (default = 0.1)
	darkFieldInterval (int): number of projections between each dark field. 
		Note: a dark is always taken at the start and end of a tomogram (default = 0)
	flatFieldInterval (int): number of projections between each flat field. 
		Note: a flat is always taken at the start and end of a tomogram (default = 0)
	imagesPerDark (int): number of images to be taken for each dark (default = 20)
	imagesPerFlat (int): number of images to be taken for each flat (default = 20)
	min_i (float): minimum value of ion chamber current required to take an image (default = -1. A negative value means that the value is not checked)

	"""
	startTm = datetime.datetime.now();
	updateProgress(0, "Starting scan")
	dataFormat = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
	if not dataFormat == "NexusDataWriter":
		handle_messages.simpleLog("Data format inconsistent. Setting 'gda.data.scan.datawriter.dataFormat' to 'NexusDataWriter'")
		LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")
	jns=beamline_parameters.JythonNameSpaceMapping()
	tomography_flyscan_flat_dark_det=jns.tomography_flyscan_flat_dark_det
	savename=tomography_flyscan_flat_dark_det.name
	try:
		#tomodet=jns.tomodet
		#if tomodet is None:
		#	raise "tomodet is not defined in Jython namespace"

		tomography_theta=jns.tomography_theta
		if tomography_theta is None:
			raise "tomography_theta is not defined in Jython namespace"

		tomography_flyscan_theta=jns.tomography_flyscan_theta
		if tomography_flyscan_theta is None:
			raise "tomography_flyscan_theta is not defined in Jython namespace"

		tomography_flyscan_det=jns.tomography_flyscan_det
		if tomography_flyscan_det is None:
			raise "tomography_flyscan_det is not defined in Jython namespace"
		
		tomography_translation=jns.tomography_translation
		if tomography_translation is None:
			raise "tomography_translation is not defined in Jython namespace"
		

		tomography_shutter=jns.tomography_shutter
		if tomography_shutter is None:
			raise "tomography_shutter is not defined in Jython namespace"
		
		#meta_add = jns.meta_add
		#if meta_add is None:
		#	raise "meta_add is not defined in Jython namespace"

		#camera_stage = jns.cs1
		#if camera_stage is None:
		#	raise "camera_stage is not defined in Jython namespace"

		#sample_stage = jns.sample_stage
		##if sample_stage is None:
		#	raise "sample_stage is not defined in Jython namespace"		

		#ionc_i = jns.ionc_i
		#if ionc_i is None:
		#	raise "ionc_i is not defined in Jython namespace"
		#ionc_i_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(ionc_i)


		#meta_add( camera_stage)
		#meta_add( sample_stage)
		

		index=SimpleScannable()
		index.setCurrentPosition(0.0)
		index.setName(tomography_flyscan_theta.name)
		index.inputNames = tomography_flyscan_theta.inputNames
		index.extraNames = tomography_flyscan_theta.extraNames
		index.configure()

#		index_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(index)


		image_key=SimpleScannable()
		image_key.setCurrentPosition(0.0)
		image_key.setInputNames(["image_key"])
		image_key.setName("image_key")
		image_key.configure()
		image_key_cont=tomography_flyscan_theta.getContinuousMoveController().createScannable(image_key)


#		ss=SimpleScannable()
#		ss.name = tomography_flyscan_theta.name
#		ss.currentPosition=0.
#		ss.inputNames = tomography_flyscan_theta.inputNames
#		ss.extraNames = tomography_flyscan_theta.extraNames
#		ss.configure()

		ss1=SimpleScannable()
		ss1.name = tomography_flyscan_theta.getContinuousMoveController().name
		ss1.currentPosition=0.
		ss1.inputNames = tomography_flyscan_theta.getContinuousMoveController().inputNames
		ss1.extraNames = tomography_flyscan_theta.getContinuousMoveController().extraNames
		ss1.configure()
		
		

		
		tomography_flyscan_flat_dark_det.name = tomography_flyscan_det.name
		
#		scanBackward=ConstantVelocityScanLine([tomography_flyscan_theta, stop, start, step, index_cont, image_key_cont, ionc_i_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
#		scanObject3=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step,ix, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
		#tomodet.stop()
		
#		multiScanObj = MultiScan([darkFlatScan, scanObject, scanObject2,scanObject3])
		multiScanItems = []

		if imagesPerDark > 0:
			darkScan=ConcurrentScan([index, 0, imagesPerDark-1, 1, image_key, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
			multiScanItems.append(MultiScanItem(darkScan, PreScanRunnable("Preparing for darks", 0, tomography_shutter, "Close", tomography_translation, inBeamPosition, image_key, image_key_dark, tomography_theta, start)))
		if imagesPerFlat > 0:
			flatScan=ConcurrentScan([index, 0, imagesPerFlat-1, 1, image_key, ss1, jns.tomography_flyscan_flat_dark_det, exposureTime])
			multiScanItems.append(MultiScanItem(flatScan, PreScanRunnable("Preparing for flats",10, tomography_shutter, "Open", tomography_translation, outOfBeamPosition, image_key, image_key_flat, tomography_theta, start)))
		
		scanForward=ConstantVelocityScanLine([tomography_flyscan_theta, start, stop, step,image_key_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
#		scanBackward=ConstantVelocityScanLine([tomography_flyscan_theta, stop, start, step,image_key_cont, ionc_i_cont, tomography_flyscan_theta.getContinuousMoveController(), tomography_flyscan_det, exposureTime])
		multiScanItems.append(MultiScanItem(scanForward, PreScanRunnable("Preparing for projections",20, tomography_shutter, "Open",tomography_translation, inBeamPosition, image_key, image_key_project, tomography_theta, start)))
#		multiScanItems.append(MultiScanItem(scanBackward, PreScanRunnable("Preparing for projections backwards",60, tomography_shutter, "Open",tomography_translation, inBeamPosition, image_key, image_key_project)))
		multiScanObj = MultiScanRunner(multiScanItems)
		#must pass fist scan to be run
		addFlyScanNXTomoSubentry(multiScanItems[0].scan, tomography_flyscan_det.name, tomography_flyscan_theta.name)
		multiScanObj.runScan()
		tomography_shutter.moveTo("Close")
			
#		time.sleep(2)
		updateProgress(100, "Scan complete")
		return multiScanObj;
	except :
		exceptionType, exception, traceback = sys.exc_info()
		#turn camera back on
		tomography_flyscan_flat_dark_det.name = savename
		if setupForAlignment:
			#tomodet.setupForAlignment()
			pass
		handle_messages.log(None, "Error in tomoFlyScan", exceptionType, exception, traceback, True)
	finally:
		handle_messages.simpleLog("Data Format reset to the original setting: " + dataFormat)
		LocalProperties.set("gda.data.scan.datawriter.dataFormat", dataFormat)
		endTm = datetime.datetime.now()
		elapsedTm = endTm - startTm
		jns=beamline_parameters.JythonNameSpaceMapping()
		print("This scan's data can be found in Nexus scan file %s." %(jns.lastScanDataPoint().currentFilename))
		print("Elapsed time (in the format [D day[s], ][H]H:MM:SS[.UUUUUU]): %s" %(str(elapsedTm)))

def tomoFlyScan(description, inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0, flatFieldInterval=0,
			  imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False):
	title_bup = getTitle()
	if (not description is None) and len(description)>0:
		setTitle(description)
	else:
		setTitle("undefined")
	# set Pixel Rate for Edge only
	if(caget("BL13I-EA-DET-01:CAM:Model_RBV") == "PCO.Camera Edge"):
		pixel_rate_bup = caget("ME07M-EA-DET-01:CAM:PIX_RATE")
		caput("ME07M-EA-DET-01:CAM:PIX_RATE", "286000000 Hz")
		#pcoEdge_readout=0.011
		#from gda.factory import Finder
		#finder = Finder.getInstance()
		#flyScanDetector=finder.find("flyScanDetector")
		#flyScanDetector.readOutTime=pcoEdge_readout
	createSRS = LocalProperties.get("gda.nexus.createSRS")
	try:
		LocalProperties.set("gda.nexus.createSRS", "false")
		_tomoFlyScan(inBeamPosition=inBeamPosition, outOfBeamPosition=outOfBeamPosition, exposureTime=exposureTime, start=start, stop=stop, step=step, darkFieldInterval=darkFieldInterval, flatFieldInterval=flatFieldInterval,
				imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, min_i=min_i, setupForAlignment=setupForAlignment)
	finally:
		LocalProperties.set("gda.nexus.createSRS", createSRS)
		setTitle(title_bup)
		if(caget("BL13I-EA-DET-01:CAM:Model_RBV") == "PCO.Camera Edge"):
			caput("ME07M-EA-DET-01:CAM:PIX_RATE", pixel_rate_bup)
		
tomoFlyScan.__doc__ = _tomoFlyScan.__doc__
	

def __test1_tomoScan():
	jns = beamline_parameters.JythonNameSpaceMapping()	
	sc = tomoScan(step=5, darkFieldInterval=5, flatFieldInterval=5,
			 inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
	print `jns`
	lsdp = jns.lastScanDataPoint()
	positions = lsdp.getPositionsAsDoubles()
	if positions[0] != 180. or positions[4] != 54.:
		print "Error - points are not correct :" + `positions`
	return sc

def __test2_tomoScan():
	jns = beamline_parameters.JythonNameSpaceMapping()	
	sc = tomoScan(step=5, darkFieldInterval=5, flatFieldInterval=0,
			 inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
	lsdp = jns.lastScanDataPoint()
	positions = lsdp.getPositionsAsDoubles()
	if positions[0] != 180. or positions[4] != 47.:
		print "Error - points are not correct :" + `positions`
	return sc

def __test3_tomoScan():
	jns = beamline_parameters.JythonNameSpaceMapping()	
	sc = tomoScan(step=5, darkFieldInterval=0, flatFieldInterval=5,
			 inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
	lsdp = jns.lastScanDataPoint()
	positions = lsdp.getPositionsAsDoubles()
	if positions[0] != 180. or positions[4] != 47.:
		print "Error - points are not correct :" + `positions`
	return sc

def __test4_tomoScan():
	jns = beamline_parameters.JythonNameSpaceMapping()	
	sc = tomoScan(step=5, darkFieldInterval=0, flatFieldInterval=0,
			 inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
	lsdp = jns.lastScanDataPoint()
	positions = lsdp.getPositionsAsDoubles()
	if positions[0] != 180. or positions[4] != 40.:
		print "Error - points are not correct :" + `positions`
	return sc

def __test5_tomoScan():
	"""
	Test optimizeBeamInterval=10
	"""
	jns = beamline_parameters.JythonNameSpaceMapping()	
	sc = tomoScan(step=5, darkFieldInterval=0, flatFieldInterval=0,
			 inBeamPosition=0., outOfBeamPosition=10., exposureTime=1., optimizeBeamInterval=10)
	lsdp = jns.lastScanDataPoint()
	positions = lsdp.getPositionsAsDoubles()
	if positions[0] != 180. or positions[4] != 43.:
		print "Error - points are not correct :" + `positions`
	return sc

def test_all():
	__test1_tomoScan()
	__test2_tomoScan()
	__test3_tomoScan()
	__test4_tomoScan()

def standardtomoScan():
	jns = beamline_parameters.JythonNameSpaceMapping()	
	sc = tomoScan(step=1, darkFieldInterval=0, flatFieldInterval=20,
			 inBeamPosition=0., outOfBeamPosition=10., exposureTime=1.)
	lsdp = jns.lastScanDataPoint()
	positions = lsdp.getPositionsAsDoubles()
	if positions[0] != 180. or positions[4] != 40.:
		print "Error - points are not correct :" + `positions`
	return sc

class RotationAxisScannable(ScannableBase):
	def __init__(self, name, value):
		self.name = name
		self.value = value
#		self.count = 0
		pass
	
	def isBusy(self):
		return False
	
	def rawAsynchronousMoveTo(self, new_position):
		return
	
	def rawGetPosition(self):
#		if self.count > 0:
#			return None
#		self.count = 1
		return self.value
