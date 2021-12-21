from time import sleep
import sys
import jarray
from gov.aps.jca.event import PutListener; # @UnresolvedImport
from gov.aps.jca import CAStatus  # @UnresolvedImport
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from gda.scan import PointsScan, ScanInformation
from gda.factory import Finder
from Diamond.PseudoDevices.FileFilter import SrsFileFilterClass
from Diamond.Utility.ScriptLogger import ScriptLoggerClass
from i06shared.commands.dirFileCommands import nfn
from gda.device.detector.nxdetector.roi import ImutableRectangularIntegerROI
from gda.device.detector import NXDetector
from gda.device.detector.nxdetector.plugin.areadetector import ADRoiStatsPair
from types import ListType
from gda.device.detector.addetector.filewriter import MultipleImagesPerHDF5FileWriter,\
	SingleImagePerFileWriter
from gda.jython import ScriptBase
import scisoftpy as dnp
from gda.configuration.properties import LocalProperties
from gda.jython import InterfaceProvider
from java.io import File
from gdascripts.metadata.nexus_metadata_class import meta

beamline_name = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME, "i06")
logger=ScriptLoggerClass();

class FastEnergyScanControlClass(object):
	""" """
	#CA Put Callback listener that handles the callback event
	class CaputCallbackListenerClass(PutListener):
		def __init__ (self, device):
			self.device = device
			
		def putCompleted(self, event):
			if event.getStatus() != CAStatus.NORMAL:  # @UndefinedVariable
				logger.simpleLog('Motor move failed!')
				logger.simpleLog('Failed source: ' + event.getSource().getName())
			else:
				if self.device.isScanAborted():
					logger.simpleLog('Epics Scan aborted. The FastEnergyScanControlClass calls back successfully')
				else:
					logger.logger.debug('FastEnergyScanControlClass.CaputCallbackListenerClass.putCompleted:Epics Scan finished. The FastEnergyScanControlClass calls back successfully. Delaying...')
					sleep(1)
					self.device.fixDataHead()
					logger.logger.debug('FastEnergyScanControlClass.CaputCallbackListenerClass.putCompleted:... Data Head fixed.')
			self.device.isCalled = True

	FASTSCAN_MODE = range(3)
	FASTSCAN_MODE_EPICS_STRING = ["Fixed", "Const velocity", "Slaved"]
	FASTSCAN_MODE_GDA_STRING  = ['fixid', 'cvid', 'slaveid']
	
	FASTSCAN_STATUS = range(10)
	FASTSCAN_STATUS_STRING = ["Scan complete", "Scan aborted", "Moving PGM to midpoint", 
							"Calculating parameters", "Moving IDD and PGM to start position", 
							"Scan ready", "Starting scan move", "Scanning", "Scan complete", "Idle"]
	#Total 6 status from Epics, plus internal Idle status
	#	"Scan complete"
	#	"Scan aborted"
	#	"Moving PGM to midpoint"
	#	"Calculating parameters"
	#	"Moving IDD and PGM to start position"
	#	"Scan ready"
	#	"Starting scan move"
	#	"Scanning"
	#	"Scan complete"
	#	"Idle"

	def __init__(self, name, rootPV):
		self.name = name
		self.setupEpics(rootPV)
		
		self.startEnergy=600
		self.endEnergy=700

		self.scanStatus='Idle'
		
		self.putListener = FastEnergyScanControlClass.CaputCallbackListenerClass(self)
		self.isCalled = True
		self.areaDetector=None
		self.adbase=None
		self.pvName=None
		self.existingCameraParametersCaptured=False

	def __del__(self):
		self.cleanChannel(self.chScanReady01)
		self.cleanChannel(self.chScanReady02)
		self.cleanChannel(self.chScanReady03)
		self.cleanChannel(self.chScanReady04)

		self.cleanChannel(self.chScanReady)

		self.cleanChannel(self.chStartEnergy)
		self.cleanChannel(self.chEndEnergy)
		self.cleanChannel(self.chScanTime)
		self.cleanChannel(self.chNumberOfPoints)
		self.cleanChannel(self.chIdMove)
		self.cleanChannel(self.chAreaDetector)
		self.cleanChannel(self.chADCIntegration)
		
		self.cleanChannel(self.chBuild)
		self.cleanChannel(self.chBuildStatus)
		self.cleanChannel(self.chExecute)
		self.cleanChannel(self.chStop)
		self.cleanChannel(self.chStatus)
		
		self.cleanChannel(self.chHead)

		self.cleanChannel(self.chVelocityStatus)

		self.cleanChannel(self.chPGMStatus)

		if beamline_name == "i06":
			self.cleanChannel(self.chMedipixMode)
			
	def setupEpics(self, rootPV):
#		Epics PVs for checking fast scan readiness:
		self.chScanReady01=CAClient(rootPV + ":PGM:HOME.RVAL");  self.configChannel(self.chScanReady01);
		self.chScanReady02=CAClient(rootPV + ":PGM:MODE.RVAL");  self.configChannel(self.chScanReady02);
		self.chScanReady03=CAClient(rootPV + ":ID:ENABLE.RVAL"); self.configChannel(self.chScanReady03);
		self.chScanReady04=CAClient(rootPV + ":DATA:OK.RVAL");   self.configChannel(self.chScanReady04);

#		New Epics PV for checking fast scan readiness, this should be used to replace the above four pvs:
		self.chScanReady=CAClient(rootPV + ":STATUS");  self.configChannel(self.chScanReady);
		
#		Epics PVs for fast scan parameters setup:
		self.chStartEnergy=CAClient(rootPV + ":EV:START"); self.configChannel(self.chStartEnergy);
		self.chEndEnergy=CAClient(rootPV + ":EV:FINISH"); self.configChannel(self.chEndEnergy);
		self.chScanTime=CAClient(rootPV + ":TIME"); self.configChannel(self.chScanTime);
		self.chNumberOfPoints=CAClient(rootPV + ":NPULSES"); self.configChannel(self.chNumberOfPoints);
		self.chIdMode=CAClient(rootPV + ":IDMODE"); self.configChannel(self.chIdMode);
		self.chAreaDetector=CAClient(rootPV + ":AD:TRIGGER"); self.configChannel(self.chAreaDetector);
		self.chADCIntegration=CAClient(rootPV + ":ADCSC:TRIGGER"); self.configChannel(self.chADCIntegration);
		
#		Epics PVs for fast scan control and status:
		self.chBuild=CAClient(rootPV + ":BUILD"); self.configChannel(self.chBuild);
		self.chBuildStatus=CAClient(rootPV + ":BUILDSTATUS"); self.configChannel(self.chBuildStatus);
		self.chExecute=CAClient(rootPV + ":START"); self.configChannel(self.chExecute);
		self.chStop=CAClient(rootPV + ":STOP");self.configChannel(self.chStop);
		self.chStatus=CAClient(rootPV + ":RUN:STATE"); self.configChannel(self.chStatus);

		#Epics PV for the Number of elements available
		self.chHead=CAClient(rootPV + ":ELEMENTCOUNTER");  self.configChannel(self.chHead);

		self.chVelocityStatus=CAClient("BL06I-OP-IDD-01:SET:VEL.STAT"); self.configChannel(self.chVelocityStatus);
		
		#To check the PGM is not stucked
		self.chPGMStatus=CAClient("BL06I-OP-PGM-01:ENERGY.DMOV"); self.configChannel(self.chPGMStatus);
		
		if beamline_name == "i06":
			#To configure medipix's driver mode
			self.chMedipixMode=CAClient("BL06I-EA-DET-02:CAM:QuadMerlinMode"); self.configChannel(self.chMedipixMode);
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure()

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup()

# 	def fixPGM(self):
# 			pgminit();

	#To check the PGM is not used or stucked
	def checkPGM(self):
		dmov = int(float(self.chPGMStatus.caget()))
		
		if (dmov == 0): #stucked
# 			self.fixPGM();
			dmov = int(float(self.chPGMStatus.caget()))
		return (dmov == 1)

	#To check the PGM and ID motors are ready for the fast scan
	def checkMotorReady(self):
		c= int(float(self.chScanReady.caget()))
		return (c == 0)

##### add support for area detector	
	def setAreaDetector(self, areadet):
		self.areaDetector=areadet
		
	def getAreaDetector(self):
		return self.areaDetector
	
	def prepareAreaDetectorForCollection(self, areadet, expotime, numImages):
		#get camera control object
		cs=areadet.getCollectionStrategy()
		# medipix - 4 level of decoratee in collection strategy
		self.adbase=cs.getDecoratee().getDecoratee().getDecoratee().getDecoratee().getAdBase()
		if self.adbase is not None:
			#capture existing settings that will be changed for fast scan
			self.aquire_state=self.adbase.getAcquireState()
			sleep(0.1)
			self.exposure_period=self.adbase.getAcquirePeriod()
			sleep(0.1)
			self.exposure_time=self.adbase.getAcquireTime()
			sleep(0.1)
			self.image_mode=self.adbase.getImageMode()
			sleep(0.1)
			self.num_images=self.adbase.getNumImages()
			sleep(0.1)
			self.trigger_mode=self.adbase.getTriggerMode()
			sleep(0.1)
			self.drive_mode=int(self.chMedipixMode.caget())
			sleep(0.1)
			self.existingCameraParametersCaptured=True
			#stop camera before change settings
			self.adbase.stopAcquiring()
			sleep(0.5)
			#set camera parameters for fast scan
			self.adbase.setAcquireTime(expotime)
			sleep(0.5)
			self.adbase.setAcquirePeriod(expotime)
			sleep(0.5)
			self.adbase.setImageMode(1) # Multiple
			sleep(0.5)
			self.adbase.setNumImages(numImages)
			sleep(0.5)
			self.adbase.setTriggerMode(0) # Auto
			sleep(0.5)
			self.chMedipixMode.caput(3)
			sleep(1.0)
		else:
			raise RuntimeError("self.adbase is not defined!")
		if self.isKBRastering():
			self.prepareKBMirrorRastering(expotime)
	
	def setKBRasteringControlPV(self, pvname):
		self.pvName=pvname
	
	def getKBRasteringControlPV(self):
		return self.pvName
	
	def setKBRastering(self, b):
		self.enableKBRastering = b
	
	def isKBRastering(self):
		return self.enableKBRastering
		
	def prepareKBMirrorRastering(self, expotime):
		if self.pvName:
			self.ch = CAClient(self.pvName)
			self.configChannel(self.ch)
			self.cachedCh = float(self.ch.caget())
			if "FREQ" in self.pvName:
				self.ch.caput(1.0/expotime)
			if "PERIOD" in self.pvName:
				self.ch.caput(expotime)
	
	def restoreKBMirrorRastering(self):
		if self.pvName:
			self.ch.caput(self.cachedCh)
			
	def restoreAreaDetectorParametersAfterCollection(self):
		if not self.existingCameraParametersCaptured:
			return
		if self.adbase is not None:
			#stop camera before change settings
			self.adbase.stopAcquiring()
			sleep(0.5)
			#restore camera parameters before fast scan
			self.adbase.setAcquireTime(self.exposure_time)
			sleep(0.5)
			self.adbase.setAcquirePeriod(self.exposure_period)
			sleep(0.5)
			self.adbase.setImageMode(self.image_mode) # Multiple
			sleep(0.5)
			self.adbase.setNumImages(self.num_images)
			sleep(0.5)
			self.adbase.setTriggerMode(self.trigger_mode) # Auto
			sleep(0.5)
			self.chMedipixMode.caput(self.drive_mode)
			sleep(1.0)
			if self.aquire_state == 1:
				self.adbase.startAcquiring()
				sleep(0.5)
		else:
			raise RuntimeError("self.adbase is not defined!")
		if self.isKBRastering():
			self.restoreKBMirrorRastering()
		
	def configureFileWriterPlugin(self, areadet, numImages):
		if not isinstance(areadet, NXDetector):
			raise TypeError("'%s' detector is not a NXDetector! " % (areadet.getName()))
		additional_plugin_list = areadet.getAdditionalPluginList()
		datawriter = None
		scanNumber = nfn()
		for each in additional_plugin_list:
			if isinstance(each, MultipleImagesPerHDF5FileWriter):
				datawriter = each
				datawriter.getNdFile().getPluginBase().disableCallbacks()
				datawriter.getNdFile().getPluginBase().setBlockingCallbacks(0)
				filePathUsed = InterfaceProvider.getPathConstructor().createFromDefaultProperty() + "/"
				f = File(filePathUsed)
				if not f.exists() and not f.mkdirs():
						raise IOError("Folder does not exist and cannot be made: " + str(filePathUsed))
				datawriter.getNdFile().setFilePath(filePathUsed)
				if not datawriter.getNdFile().filePathExists():
					raise IOError("Path does not exist on IOC '" + filePathUsed + "'")
				datawriter.getNdFile().setFileName("medipix")
				datawriter.getNdFile().setFileNumber(scanNumber)
				datawriter.getNdFile().setAutoIncrement(0)
				datawriter.getNdFile().setAutoSave(0)
				datawriter.getNdFile().setFileWriteMode(2)
				datawriter.getNdFileHDF5().setStoreAttr(0)
				datawriter.getNdFileHDF5().setStorePerform(0)
				datawriter.getNdFileHDF5().setLazyOpen(True)
				datawriter.getNdFileHDF5().setBoundaryAlign(0)
				datawriter.getNdFileHDF5().setNumCapture(numImages)
				datawriter.getNdFileHDF5().setNumRowChunks(0)
				datawriter.getNdFileHDF5().setNumColChunks(0)
				datawriter.getNdFileHDF5().setNumFramesChunks(0)
				datawriter.getNdFileHDF5().setNumFramesFlush(0)
				datawriter.getNdFileHDF5().startCapture()
				datawriter.getNdFile().getPluginBase().enableCallbacks()

			elif isinstance(each, SingleImagePerFileWriter):
				datawriter = each
				datawriter.getNdFile().getPluginBase().disableCallbacks()
				filePathUsed = InterfaceProvider.getPathConstructor().createFromDefaultProperty() + "/" + str(scanNumber) + "_MedipixImage/"
				f=File(filePathUsed)
				if not f.exists() and not f.mkdirs():
						raise IOError("Folder does not exist and cannot be made: " + str(filePathUsed))
				datawriter.getNdFile().setFilePath(filePathUsed)
				if not datawriter.getNdFile().filePathExists():
					raise IOError("Path does not exist on IOC '" + filePathUsed + "'")
				datawriter.getNdFile().setFileName("medipix")
				datawriter.getNdFile().setFileNumber(1)
				datawriter.getNdFile().setAutoIncrement(1)
				datawriter.getNdFile().setAutoSave(1)
				datawriter.getNdFile().setFileWriteMode(0)
				datawriter.getNdFile().getPluginBase().enableCallbacks()
		if datawriter is None:
			raise RuntimeError("Cannot find EPICS File Writer Plugin for detector %s" % (areadet.getName()))	
# 		datawriter.prepareForCollection(numImages, ScanInformation.EMPTY)
		
	def disableFileWritingPlugin(self, areadet):
		if not isinstance(areadet, NXDetector):
			raise TypeError("'%s' detector is not a NXDetector! " % (areadet.getName()))
		additional_plugin_list = areadet.getAdditionalPluginList()
		datawriter=None
		for each in additional_plugin_list:
			if isinstance(each, MultipleImagesPerHDF5FileWriter):
				datawriter = each
				datawriter.getNdFile().getPluginBase().disableCallbacks()
				datawriter.getNdFileHDF5().stopCapture();
			elif isinstance(each, SingleImagePerFileWriter):
				datawriter = each
				datawriter.getNdFile().getPluginBase().disableCallbacks()
		if datawriter is None:
			raise RuntimeError("Cannot find EPICS File Writer Plugin for detector %s" % (areadet.getName()))	
		
	def setupAreaDetectorROIs(self, rois, roi_provider_name='medipix_roi'):
		'''update ROIs list in GDA but not yet set to EPICS
		This must be called when ROI is changed, and before self.prepareAreaDetectorForCollection(areadet)
		@param rois: list of rois i.e. [[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size]]
		'''
		if not type(rois) == ListType:
			raise TypeError("Input must be a list of ROIs, each provides a list specifies [x_start,y_start,x_size,y_size]")
		i=1
		newRois=[]
		for roi in rois:
			newRoi = ImutableRectangularIntegerROI(roi[0],roi[1],roi[2],roi[3],'Region'+str(i))
			i += 1
			newRois.append(newRoi)
		roi_provider = Finder.find(roi_provider_name)
		roi_provider.updateRois(newRois)
		
	def clearAreaDetectorROIs(self, roi_provider_name='medipix_roi'):
		roi_provider = Finder.find(roi_provider_name)
		roi_provider.updateRois([])
	
	def getROIStatsPair4DetectorFromGDA(self, areadet):
		''' retrieve GDA ROI and STAT pairs for a given detector
		'''
		if not isinstance(areadet, NXDetector):
			raise TypeError("'%s' detector is not a NXDetector! " % (areadet.getName()))
		additional_plugin_list = areadet.getAdditionalPluginList()
		roi_stat_pairs = []
		for each in additional_plugin_list:
			if isinstance(each, ADRoiStatsPair):
				roi_stat_pairs.append(each)
		return roi_stat_pairs

	def prepareAreaDetectorROIsForCollection(self, areadet, numImages):
		'''configure ROIs and STATs plugins in EPICS for data collection with regions of interests
		@param areadet: must be a NXDetector 
		'''
		for each in self.getROIStatsPair4DetectorFromGDA(areadet):
			#ScanInformation is not used in zacscan so just create a dummy to make Java method works
			#update ROIs and enable EPICS rois and stats plugins
			each.prepareForCollection(numImages, ScanInformation.EMPTY)

	def stopROIStatsPair(self, areadet):
		'''stop or abort ROI and STAT plug-in processes. 
		This must be called when users interrupt or abort beam stabilisation process!
		'''
		for each in self.getROIStatsPair4DetectorFromGDA(areadet):
			each.stop()
	
	def completeCollectionFromROIStatsPair(self,areadet):
		'''must be called when beam stabilisation process completed!
		IMPORTANT: test prove this method leave ROI-STAT pair locked, should not be used until Java code fix this.
		'''
		for each in self.getROIStatsPair4DetectorFromGDA(areadet):
			each.completeCollection()

	def enableAreaDetector(self):
		self.chAreaDetector.caput(1) # 0-Disabled, 1-Enabled
		
	def disableAreaDetector(self):
		self.chAreaDetector.caput(0) # 0-Disabled, 1-Enabled

	def setEnergyRange(self, startEnergy, endEnergy):
		self.startEnergy = startEnergy
		self.endEnergy = endEnergy
		self.chStartEnergy.caput(startEnergy)
		self.chEndEnergy.caput(endEnergy)

	def getEnergyRange(self):
		return [self.startEnergy, self.endEnergy]

	def setTime(self, scanTime, pointTime):
		numberOfPoints = scanTime/pointTime
		self.chScanTime.caput(scanTime)
		self.chNumberOfPoints.caput(numberOfPoints)

	def getNumberOfPoint(self):
		return int( float(self.chNumberOfPoints.caget()))
	
	def getVelocityStatus(self):
		return self.chVelocityStatus.caget()
		
	
	def getDataHead(self):
		head = int(float(self.chHead.caget()))
		return head;
	
	def fixDataHead(self):
		head = self.getDataHead()
		numberOfPoint = self.getNumberOfPoint()
		
		if head >= numberOfPoint:
			logger.logger.debug("Enough points generated by the scan.")
		else:
			logger.simpleLog("Not enough points generated by the scan. Fix is needed to finished the scan.")
			self.chHead.caput(numberOfPoint)


	#trigger the scan
	def startScan(self):
		'''trigger the scan and setup callback listener for checking
		'''
		self.isCalled = False
		self.chExecute.getController().caput(self.chExecute.getChannel(), 1, self.putListener)

	#Abort the scan
	def abortScan(self):
		self.chStop.caput(1)
#		self.fixPGM();

	def setIDMode(self, mode):
		self.chIdMode.caput(mode) #select the ID Mode 

	def getIDMode(self):
		idmode=self.chIdMode.caget()
		return int(float(idmode))	

	#trigger the scan
	def buildScan(self, timeout=None):
		if timeout is None:
			self.chBuild.caput('Busy') # click the build button and return
		else:
			self.chBuild.caput('Busy', timeout) # click the build button and wait for the call back		

	def isBuilt(self):
		strStatus = self.getScanStatus()
			
		if strStatus == 'Build failed - ID velocity too slow': #Built error
			raise RuntimeError("Fast energy scan CAN NOT be built. Please check the ID speed setting is not too slow!")
		elif strStatus == 'Scan ready': #Finished building
			return True
		else:
			return False

	def isScanReady(self):
		strStatus = self.getScanStatus()
		if strStatus == "Scan ready": #Finished building
			return True
		else:
			return False
		
	def isScanning(self):
		strStatus = self.getScanStatus()
		if strStatus == "Scanning": #Finished building
			return True
		else:
			return False

	def isScanComplete(self):
		strStatus = self.getScanStatus()
		if strStatus in ['Scan complete', 'Scan aborted'] and self.isCalled: #The last scan is finished and is called back
			return True
		else:
			return False
		
	def isScanAborted(self):
		strStatus = self.getScanStatus()
		if strStatus == "Scan aborted": #The last scan is aborted.
			return True
		else:
			return False

	def getScanStatus(self):
		newScanStatus = self.chStatus.caget()
		if newScanStatus != self.scanStatus: # scan status changed
			self.scanStatus = newScanStatus
		return self.scanStatus
	
###########################################################################
class FastEnergyScanIDModeClass(ScannableMotionBase):
	""" """

	def __init__(self, name, fastEnergyScanController):
		self.setName(name)
		self.setInputNames([name])
		self.setExtraNames([])
		self.setOutputFormat(["%12.6f"])
		self.setLevel(6)

		self.fesController = fastEnergyScanController

	#set the ID mode
	def setIDMode(self, mode):
		self.fesController.setIDMode(mode)

	#get the ID mode
	def getIDMode(self):
		return self.fesController.getIDMode()

#ScannableMotionBase Implementation
	def getPosition(self):
		mode = self.getIDMode()
		modeString = FastEnergyScanControlClass.FASTSCAN_MODE_GDA_STRING[mode]
		return modeString

	def asynchronousMoveTo(self,newPos):
		if newPos in FastEnergyScanControlClass.FASTSCAN_MODE:
			mode = newPos
		elif newPos in FastEnergyScanControlClass.FASTSCAN_MODE_EPICS_STRING:
			mode = FastEnergyScanControlClass.FASTSCAN_MODE_EPICS_STRING.index(newPos)
		elif newPos in FastEnergyScanControlClass.FASTSCAN_MODE_GDA_STRING:
			mode = FastEnergyScanControlClass.FASTSCAN_MODE_GDA_STRING.index(newPos)
		else:
			print("Please use 'fixid', 'cvid' or 'slaveid' to set the fast energy scan mode")
			return
		
		self.setIDMode(mode)
		
	def isBusy(self):
		return False
	
	def toString(self):
		modeInfo = "Fast Energy Scan ID mode: " + self.getPosition()
		return modeInfo

###########################################################################
class FastEnergyDeviceClass(ScannableMotionBase):
	""" """

	def __init__(self, name, fastEnergyScanController, fastEnergyScanDetector):
		self.setName(name)
		self.setInputNames([name])
		self.setExtraNames([])
		self.setOutputFormat(["%12.6f"])
		self.setLevel(6)

		self.fesController = fastEnergyScanController
		self.fesDetector = fastEnergyScanDetector
		
		self.scanStatus='Idle'
		self.indexPosition = 0
		self.indexChannel = 6

		self.delay=None

	def setDelay(self, delay):
		self.delay = delay

	def setIDMode(self, mode):
		self.fesController.setIDMode(mode)

	def getIDMode(self):
		return self.fesController.getIDMode()

	def buildScan(self):
		try:
			if not self.fesController.checkMotorReady():
				raise RuntimeError("Fast energy scan CAN NOT be performed. Please check both PGM and ID are ready!")
			
			if self.fesController.getScanStatus() not in ["Scan complete", "Scan aborted", "Build failed - ID velocity too slow"]: #Not in Ready to Build status
				raise RuntimeError("Fast energy scan CAN NOT be built because of wrong EPICS status!")
			
			#trigger the scan
			self.fesController.buildScan()
			print("Start building the fast energy scan...")
		
			while not self.fesController.isBuilt():
				logger.singlePrint('... ' + self.fesController.getScanStatus())
				sleep(2)
			print('Fast Scan Built')
			
		except:
			exceptionType, exception, traceback=sys.exc_info();
			logger.fullLog(None, "Error occurs at FastEnergyDeviceClass.buildScan", exceptionType, exception, traceback, True)

	def execScan(self):
		try:
			if not self.fesController.isScanReady():
				raise RuntimeError("Fast energy scan CAN NOT be performed. Please build the scan first!")
		
			print("Start the fast energy scan...")
			self.fesController.startScan()
			self.fesDetector.reset()
			self.indexPosition = 0
			sleep(2)
		except:
			exceptionType, exception, traceback=sys.exc_info()
			logger.fullLog(None, "Error occurs at FastEnergyDeviceClass.execScan", exceptionType, exception, traceback, True)
		
#ScannableMotionBase Implementation
	def atScanStart(self):
		try:
			self.buildScan()
			self.execScan()
		except:
			exceptionType, exception, traceback=sys.exc_info()
			logger.fullLog(None, "Error occurs at FastEnergyDeviceClass.atScanStart", exceptionType, exception, traceback, True)

	def atScanEnd(self):
		return

	def atScanLineStart(self):
		return
		
	def atScanLineEnd(self):
		return

	def atPointStart(self):
		return
	
	def atPointEnd(self):
		self.indexPosition += 1

	def getPosition(self):
		return self.fesDetector.readoutChannel(self.indexChannel)

	def asynchronousMoveTo(self,newPos):
		self.fesDetector.asynchronousMoveTo(self.indexPosition)
		if self.delay is not None:
			sleep(self.delay)
		
	def isBusy(self):
		if self.fesDetector.isDataAvailable():
			return False
		else:
			if self.delay is not None:
				sleep(self.delay)
			return True	
	
	def toString(self):
		p = self.getPosition();
		return str(p);

	def stop(self):
		print("%s: Panic Stop Called" % self.getName())
		self.fesController.abortScan();
		if beamline_name == "i06":
			self.fesController.getAreaDetector().stop()
			self.fesController.stopROIStatsPair(self.fesController.getAreaDetector())
			self.fesController.disableFileWritingPlugin(self.fesController.getAreaDetector())
			self.fesController.restoreAreaDetectorParametersAfterCollection()
		self.fesController.existingCameraParametersCaptured=False

	def cvscan(self, startEnergy, endEnergy, scanTime, pointTime):
		command = "zacscan " + str(startEnergy) + " " + str(endEnergy) + " " + str(scanTime) + " " + str(pointTime)
		if not self.fesController.checkPGM():
			print("PGM is not in a movable status. Please check it manually!")
			return

		if startEnergy >= endEnergy:
			print("Can only scan from low energy to high energy!")
			raise RuntimeError('Wrong Energy Range!')

		self.fesDetector.reset()
		sleep(1)
		self.fesDetector.setFilter(startEnergy, endEnergy, self.indexChannel)
		self.fesController.setEnergyRange(startEnergy, endEnergy)
		self.fesController.setTime(scanTime, pointTime)
#		self.fesController.setIDMode(1)
			
		#to set delay half of point time
		self.setDelay(pointTime*0.5)
		
		numPoint = self.fesController.getNumberOfPoint()
		if numPoint < 1:
			print("Number of scan points is set to ZERO. Please check your command carefully!")
			return
		
		if beamline_name == "i06":
			self.fesController.enableAreaDetector() #using area detector
			self.fesController.prepareAreaDetectorForCollection(self.fesController.getAreaDetector(), pointTime, numPoint)
			self.fesController.configureFileWriterPlugin(self.fesController.getAreaDetector(), numPoint)
			self.fesController.prepareAreaDetectorROIsForCollection(self.fesController.getAreaDetector(), numPoint)
				
		#pscan fastEnergy 0 1 numPoint fesData 0 1;
		fesData = self.fesDetector;
		meta.addScalar("user_input", "command", command)
		try:
			theScan = PointsScan([self,0,1,numPoint,fesData,0,1])
			theScan.runScan()
		except:
			exceptionType, exception, traceback=sys.exc_info()
			logger.fullLog(None, "Error occurs at FastEnergyDeviceClass.cvscan", exceptionType, exception, traceback, True)
		finally:
			meta.rm("user_input", "command")
			
		while(not self.fesController.isScanComplete() ):
			logger.singlePrint( "Wait for the fast energy scan to finish" )
			sleep(1)

		if self.fesController.isScanAborted():
			print("The Fast Energy Scan is aborted.")
		else:
			if beamline_name == "i06":
				# restore ADRoiStatsPair state in GDA
# 				self.fesController.completeCollectionFromROIStatsPair(self.fesController.getAreaDetector())
				self.fesController.stopROIStatsPair(self.fesController.getAreaDetector())
				self.fesController.disableFileWritingPlugin(self.fesController.getAreaDetector())
				#restore area detector settings	
				self.fesController.restoreAreaDetectorParametersAfterCollection()
				self.fesController.existingCameraParametersCaptured=False
				
			print("The Fast Energy Scan is completed.")

#######################################################
class EpicsWaveformDeviceClass(ScannableMotionBase):
	def __init__(self, name, rootPV, channelList, extraChannelList=[], elementCounter="iddFastScanElementCounter"):

		self.numberOfChannels = len(channelList)
		self.setupEpics(rootPV)
		
		self.setName(name)
		self.setInputNames(["pIndex"])
		self.setLevel(7)
		en = []; of = ["%5.0f"];
		for c in channelList + extraChannelList:
			en.append( str(c) )
			of.append("%20.12f")

		self.setExtraNames(en)
		self.setOutputFormat(of)

		self.timeout = 30
		self.defaultSize = 100
		self.low = 0
		self.high = 1000
		self.keyChannel = None
		self.firstTime = True

		self.fastScanElementCounter = Finder.find(elementCounter)

		self.reset()

	def __del__(self):
		self.cleanChannel(self.chHead)
		for chd in self.chData:
			self.cleanChannel(chd)

	def reset(self):
		self.data=[[None]]*self.numberOfChannels
		self.dataset = None
		self.readPointer = -1
		#according to Pete leicester GDA should not reset Element Counter
# 		self.resetHead()
		
	def setFilter(self, low, high, keyChannel):
		self.low = low
		self.high = high
		self.keyChannel=keyChannel
		
	def getDataLength(self):
		if self.dataset is None:
			return 0
		dim = self.dataset.shape
		return dim[1]


	"""
	waveform PVs
	rootPV          = 'BL06I-MO-FSCAN-01'
	pvElementCounter= 'BL06I-MO-FSCAN-01:ELEMENTCOUNTER'

	pvDataChannel01 = 'BL06I-MO-FSCAN-01:CH1DATA'
	pvDataChannel02 = 'BL06I-MO-FSCAN-01:CH2DATA'
	pvDataChannel03 = 'BL06I-MO-FSCAN-01:CH3DATA'
	pvDataChannel04 = 'BL06I-MO-FSCAN-01:CH4DATA'
	...
	"""	
	def setupEpics(self, rootPV):
		#Epics PV for the Number of elements available
		self.chHead=CAClient(rootPV + ":ELEMENTCOUNTER")
		self.configChannel(self.chHead)

#		Epics PVs for the channels:
		self.chData=[]
		for i in range(self.numberOfChannels):
			self.chData.append( CAClient(rootPV + ":CH" + str(i+1) + "DATA"))
			self.configChannel(self.chData[i])
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure()

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup()

#	Epics level operation:
	def getHead(self):
		if self.fastScanElementCounter != None:
			return int(float(self.fastScanElementCounter()))-1
		else:
			head = int(float(self.chHead.caget()))-1
			return head

	def resetHead(self):
		self.chHead.caput(0)
		
	def atScanStart(self):
		self.firstTime = True
	
	def getNewEpicsData(self, offset, size):
		if self.firstTime:
			sleep(2.0)
			self.firstTime = False
		#To check the head
		head=self.getHead()
		if offset > head:
			# No new data available. Offset exceeds Head
			return False

		la=[]
		#To get the waveform data from EPICS
		for i in range(self.numberOfChannels):
			ok = False
			while( not ok):
				try:
					self.data[i] = self.chData[i].getController().cagetDoubleArray(self.chData[i].getChannel(), head+1)
					ok = True
				except:
					type1, exception, traceback = sys.exc_info()
					logger.fullLog(None,"Error in EpicsWaveformDeviceClass.getNewEpicsData reading channel %d" %i, type1, exception , traceback, False)
					ScriptBase.checkForPauses()
			la.append(self.data[i])
		
		self.dataset = dnp.array(la) 
		return True

	def getUnFilteredPosition(self):
		resultlist = [self.readPointer] #The index
		resultlist.extend(list(self.readout())) # the readout		
		resultjavaarray = jarray.array(resultlist, 'd')
		return resultjavaarray
		
	def applyFilter(self, inputlist, low, high, index):
		if index is None:
			return inputlist
		
		outputlist = []
		judge = inputlist[index]
		for i in range(len(inputlist)):
			if (judge >= low and judge <= high) or i == index:
				outputlist.append(inputlist[i])
			else:
				outputlist.append(0)
				
		return outputlist

	def getFilteredPosition(self):
		filtered_readout = self.applyFilter(list(self.readout()), self.low-1.0, self.high+1.0, self.keyChannel-1)
		result_list = [self.readPointer] #The index
		result_list.extend(filtered_readout) # the readout		
		result_java_array = jarray.array(result_list, 'd')
		return result_java_array

# DetectorBase Implementation
	def getPosition(self):
#		return self.getUnFilteredPosition()
		return self.getFilteredPosition()

	def asynchronousMoveTo(self,newPosition):
		self.readPointer = int(newPosition);

	def isDataAvailable(self):
		len1 = self.getDataLength(); #read current dataset size in this object
		if len1 == 0 or self.readPointer > len1-1: #either dataset is empty or no new data
			while self.getNewEpicsData(len1, self.defaultSize): #read data from EPICS into dataset
				len1 = self.getDataLength()
				if self.readPointer <= len1-1:#After updating dataset, new data available
					return True
			return False #Epics data exhausted. 
		else: #self.readPointer <= len1-1, which means there are new data in the buffer to offer
			return True

	def isBusy(self):
		return False

	def readout(self):
		if self.firstTime:
			sleep(2.0)
			self.firstTime = False
		if self.isDataAvailable():
			result = self.dataset[:, self.readPointer]
		else:#No new data to read
			print("Wrong readPointer: %d or wrong dataLength: %d" %(self.readPointer, self.getDataLength()))
			raise IndexError('Array Out of Boundary Error!')
		
		ev = self.getExtraChannelValues(result)
		result.resize(result.size + len(ev))
		result[-len(ev):]=ev
		
		return result
	
	def toString(self):
		return self.getName() + ": Count=" + str(self.getPosition())

	#To artificially add extra channels of which value is a calculation of existing channels
	def getExtraChannelValues(self, d):
		if beamline_name == "i06-1":
			Id, I0, If, Ifft, Iffb = d[0], d[1], d[2], d[3], d[6] #C1, C2, C3, C4, and C5 see I06-344 for more info
	
			if I0 <= 0.001:
				I0 += 0.001
				
			idi0 = float(Id)/I0
			ifi0 = float(If)/I0
			ifi0ft = float(Ifft)/I0
			ifi0fb = float(Iffb)/I0
			
			return [idi0, ifi0, ifi0ft, ifi0fb]
		
		if beamline_name == "i06":
			Id, I0, If, Ifft, roi1, roi2 = d[0], d[1], d[2], d[3], d[6], d[7] #C1, C2, C3, C4, and ROI1 and ROI2, see I06-1021 for more info
	
			if I0 <= 0.001:
				I0 += 0.001
			if Id <= 0.001:
				Id += 0.001
				
			roi1i01 = float(roi1)/Id
			roi1i02 = float(roi1)/I0
			roi2i01 = float(roi2)/Id
			roi2i02 = float(roi2)/I0
			
			return [roi1i01, roi1i02, roi2i01, roi2i02]
		
	def readoutChannel(self, channelIndex):
		result = self.readout()
		return result[channelIndex-1]
