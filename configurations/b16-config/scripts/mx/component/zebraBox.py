import os
import time

from framework import PilatusScripts

from framework import cbf_template

from java.lang import IllegalArgumentException
from time import sleep

from gda.configuration.properties import LocalProperties
from gda.configuration.properties.LocalProperties import isDummyModeEnabled # @UnusedImport

from gda.device import Stoppable
from gda.device.zebra.controller import Zebra
from gda.device.zebra.controller.impl import ZebraImpl

from gda.epics import LazyPVFactory
from gda.factory import Finder, Findable

from gda.epics import CAClient 


"""
The zebraBox module contains the classes that set the required input values
to the java object that communicates with a zebra box during a scan.

The basis of this code is borrowed from i24

ZebraPin is wired up to BL???-EA-ZEBRA-??
Its position position encoder triggers the shutter
and detector for x,y,z translations of the stage, and rotation angle omega on
the pin gonio.

ZebraTray is wired up to BL241-EA-ZEBRA-02
Its position position encoder triggers the shutter
and detector for x,y translations of the stage on the tray gonio.

Utility methods are implemented to set up the detector so that the set up of
the Zebra box during a scan can be tested in isolation.
"""

DEFAULT_OMEGA_SPEED = 5
DEFAULT_IMAGE_RANGE = 0.5
DEFAULT_NUM_IMAGES = 100
DEFAULT_OMEGA_START = 0
DEFAULT_TIME_TO_VELOCITY = 5
DEFAULT_EXPOSURE_T = 0.01
DEFAULT_OSC_WIDTH = 0.5
DEFAULT_START_DELTA = 1.0 # degrees, for wind-back on scan axis

CBF_GONIO_ROTATION_AXIS = ". 1 0 0 . . ." # I19-1 entry for cbf header template

def formatImageNumber(number):
	return str("%05d" % (number))

###############################################################################

class ZebraManager(Stoppable,Findable):


	def __init__(self):
		self.my_name = "zebra_manager"
		self.mode = ZebraBox.MODE_PIN


	def getZebraMode(self):
		return self.mode


	def setZebraMode(self, mode):
		# Overridden for I19-1
		if ZebraBox.MODE_PIN != mode:
			raise IllegalArgumentException
		return self.mode


	def getZebra(self):
		# Overridden for I19-1
		return zebraP


	def closeShutter(self, override_auto=True):
		if override_auto:
			self.setShutterModeManual()
		zebraP._getZebraController().setSoftInput(ZebraBox.IN2,ZebraBox.CLOSE_SHUTTER)
		sleep(1)


	def getName(self):
		return self.my_name


	def getShutterState(self):
		state = "UNKOWN"
		if zebraP._getZebraController().isSoftInputSet(ZebraBox.IN2):
			state = ZebraBox.OPEN_SHUTTER_STATE
		else:
			state = ZebraBox.CLOSE_SHUTTER_STATE
		return state


	def isShutterModeAuto(self):
		return zebraP._getZebraController().isSoftInputSet(ZebraBox.IN1)


	def isShutterModeManual(self):
		return not zebraP._getZebraController().isSoftInputSet(ZebraBox.IN1)


	def isShutterOpen(self):
		return zebraP._getZebraController().isSoftInputSet(ZebraBox.IN2)
		# FIXME should read TTL output BL19I-EA-ZEBRA-02:OUT1_TTL:STA


	def openShutter(self):
		zebraP._getZebraController().setSoftInput(ZebraBox.IN2,ZebraBox.OPEN_SHUTTER)


	def reset(self):
		self.getZebra().reset()


	def setName(self, name):
		self.my_name = name


	def setShutterModeAuto(self):
		zebraP._getZebraController().setSoftInput(ZebraBox.IN1,ZebraBox.ENABLE_AUTO)


	def setShutterModeManual(self):
		zebraP._getZebraController().setSoftInput(ZebraBox.IN1,ZebraBox.ENABLE_MANUAL)


	def stop(self):
		self.reset()
		self.closeShutter()


class ZebraBox:

	MODE_UNKNOWN = -1
	MODE_PIN = 0
	MODE_PIN_KAPPA = 1
	MODE_TRAY = 2

	OPEN_SHUTTER = 1
	CLOSE_SHUTTER = 0
	OPEN_SHUTTER_STATE = "Open"
	CLOSE_SHUTTER_STATE = "Close"
	RESET_SHUTTER_STATE = "Reset"

	ENABLE_AUTO = 1
	ENABLE_MANUAL = 0
	IN1 = 1
	IN2 = 2

	def __init__(self):
		self.mode = ZebraBox.MODE_UNKNOWN
		self.zebra = None
		self.detector = BCMFinder.getDetector() # FIXME:
		
		self.resetOscillationParameters()
		
		self.fluo_gate_width = 1
		self.omega_start = DEFAULT_OMEGA_START
		self.omega_speed = DEFAULT_OMEGA_SPEED
		self.image_range = DEFAULT_IMAGE_RANGE
		self.num_images = DEFAULT_NUM_IMAGES
		self.time_to_velocity = DEFAULT_TIME_TO_VELOCITY
		self.exposure_t = DEFAULT_EXPOSURE_T
		self.osc_width = DEFAULT_OSC_WIDTH


	def configurePVs(self,prefix):
		self.PCEnc = LazyPVFactory.newIntegerPV(prefix+ZebraImpl.PCEnc)
		self.PCDir = LazyPVFactory.newIntegerPV(prefix+ZebraImpl.PCDir)
		self.PCArmSource = LazyPVFactory.newIntegerPV(prefix+ZebraImpl.PCArmSource)
		self.PCGateSource = LazyPVFactory.newIntegerPV(prefix+ZebraImpl.PCGateSource)
		self.PCGateStart = LazyPVFactory.newDoublePV(prefix+ZebraImpl.PCGateStart)
		self.PCGateWidth = LazyPVFactory.newDoublePV(prefix+ZebraImpl.PCGateWidth)
		self.PCGateNumberOfGates = LazyPVFactory.newIntegerPV(prefix+ZebraImpl.PCGateNumberOfGates)
		self.setOutTTL4 = LazyPVFactory.newIntegerPV(prefix+"OUT4_TTL")
		self.setOutTTL3 = LazyPVFactory.newIntegerPV(prefix+"OUT3_TTL")
		self.setOutTTL2 = LazyPVFactory.newIntegerPV(prefix+"OUT2_TTL")
		self.PCArm = LazyPVFactory.newIntegerPV(prefix+ZebraImpl.PCArm)
		self.sysResetProc = LazyPVFactory.newIntegerPV(prefix+ZebraImpl.sysResetProc)
		self.PCDisArm = LazyPVFactory.newIntegerPV(prefix+ZebraImpl.PCDisArm)
		# self.PCPulseMax = LazyPVFactory.newIntegerPV(prefix+ZebraImpl.PCPulseMax)
		self.encCopy1 = LazyPVFactory.newIntegerPV(self.prefix+"M1:SETPOS.PROC")


	# Should only be called after homing an axis
	def encCopyMotorPosToZebra(self,pos=1):
		# assert 1 <= pos <= 4
		if pos==1:
			self.encCopy = self.encCopy1
		else:
			pvSuffix = "M%d:SETPOS.PROC" % (pos)
			self.encCopy = LazyPVFactory.newIntegerPV(self.prefix+pvSuffix)
		self.encCopy.putWait(1)


	"""
	Abstract. Delegate to sub-class
	Set the Zebra box up for a grid scan.
	"""
	def setup_zebraGridScan(self,startPoint,endPoint):
		pass


	def setShutterToManual(self):
		# self.zebra.setOutTTL(2, 30)
		# self.zebra.setOutTTL(4, 36)
		self.setOutTTL2.putWait(30,1.0)
		self.setOutTTL4.putWait(36,1.0)


	"""
	Abstract. Delegate to sub-class
	Set the Zebra box up for fluorescence scan.
	"""
	def setup_zebra(self,num_images,image_range,omega_start):
		pass


	def _getZebraController(self):
		return self.zebra


	def arm_zebra(self):
		print "Arming Zebra "+self.prefix
		# self.camera.setAutoMode()
		# sleep(0.5)
		# self.sysResetProc.putWait(1,1.0)
		self.PCArm.putWait(1, 1.0)
		sleep(2.0)
		print "Armed "+self.prefix


	def disarm_zebra(self):
		print "Disarming Zebra "+self.prefix
		self.PCDisArm.putWait(1,5.0)
		print "Disarmed "+self.prefix


	def arm_detector(self):
		print "arming detector..."
		self.detector.start("", 0)


	def setOscillationParameters(self,oscRange,imageNum,exposureTimePerImage,phiDelta):
		self.oscRange = oscRange
		self.imageNum = imageNum
		self.exposureTimePerImage = exposureTimePerImage
		self.phiDelta = phiDelta
		self.phiInc = 0


	def resetOscillationParameters(self):
		self.setOscillationParameters(1.0,1,1.0,0.0)


	def setPhiInc(self):
		self.phiInc = 0


	def setIsPilatusDataCollection(self,isPilatus):
		self.isPilatus = isPilatus


	def isPilatusDataCollection(self):
		return self.isPilatus


	"""
	Abstract. Delegate to sub-class
	Set up the detector for grid scan
	"""
	def setup_detectorGrid(self,omega_start,boxWidthY,numBoxes,inc):
		pass


	def setup_detector(self,omega_start,num_images,osc,end_angle):
		pass


	def calculateEndAngle(self,omega_start,image_num, osc_range):
		print "end angle is omega start %2.4f + image_num %2.4f * oscRange %2.4f"%(omega_start,image_num,osc_range)
		end = omega_start + (image_num * osc_range)
		return end


	def reset(self):
		self.disarm_zebra()
		self.resetOscillationParameters()
		self.zebra.PCDir = int(Zebra.PC_DIR_POSITIVE)


	def showParams(self):
		print "omega start %2.4f" % (self.omega_start)
		if self.exposureTimePerImage > 0.0:
			print "omega_speed %2.4f" % (self.oscRange/self.exposureTimePerImage)
		print "image_range %2.4f" % (self.image_range)
		print "num_images %d" % (self.num_images)

###############################################################################

class ZebraPin(ZebraBox):

	def __init__(self):
		self.max_speed = 9999 # theoretical maximum speed of all axes
		self.zebra = Finder.find("zebra")
		self.detector = BCMFinder.getDetector() # FIXME:
		self.imageNum = 0
		self.exposureTimePerImage = 0
		self.oscRange = 0
		#These values are to set the shutter - ideally it should be done
		#explicitly throw through the i24MXShutter object
		self.ENABLE_MANUAL = 0
		self.IN1 = 1
		self.OPEN_SHUTTER = 1
		self.CLOSE_SHUTTER = 0
		self.IN2 = 2
		
		self.omega_encoder=int(Zebra.PC_ENC_ENC1)
		self.phi_encoder=int(Zebra.PC_ENC_ENC2)
		self.test_path="/ramdisk/2015/cm12174-3"
		
		self.caclient = CAClient()
		self.num_images_pv="BL19I-EA-PILAT-02:cam1:NumImages"


	"""
	Set the Zebra box up for normal data collection
	"""
	def setup_zebra(self, num_images, image_range, scan_encoder, start_angle):#, dc, scan):
		print "setting up zebra..."
		
		self.disarm_zebra()
		# self.camera.close()
		
		# Setup
		# Capture - ENC1&2
		self.zebra.PCCaptureBitField = 3
		self.zebra.PCEnc = scan_encoder
		time.sleep(0.02)
		# Posn Dir - Positive
		if image_range < 0:
			self.zebra.PCDir = int(Zebra.PC_DIR_NEGATIVE)
		else:
			self.zebra.PCDir = int(Zebra.PC_DIR_POSITIVE)
		
		# Arm
		# Trig Source - Soft
		self.zebra.PCArmSource = int(Zebra.PC_ARM_SOURCE_SOFT)
		
		# Gate
		# Trig Source - Position
		self.zebra.PCGateSource = int(Zebra.PC_GATE_SOURCE_POSITION)
		# Gate Start
		self.zebra.PCGateStart = start_angle
		# Gate Width
		self.zebra.PCGateWidth = abs(num_images * image_range)
		# Num Gates
		self.zebra.PCGateNumberOfGates = 1
		
		# Pulse
		# Max Pulses
		self.zebra.PCPulseMax = 0
		self.zebra.PCPulseWidth = abs(image_range)/100.0
		self.zebra.PCPulseStep = abs(image_range)
		
		# connect PC_GATE to OUT3 TTL (to detector)
		#self.zebra.setOutTTL(3, 30)
		# PC_GATE via AND/ORs to OUT is fixed configuration in I19 boxes


	def getZebraBox(self):
		return self.zebra


	def arm_zebra(self):
		print "arming Zebra..."
		#DETECTOR IS DUMMY AT THE MOMENT
		#if not isDummyModeEnabled():
		#self.camera.setAutoMode()
		self.zebra.pcArm()


	def disarm_zebra(self):
		print "disarm zebra"
		self.zebra.pcDisarm()


	def arm_detector(self):
		print "arming detector..."
		self.detector.start(None, 0)
		print "armed detector..."


	def setOscillationParameters(self,oscRange,imageNum,exposureTimePerImage):
		self.oscRange = oscRange
		self.imageNum = imageNum
		self.exposureTimePerImage = exposureTimePerImage


	def setup_detectorGrid(self,omega_start,boxWidthY,numBoxes,inc):
		raise Exception("Not supported on I19-1")


# 	def setup_detector(self, pilatus_template, extendedRequest, oscillation):
# 
# 		print "setting up detector..."
# 		
# 		output_path = extendedRequest.request.getFileinfo().getDirectory()
# 		output_filename = extendedRequest.request.getFileinfo().getPrefix()
# 		
# 		file_path = PilatusScripts.getDetectorWriteFilepath(output_path)
# 		print "file path = %s" % file_path
# 		self.detector.filepath = file_path
# 		
# 		filename = output_filename#"%s_%d_" % ("test", 1)
# 		print "file name = %s" % filename
# 		self.detector.fileprefix = filename
# 		
# 		run_number = extendedRequest.getRunNumber()
# 		print "run number = %d" % run_number
# 		self.detector.filenumber = run_number # auto increments
# 		
# 		num_images = extendedRequest.getTotalNumberOfImages()
# 		print "number of images = %d" % num_images
# 		self.detector.numberOfImages = num_images
# 		
# 		start_number = oscillation.getStart_image_number()
# 		print "first image number = %d" % start_number
# 
# 		# one signal to start acquisition of all images (not one signal per image)
# 		self.detector.imageMode = "Single"
# 		self.detector.mode = "Ext. Trigger"
# 		self.detector.gapFill = -1
# 		self.detector.fileformat = "%s%s_%02d_" + formatImageNumber(start_number) + ".cbf"
# 		
# 		pilatus_template = self.setup_template(pilatus_template, extendedRequest, oscillation)
# 		
# 		if cbf_template.should_write_template():
# 			# startImageNumber = oscillation.getStart_image_number()
# 			semirandom_filename = "%03d.cif" % int(time.time() * 1000 % 1000)
# 			template_location = LocalProperties.get("gda.cbf.template")
# 			pilatus_template.cbfTemplateFile = os.path.join(template_location, semirandom_filename)
# 			print "writing CBF template to %s" % pilatus_template.cbfTemplateFile
# 			cbf_template.write_template(pilatus_template.cbfTemplateFile, {
# 				'detector_id': self.detector.id,
# 				'detector_name': self.detector.shortName,
# 				'beam_x': pilatus_template.beamX,
# 				'beam_y': pilatus_template.beamY,
# 				'pixel_size_x': self.detector.pixelSize[0],
# 				'pixel_size_y': self.detector.pixelSize[1],
# 				'distance': pilatus_template.sampleDetectorDistance,
# 				"gonio_rotation_vector": [1, 0, 0]
# 			})
# 		else:
# 			print "not writing CBF template"
# 			pilatus_template.cbfTemplateFile = "0" # need to tell it 0 to unset
# 		
# 		# "MX Settings" that aren't currently set:
# 		#    Energy range (low & high)
# 		#    Detector 2theta
# 		#    Oscillation axis
# 		#    No. oscillations
# 		
# 		self.detector.initialiseDataSet(pilatus_template)


# 	def setup_position_compare(self, run_data, time_to_velocity, shutter_delay):
# 		self.zebra.setPCCaptureBitField(3)
# 		self.zebra.setPCTimeUnit(Zebra.PC_TIMEUNIT_SEC)
# 		self.zebra.setPCArmSource(int(Zebra.PC_ARM_SOURCE_SOFT))
# 		
# 		if run_data.isRotationOmega():
# 			self.zebra.setPCEnc(Zebra.PC_ENC_ENC2)
# 		else:
# 			self.zebra.setPCEnc(Zebra.PC_ENC_ENC1)
# 		
# 		# Gate Start
# 		gate = compute_gate(run_data, time_to_velocity, shutter_delay)
# 		self.zebra.setPCDir(gate.direction)
# 		self.zebra.setPCGateSource(Zebra.PC_GATE_SOURCE_POSITION)
# 		self.zebra.setPCGateStart(gate.shutter_open)
# 		self.zebra.setPCGateWidth(gate.shutter_interval + gate.scan_width)
# 		self.zebra.setPCGateStep(0.0)
# 		self.zebra.setPCGateNumberOfGates(1)
# 
# 		# Pulse
# 		self.zebra.setPCPulseSource(Zebra.PC_PULSE_SOURCE_TIME)
# 		self.zebra.setPCPulseStart(gate.shutter_delay)
# 		self.zebra.setPCPulseWidth(gate.scan_exposure)
# 		self.zebra.setPCPulseDelay(0.0)
# 		self.zebra.setPCPulseStep(0.0)
# 		self.zebra.setPCPulseMax(1)


	def setup_template(self, pilatus_template, extendedRequest, oscillation):

		print "setting up template..."
		
		pilatus_template.chi = -54.7 # Hard coded for i19-1
		pilatus_template.chiIncrement = 0
		pilatus_template.exposureTime = oscillation.getExposure_time()
		pilatus_template.kappa = 0

		if extendedRequest.getTwoTheta():
			pilatus_template.twoTheta = extendedRequest.getTwoTheta()
		else:
			pilatus_template.twoTheta = 0
		
		pilatus_template.oscillationSize = oscillation.getRange()
		pilatus_template.polarization = 0.99
		pilatus_template.sampleDetectorDistance = extendedRequest.getSampleDetectorDistanceInMM()
		pilatus_template.startAngle = oscillation.getStart()
		pilatus_template.transmission = extendedRequest.getTransmissionInPerCent()
		
		axisChoice = extendedRequest.getAxisChoice()
		pilatus_template.setOscillationAxis(axisChoice)
		
		if extendedRequest.getAxisChoice() == 'Omega':
			pilatus_template.omega = oscillation.getStart() # was set to end angle. Why?
			pilatus_template.omegaIncrement = oscillation.getRange()
			pilatus_template.phi = extendedRequest.getOtherAxis()
			pilatus_template.phiIncrement = 0
		else:
			pilatus_template.omega = extendedRequest.getOtherAxis()
			pilatus_template.omegaIncrement = 0
			pilatus_template.phi = oscillation.getStart() # was set to end angle. Why?
			pilatus_template.phiIncrement = oscillation.getRange()
		
		return pilatus_template


	def calculateEndAngle(self, start_angle, imageNum, oscRange):
		return start_angle + (imageNum * oscRange)


	def runScan(self, start_angle, scan_axis, scan_encoder):
		self.start_angle = start_angle
		end_angle = self.calculateEndAngle(start_angle, self.imageNum, self.oscRange)
		
		print "moving scan axis to start angle %.2f" % start_angle
		scan_axis.motor.speed = self.max_speed
		# set wind-back to at least the max of DEFAULT_START_DELTA degrees and 1sec of rotation
		start_delta = max(DEFAULT_START_DELTA,self.oscRange/self.exposureTimePerImage)
		scan_axis.moveTo(start_angle - start_delta)
		
		scan_speed = self.oscRange/self.exposureTimePerImage
		print "setting scan speed to %.2f deg/sec..." % scan_speed
		scan_axis.motor.speed = scan_speed
		
		self.arm_detector()
		self.arm_zebra()
		sleep(3)
		
		print "Scanning to end angle (%2.4f)..." % end_angle
		# asynchronous
		scan_axis.asynchronousMoveTo(end_angle + self.oscRange/self.exposureTimePerImage)
		print "Motor finish point (%2.4f)" %(end_angle + self.oscRange/self.exposureTimePerImage)


	def runScan2(self, start_angle, scan_axis, scan_encoder):
		
		# 1. Compute start and end positions
		self.start_angle = start_angle
		end_angle = self.calculateEndAngle(start_angle, self.imageNum, self.oscRange)
		
		# 2. Reset speed, Move to start position with wind-up interval
		self.disarm_zebra()
		sleep(1)
		print "moving scan axis to start angle %.2f" % start_angle
		scan_axis.motor.speed = self.max_speed
		scan_axis.moveTo(start_angle - (self.oscRange/self.exposureTimePerImage))

		# 3. Compute scan axis speed
		scan_speed = self.oscRange/self.exposureTimePerImage
		print "setting scan speed to %.2f deg/sec..." % scan_speed
		scan_axis.motor.speed = scan_speed
		
		# 4. Prepare position compare on zebra controller
		self.arm_detector()
		self.arm_zebra()
		sleep(3)
		
		# 5. Asynchronous trigger of move to end position
		print "moving to end angle (%2.4f)..." % (end_angle + self.oscRange/self.exposureTimePerImage)
		self.gonomega.asynchronousMoveTo(end_angle + self.oscRange/self.exposureTimePerImage)
		
		# Caller needs to reset speeds and notify observers, else use callback here


###############################################################################

zebraP = ZebraPin()
zebraManager = ZebraManager()

###############################################################################

