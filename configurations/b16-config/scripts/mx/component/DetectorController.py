import sys
import os
import time

from java.lang import IllegalArgumentException
from java.util import Optional

from gda.configuration.properties import LocalProperties
from gda.device import DeviceException
from gda.epics.connection import EpicsChannelManager
from gda.epics.connection import EpicsController

from gda.px import AxisChoice
from gda.px import MxProperties
from gda.px.detector import IAreaDetectorPilatus
from gda.px.detector import DetectorStatus
from gda.px.detector import PilatusDetectorCollectionParameters

from component.ScanControllerZebra import ScanControllerZebra
from component.shutter_control import shutterControl
from framework.script_utilities import not_implemented

from datacollection.CollectionMode import CollectionMode, COLLECT_MODE
from datacollection.DatasetMetadata import DatasetMetadata
from datacollection.RunMetadata import RunMetadata

from org.slf4j import LoggerFactory

# Detector-specific
from framework import cbf_template
from framework import PilatusScripts # @UnresolvedImport mx-config/scripts
from gdaserver import PXDetector
from gdaserver import GONIODET, GONIOOMEGA, GONIOPHI, GONIOCHI, GONIO2THETA, GONIOKAPPA


def minimum_wait_to_set_motors_busy():
	time.sleep(0.05)


class DetectorController():

	MIN_SETTLE_TIME = 3.0
	CBF_GONIO_ROTATION_AXIS = ". -1 0 0 . . ." # B16 entry for cbf header template

	def __init__(self):
		self.detector = None # IAreaDetectorPilatus
		self.shutter_control = None
		self.scan_control = None
		self.updater = self.update
		self.script_controller = None
		self.epicsController = None
		
		self.dcmode_control = CollectionMode() # Data Collection Mode Controller
		self.metadata = DatasetMetadata()
		self.runData = RunMetadata()
		
		self.logger = LoggerFactory.getLogger(__name__)


	def _readFlux(self):
		flux = 0.0 # Future: replace with read value
		return flux


	def abortCollection(self):
		didStopDetector, didCloseShutter = self.stop()
		if self.isConfigured():
			pass # any other cleanup
			# PilatusScripts.clearPilatusLastImage(self.detector, self.updater) ?
		
		return didStopDetector, didCloseShutter


	def armDetector(self):
		self.logger.info('Arming detector...')
		self.detector.start("", 0)
		self.logger.info('Detector armed.')


	def checkFileNumberUpdate(self, imageNumber, timeout, updater):
		PilatusScripts.checkPilatusFilenumberUpdate(self.detector, updater, imageNumber, timeout)


	def closeFastShutter(self):
		self.shutter_control.closeFastShutter()


	def configure(self, default='normal'):
		self.setDetector(PXDetector)
		self.shutter_control = shutterControl
		if default:
			self.dcmode_control.setMode(default)
		
		self.gonio_det = GONIODET
		self.gonio_twotheta = GONIO2THETA
		self.gonio_omega = GONIOOMEGA
		self.gonio_phi = GONIOPHI
		self.gonio_kappa = GONIOKAPPA
		
		self.resetScanController() # after axes set
		self.writer = cbf_template


	def configureScanPosition(self, runData, time_to_velocity=0.5, shutter_delay=0.03):
		# Configure position compare
		self.scan_control.configureScan(runData, None, time_to_velocity, shutter_delay)


	def doAcquisition(self, run_data): # compatibility
		return self.doOscillation(run_data)


	def doOscillation(self, run_data):
		try:
			self.logger.debug('detectorController.doOscillation')
			self.armDetector()
			is_scan_configured = self.scan_control.runScan(run_data, self.getCollectionModeController().getMode())
			# zebra should now be armed
			# scan axis should be in motion (asynchronous)
			
		except:
			_type, _exception, _traceback = sys.exc_info()
			raise DeviceException("Detector Controller FAILED to process oscillation: " + _exception.message, _exception)
		
		return is_scan_configured


	def get_scan_axis_scannable(self, runData):
		return self.scan_control.get_scan_axis_scannable(runData)


	def getCollectionModeController(self):
		return self.dcmode_control


	def getDetectorDimensionInMm(self):
		return self.detector.getDimensionInMm()


	def getDetectorPixelsX(self):
		return self.detector.getSizeX() if self.isAreaDetector() else 0


	def getDetectorPixelsY(self):
		return self.detector.getSizeY() if self.isAreaDetector() else 0


	def getDetectorStatus(self):
		try:
			return self.detector.getDetectorStatus().getValue()
		except:
			return DetectorStatus.ERROR


	def getScanController(self):
		return self.scan_control


	def getShutterState(self):
		return self.shutter_control.getFastShutterPosition() # String


	def hasDetector(self):
		return self.detector is not None


	def hasScanController(self):
		return self.scan_control is not None


	def hasShutterController(self):
		return self.shutter_control is not None


	def isAreaDetector(self):
		return True


	def isConfigured(self):
		return self.hasDetector() and self.hasScanController() and self.hasShutterController()


	def isDetectorBusy(self):
		return self.detector.isBusy()


	def isDetectorInError(self):
		return DetectorStatus.ERROR==self.getDetectorStatus()


	def isFastShutterOpen(self):
		return self.shutter_control.isShutterOpen()


	def isPilatus(self):
		return isinstance(self.detector, IAreaDetectorPilatus)


	def isScanning(self):
		return self.scan_control.isMoving()


	def isTriggered(self):
		not_implemented("DetectorController.isTriggered()")


	def openFastShutter(self):
		return self.shutter_control.openFastShutter()


	def readDetectorParameters(self):
		det_description = {}
		return det_description


	def resetScanController(self):
		''' Reset to standard collection scan controller, normal collection mode '''
		if self.scan_control:
			self.scan_control.stop()
			self.scan_control.reset()
		else:
			self.scan_control = ScanControllerZebra()
		
		self.scan_control.set_gonio_det_axis(self.gonio_det)
		# self.scan_control.set_gonio_kappa_axis(self.gonio_kappa)
		self.scan_control.set_gonio_omega_axis(self.gonio_omega)
		# self.scan_control.set_gonio_phi_axis(self.gonio_phi)
		# self.scan_control.set_gonio_twotheta_axis(self.gonio_twotheta)
		self.getCollectionModeController().setCollectionModeNormal()


	def resetSpeeds(self):
		self.scan_control._reset_speeds()


	def setCollectionModeNormal(self):
		self.getCollectionModeController().setCollectionModeNormal()


	def setDetector(self, detector):
		if detector is not None:
			assert isinstance(detector, IAreaDetectorPilatus)
			self.detector = detector
		
		else:
			raise IllegalArgumentException()


	def setDetectorMode(self, detectorMode):
		self.detector.setGain(detectorMode.gain())
		self.detector.setImageMode(detectorMode.imageMode())
		self.detector.setMode(detectorMode.triggerMode())


	def setEnergy(self, energy):
		if self.isPilatus():
			self.update("Checking detector threshold: detector.getGain():"+self.detector.getGain()+" desired energy:"+str(energy))
			if self.detector.getGain() == "Default":
				PilatusScripts.PilatusCheckThreshold(self.detector, energy, self.update)
				
			else:
				self.update("Not checking threshold because we are not in default mode. Currently, gain and threshold are: "+str(self.detector.getGain())+" "+str(self.detector.getThresholdEnergy()))
			
			self.update("Wavelength now: " + str(self.convertEVToAngstrom(energy)))


	def setScanController(self, scan_con, mode='normal'):
		self.scan_control = scan_con
		if mode:
			self.getCollectionModeController().setMode(mode)


	def setUpdate(self, update):
		self.updater = update


	def setupDetectorChannelAccess(self):
		self.epicsController = EpicsController.getInstance();
		self.channelManager = EpicsChannelManager();
		self.detector_energy_pv = "BL16B-EA-DET-04:CAM"
		self.detector_energy_high_channel =self.channelManager.createChannel(self.detector_energy_pv+':EnergyHigh', False)
		self.detector_energy_low_channel =self.channelManager.createChannel(self.detector_energy_pv+':EnergyLow', False)


	def setupDetectorParameters(self, metadata, runData):
		''' API '''
		self.logger.info("setupDetectorParameters - entry")
		
		self.runData = runData
		self.metadata = metadata
		
		self.parameters = self.setupPilatusParameters(metadata, runData)
		template_file = self.writeDetectorTemplate(self.parameters)
		self.parameters.setCbfTemplateFile(template_file)
		self.detector.initialiseDataSet(self.parameters) # sets exposure period
		
		fileFormat = "%s%s_" + MxProperties.RUN_NUMBER_FORMAT + "_00001." + self.detector.getSuffix() # "%s%s_%02d_00001.cbf"
		
		self.detector.setFilepath("/ramdisk/2021/nt29738-1/" + metadata.detectorWritePath())
		self.detector.setFileprefix(metadata.prefix())
		self.detector.setFilenumber(metadata.startRunNumber())
		self.detector.setFileformat(fileFormat)
		self.detector.setNumberOfImages(runData.numImages()) # necessary if not special collection
		self.detector.setAutoIncrement("Yes")
		
		self.detector.setExposureTime(runData.exposure()-0.003) # deadtime may not be set non-zero when set PilatusType
		
		self.detector.setMode("Ext. Trigger")
		self.detector.setImageMode("Single")
		self.detector.setGapFill(-1)
		self.detector.setDelayTime(0.0) # Use zebra pulse delay

		self.logger.info("setupDetectorParameters - exit")


	def setupPilatusParameters(self, metadata, runData):
		
		from procedure import blProcedure
		
		parameters = PilatusDetectorCollectionParameters()
		
		parameters.setWavelength(runData.wavelength())
		parameters.setTransmission(runData.transmissionInPercent())
		parameters.setFlux(Optional.of(self._readFlux()))
		parameters.setBeamX(float(blProcedure.blParameters().detector_beam_x))
		parameters.setBeamY(float(blProcedure.blParameters().detector_beam_y))
		
		parameters.setAlpha(0.0)
		parameters.setKappa(0.0)
		parameters.setTwoTheta(0.0)
		parameters.setChi(0.0)
		parameters.setChiIncrement(0.0)
		
		parameters.setOscillationSize(runData.range())
		parameters.setExposureTime(runData.exposure())
		parameters.setPolarization(0.01)
		
		detDistanceOffset = 0.0
		detVerticalOffset = 0.0
		parameters.setSampleDetectorDistance(runData.detDistance()+detDistanceOffset)
		parameters.setDetectorVOffset(detVerticalOffset)
		
		parameters.setOscillationAxis(runData.axisChoice())
		parameters.setStartAngle(runData.start())
		scanAxisName = runData.axisChoice()
		
		if scanAxisName == AxisChoice.OMEGA.getCode():
			parameters.setOmega(runData.start())
			parameters.setOmegaIncrement(runData.step())
			parameters.setPhi(runData.otherAxis())
			parameters.setPhiIncrement(0.0)
		
		else:
			raise IllegalArgumentException(scanAxisName)
		
		return parameters


	def setupScanPosition(self, runData):
		# Move to pre-scan position
		self.scan_control.setupScanPosition(runData)


	def start(self, filename, scanAxisStart, updater=None):
		try:
			self.detector.start(filename, scanAxisStart)
		
		except:
			raise DeviceException('FAIL to start acquisition on detector', sys.exc_info()[1])


	def stop(self):
		if self.isConfigured():
			try:
				self.scan_control.stop() # stop scan axis, close shutter
			except:
				self.logger.warn("Fail to close shutter") # and continue
			
			try:
				self.detector.abort()
			except:
				self.logger.warn("Fail to abort detector acquisition") # and continue
			
			try:
				self.scan_control.disarm()
			except:
				self.logger.warn("Fail to disarm scan_control (zebra)") # and continue
			
		else:
			self.logger.warn("Fail to close shutter")
			self.logger.warn("Fail to abort detector acquisition")
		
		return not self.detector.isBusy(), not self.shutter_control.isFastShutterOpen()


	def update(self, message):
		self.logger.info(message)
		print (message) # default


	def waitWhileMoving(self):
		self.scan_control.waitWhileBusy()


	def waitWhileScanning(self):
		self.scan_control.waitWhileScanning()


	def waitUntilDetectorReady(self):
		self.detector.waitForReady()


	def writeDetectorTemplate(self, parameters):
		# pixel_size = [0.172, 0.172]
		if self.writer.should_write_template():
			semirandom_filename = "%03d.cif" % int(time.time() * 1000 % 1000)
			template_location = "/dls_sw/b16/software/var_diffraction/cbf-cache/"
			template_file = os.path.join(template_location, semirandom_filename)
			self.update("writing CBF template to " + template_file)
			self.writer.write_template(template_file, {
				'detector_id': self.detector.getId(),
				'detector_name': self.detector.getName(),
				'beam_x': parameters.getBeamX(),
				'beam_y': parameters.getBeamY(),
				'pixel_size_x': self.detector.pixelSize[0],
				'pixel_size_y': self.detector.pixelSize[1],
				'distance': parameters.getSampleDetectorDistance(),
				"gonio_rotation_axis": DetectorController.CBF_GONIO_ROTATION_AXIS
			})
			
		else:
			self.update("not writing CBF template")
			template_file = "0" # need to tell it 0 to unset
			
		parameters.setCbfTemplateFile(template_file)
		return template_file


	def writeMetadata(self, run_data, parameters, beam_posn):
		pass


detectorController = DetectorController()
detectorController.configure()
