from time import sleep
from datetime import datetime as ivium_datetime
from gda.device.monitor import EpicsMonitor
from gda.device.enumpositioner import EpicsSimpleMbbinary
from gda.device.scannable import ScannableMotionBase


class EpicsDeviceClass(ScannableBase):
	def __init__(self, name, pvSet, pvGet, pvStatus, strUnit, strFormat, timeout=None):
		self.setName(name);
		self.setInputNames([name]);
		self.Units=[strUnit];
		self.setOutputFormat([strFormat]);
		
		self.delay=1;
		self.timeout = timeout;

		self.setupEpics(pvSet, pvGet, pvStatus);

	def __del__(self):
		self.cleanChannel(self.chSet);
		self.cleanChannel(self.chGet);
		if self.chStatus:
			self.cleanChannel(self.chStatus);
	
	def setupEpics(self, pvSet, pvGet, pvStatus):
#		Epics PVs for checking fast scan readiness:
		self.chSet=CAClient(pvSet);  self.configChannel(self.chSet);
		self.chGet=CAClient(pvGet);  self.configChannel(self.chGet);

		if pvStatus:
			self.chStatus = CAClient(pvStatus);	self.configChannel(self.chStatus);
		else:
			self.chStatus = None;
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();
	
	def setDelay(self, newDelay):
		self.delay = newDelay;
	
	def setTimeout(self, newTimeout):
		self.timeout = newTimeout;

	def caget(self):
		try:
			result = float(self.chGet.caget())
		except:
			print "Error getting position"
		return result;

	def caput(self, new_position):
		try:
			if self.timeout is None:
				self.chSet.caput(new_position);
			else:
				self.chSet.caput(new_position, self.timeout);
		except:
			print "Error setting position"
			
	def getPosition(self):
		return self.caget();

	def asynchronousMoveTo(self, new_position):
		self.currentposition = new_position;
		self.caput(new_position);

		sleep(self.delay);

	def getStatus(self):
		status=0;
		try:
			if self.chStatus:
				status = int(float(self.chStatus.caget()));
		except:
			print "Error getting status"
		if status == 1:
			return EpicsDevicStatus.DEVICE_STATUS_IDLE;
		if status ==0:
			return EpicsDevicStatus.DEVICE_STATUS_BUSY;


	def isBusy(self):
		if self.chStatus is None:#No status pv provided, so no status feedback necessary
			return False;
		
		if self.getStatus() == EpicsDevicStatus.DEVICE_STATUS_IDLE:#It's done
			return False;
		else:
			return True;




class IviumPotentiastat:
    """A potentiostat class for the Ivium CompactStat (one channel)"""
    def __init__(self, pvStem):
        self.pvStem = pvStem

        
    def setMethodMode(self):
        for i in [1]:
            caput(self.pvStem+"PORT"+str(i)+":OperatingMode",1) #Method
            caput(self.pvStem+"PORT"+str(i)+":ImageMode",1) #Multiple
            caputS(self.pvStem+"HDF"+":FileTemplate","%s%s.hdf")
            sleep(0.1)
            caput(self.pvStem+"HDF"+":EnableCallbacks",1)
            caput(self.pvStem+"HDF"+":FileWriteMode",2)
            caput(self.pvStem+"HDF"+":LazyOpen",1)
            
    def setDirectMode(self):
        for i in [1]:
            caput(self.pvStem+"PORT"+str(i)+":OperatingMode",0) #Direct
            caput(self.pvStem+"PORT"+str(i)+":ImageMode",2) #Continuous
            caputS(self.pvStem+"HDF"+":FileTemplate","%s%s.hdf")
            sleep(0.1)
            caput(self.pvStem+"HDF"+":EnableCallbacks",1)
            caput(self.pvStem+"HDF"+":FileWriteMode",2)
            caput(self.pvStem+"HDF"+":LazyOpen",1)
            caput(self.pvStem+"PORT"+str(1)+":Acquire",1)
            
    def setMethodPath(self,path="/IviumStat/datafiles/"):
        for i in [1]:
            caputS(self.pvStem+"PORT"+str(i)+":MethodDirectory",path)
            
    def setMethodFilename(self,filename):
        """Takes the filename of the method to run (with or without the .imf extension)"""
        if filename[-4:] != ".imf":
            filename = filename+".imf"
        for i in [1]:
            caputS(self.pvStem+"PORT"+str(i)+":MethodFileName",filename)
    
    def setHdfPath(self,path=None):
        """Sets the file path for the HDF file containing the eChem data.
        
        Defaults to the current visit directory /processed/eChem"""
        if path == None:
            path = InterfaceProvider.getPathConstructor().getVisitDirectory() + "/ivium/"
            if not os.path.exists(path): os.makedirs(path)
        caputS(self.pvStem+"HDF"+":FilePath",path)
            
    def setHdfFilename(self,filename):
        """Sets the filename for the HDF file containing the eChem data.
        
        Automatically appends the channel number to the name given"""
        caputS(self.pvStem+"HDF"+":FileName",filename+"_ch{}".format(i))
    
    def primeHdfWriter(self):
        caput(self.pvStem+"HDF"+":Capture",1)
        _waitFor(self.pvStem+"HDF:Capture_RBV",1,checkTime=.1,timeOut=5)
    
    def stopAcquiring(self):
        caput(self.pvStem+"PORT"+str(1)+":Acquire",0)

    def startAcquiring(self):
        caput(self.pvStem+"PORT"+str(1)+":Acquire",1)

    def startMethod(self):
        for i in [1]:
            caput(self.pvStem+"PORT"+str(i)+":Acquire",1)
            
    def stopMethod(self):
        for i in [1]:
            caput(self.pvStem+"PORT"+str(i)+":Acquire",0)
        caput(self.pvStem+"HDF"+":Capture",0)
        
    def runMethod(self,methodFilePath):
        self.setMethodMode()
        filename = os.path.basename(methodFilePath)
        filepath = os.path.dirname(methodFilePath)+"/"
        if filename[-4:] != ".imf":
            filename = filename+".imf"
        self.setMethodPath(filepath)
        self.setMethodFilename(filename)
        self.setHdfPath()
        hdfFileName = filename[:-4]
        hdfFileName = hdfFileName+"_"+ivium_datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.setHdfFilename(hdfFileName)
        self.primeHdfWriter()
        self.startMethod()
        print "ivium method {} started".format(filename)

    def setCellMode(self, mode):
        caput(self.pvStem+"PORT"+str(1)+":CellConnection", mode)
        caput(self.pvStem+"PORT"+str(1)+":Apply",1)
            
    def cellOff(self):
        self.setCellMode(0)
        
    def applyCurrent(self, current):
        self.setDirectMode()
        sleep(0.1)
        caput(self.pvStem+"PORT"+str(1)+":AppliedCurrent",current)
        caput(self.pvStem+"PORT"+str(1)+":Apply",1)
        
    def applyVoltage(self, voltage):
        self.setDirectMode()
        sleep(0.1)
        caput(self.pvStem+"PORT"+str(1)+":AppliedPotential",voltage)
        caput(self.pvStem+"PORT"+str(1)+":Apply",1)
        
    def isAcquiring(self):
        return caget(self.pvStem+"PORT"+str(1)+":Acquire") == str(1)
        
ivium = IviumPotentiastat(pvStem="BL07I-EA-IVIUM-01:")

    
def caputS(pv,string):
    ustring = map(ord,string+u"\u0000")
    caput(pv,ustring)
    
def _waitFor(pv,value,checkTime=0.5,timeOut=30,logger=None):
     i = 0
     timeOut = int(float(timeOut) / float(checkTime))
     sleep(float(checkTime))
     while str(caget(pv)) != str(value):
         sleep(float(checkTime))
         i += 1
         if i > timeOut:
             raise Exception("waitFor timed out while waiting for "+ str(pv) + " to change to " + str(value))
    
    
    #eChemMethodCh1_V,eChemMethodCh1_I, eChemMethodCh2_V, eChemMethodCh2_I, eChemMethodCh3_V, eChemMethodCh3_I, eChemMethodCh4_V, eChemMethodCh4_I, eChemMethodCh5_V, eChemMethodCh5_I, eChemMethodCh6_V, eChemMethodCh6_I, eChemMethodCh7_V, eChemMethodCh7_I, eChemMethodCh8_V, eChemMethodCh8_I    


class IviumEpicsMonitor(EpicsMonitor):
        
    def setController(self, controller):
        self.controller = controller
    
    def getPosition(self):
        if not self.isConfigured():
            self.configure()
        if not self.controller.isAcquiring():
            self.controller.setDirectMode()
        return super(IviumEpicsMonitor, self).getPosition()
    
    
    
    
class ScannableIvium(EpicsDeviceClass):
    def __init__(self, name, basePV):
        self.setName(name)
        
        pvAppliedCurrent = '%s:PORT1:AppliedCurrent' %(basePV)
        pvAppliedCurrentRBV  = '%s:PORT1:AppliedCurrent_RBV' %(basePV)
        pvAppliedPotential = '%s:PORT1:AppliedPotential' %(basePV)
        pvAppliedPotentialRBV  = '%s:PORT1:AppliedPotential_RBV' %(basePV)
        pvStartStopAcquire = '%s:PORT1:Acquire' %(basePV)
        pvMeasuredPotentialRBV  = '%s:CHAN1:MeasuredPotential_RBV' %(basePV)
        pvMeasuredCurrentRBV  = '%s:CHAN1:MeasuredCurrent_RBV' %(basePV)
        pvCellMode = '%s:PORT1:CellConnection' %(basePV)
        pvApply = '%s:PORT1:Apply' %(basePV)
        format = '%.6f'
        units = "A"
        self.acquire = CAClient(pvStartStopAcquire)
        self.apply = CAClient(pvApply)
        self.acquire.configure()
        self.apply.configure()
        EpicsDeviceClass.__init__(self,name,pvAppliedPotential,pvAppliedPotential,None,units,format,timeout=None)
        
        self.setInputNames(['Potential'])
        self.setExtraNames(["MeasuredPotential","MeasuredCurrent"])
        
        self.mpr = CAClient(pvMeasuredPotentialRBV)
        self.mpr.configure()
        self.mcr = CAClient(pvMeasuredCurrentRBV)
        self.mcr.configure()
        self.pcb = CAClient(pvAppliedPotentialRBV)
        self.pcb.configure()
        self.cm = CAClient(pvCellMode)
        self.cm.configure()
        self.setDelay(0.5)
        
    def asynchronousMoveTo(self, new_position):
        self.currentposition = new_position;
        self.caput(new_position);
        self.apply.caput(1)
        sleep(1);
        
        
    def atScanStart(self):
        self.acquire.caput(1) 
        sleep(self.delay)
        
    def atScanEnd(self):
        self.acquire.caput(0)
        sleep(self.delay)
        
    def getPosition(self):
        self.acquire.caput(1)
        sleep(1);
        vals = float(self.pcb.caget()),float(self.mpr.caget()),float(self.mcr.caget())
        self.acquire.caput(0)
        return vals


class IviumMethodScannable(ScannableBase):
    def __init__(self, name, pvBase):
        self.pvBase = pvBase
        self.setName(name)
        self.setExtraNames([])
	self.setInputNames([])
        self.setOutputFormat([])

    def asynchronousMoveTo(self, position):
	# start method
        caput(self.pvBase + ":PORT1:StartMethod", 1)


    def isBusy(self):
        """
        [ 0] No IviumSoft
        [ 1] Not Connected
        [ 2] Available Idle
        [ 3] Available Busy
        """
        state = caget(self.pvBase + ":CHAN1:DeviceStatus_RBV")
        return state != "2"

    def stop(self):
        caput(self.pvBase + ":PORT1:StopMethod", 1)

    def getPosition(self):
        return None


iviumPotential = IviumEpicsMonitor()
iviumPotential.setController(ivium)
iviumPotential.setPvName("BL07I-EA-IVIUM-01:CHAN1:MeasuredPotential_RBV")
iviumPotential.setName("iviumPotential")

iviumCurrent = IviumEpicsMonitor()
iviumCurrent.setController(ivium)
iviumCurrent.setPvName("BL07I-EA-IVIUM-01:CHAN1:MeasuredCurrent_RBV")
iviumCurrent.setName("iviumCurrent")

iviumRange = EpicsSimpleMbbinary()
iviumRange.setName("iviumRange")
iviumRange.setRecordName("BL07I-EA-IVIUM-01:PORT1:CurrentRange")
iviumRange.configure()
iviumRange.setReadOnly(False)


iviumStatus = EpicsSimpleMbbinary()
iviumStatus.setName("iviumStatus")
iviumStatus.setRecordName("BL07I-EA-IVIUM-01:CHAN1:DeviceStatus_RBV")
iviumStatus.configure()
iviumStatus.setReadOnly(True)

iviumMethodS = IviumMethodScannable("iviumMethod", "BL07I-EA-IVIUM-01")
iviumMethodS.configure()
iviumMethodS.setLevel(100)

ivium1 = ScannableIvium("ivium1", "BL07I-EA-IVIUM-01")
    
"""
NOTES ON OPERATION IN DIRECT MODE
1. Changes to applied current/voltage are only taken into account when the PORT is Stopped and Started again
2. When Cell Mode is set to Potential or Current,  is the live Voltage reading and LastCollectionY_RBV is the live Current reading
"""

# Method detector

from gda.device.detector.addetector.filewriter import MultipleImagesPerHDF5FileWriter
from gda.device.detector.areadetector.v17.impl import NDFileHDF5Impl, NDPluginBaseImpl, NDFileImpl
from gda.device.detector import NXDetectorData
from gda.device.detector import NexusDetector

from org.eclipse.scanning.api.device import AbstractRunnableDevice
from uk.ac.diamond.osgi.services import ServiceProvider
from org.eclipse.scanning.api.device import IRunnableDeviceService
from uk.ac.diamond.daq.detectors.addetector.api import AreaDetectorRunnableDeviceModel
from org.eclipse.dawnsci.nexus import NexusNodeFactory
from org.eclipse.dawnsci.nexus.builder import NexusObjectWrapper
from org.eclipse.dawnsci.nexus import INexusDevice
from org.eclipse.january.dataset import LazyWriteableDataset
from org.eclipse.january.dataset import DatasetFactory
from org.eclipse.january.dataset import SliceND
from java.lang import Double

import os.path
from os.path import exists
import re


class IviumMethodRunner(AbstractRunnableDevice, INexusDevice):


    def __init__(self, name, fileWriter, methodScannable, pathInDatafile="#entry/instrument/detector/data"):
        super(IviumMethodRunner, self).__init__(ServiceProvider.getService(IRunnableDeviceService))
        self.fileWriter = fileWriter
        self.lastReadout = None
        self.pathInDatafile = pathInDatafile
        self.methodScannable = methodScannable
        model = AreaDetectorRunnableDeviceModel()
        model.setName(name)
        self.setName(name)
        self.setModel(model)
        self.register()
        self.dNames = {"x": "x", "y": "y", "z": "z"}

    def run(self, position):
        self.lastReadout = None
        self.fileWriter.prepareForCollection(1, None)
        self.startRunningMethod()
        self.fileWriter.read(1)


        fName = self.fileWriter.getNdFileHDF5().getFullFileName_RBV()
        #self.lastReadout = NXDetectorDataWithFilepathForSrs(self)
        #self.lastReadout.addExternalFileLink(self.getName(), "data", "nxfile://" + fName + self.pathInDatafile, 3);
        #self.lastReadout.addFileName(self.getName(), os.path.basename(fName))
        while (iviumStatus.getPosition() != "Available Idle") and (not exists(fName)):
        	sleep(0.2)

        ds = dnp.io.load(fName)["entry"]['instrument']['detector']['data']
        x = ds[0, :, 0]
        y = ds[0, :, 1]
        z = ds[0, :, 2]

        self.xDataset.setSlice(None, x._jdataset(), SliceND(x.shape))
        self.yDataset.setSlice(None, y._jdataset(), SliceND(y.shape))
        self.zDataset.setSlice(None, z._jdataset(), SliceND(z.shape))

        # TODO need to call this at failure too
        self.fileWriter.completeCollection()


    def startRunningMethod(self):
        # TODO need to set to method mode
        # TODO need to set the scanning timeout/ask Matt how to do it properly
        ivium.startAcquiring()
        self.methodScannable.asynchronousMoveTo(None)


    def getNexusProvider(self, info):
    	
    	scanFileName = os.path.basename(os.path.splitext(info.getFilePath())[0]) # without extension
    	scanNumber = re.findall("\d+$", scanFileName)[0]
    	self.fileWriter.setScanNumber(scanNumber)

        nxDet = NexusNodeFactory.createNXdetector();
        wrapper = NexusObjectWrapper("ivium", nxDet);

        self.xDataset = LazyWriteableDataset(self.dNames["x"], Double, [0], [-1], None, None)
        self.yDataset = LazyWriteableDataset(self.dNames["y"], Double, [0], [-1], None, None)
        self.zDataset = LazyWriteableDataset(self.dNames["z"], Double, [0], [-1], None, None)


        wrapper.getNexusObject().createDataNode(self.dNames["x"], self.xDataset);
        wrapper.getNexusObject().createDataNode(self.dNames["y"], self.yDataset);
        wrapper.getNexusObject().createDataNode(self.dNames["z"], self.zDataset);

        wrapper.addAxisDataFieldNames(self.dNames["x"], self.dNames["y"], self.dNames["z"]);
        wrapper.setPrimaryDataFieldName(self.dNames["x"])
        wrapper.addAdditionalPrimaryDataFieldName(self.dNames["y"])
        wrapper.addAdditionalPrimaryDataFieldName(self.dNames["z"])
        return wrapper

    #def isBusy(self):
        #return self.fileWriter.getNdFileHDF5().getCapture_RBV() == 1

    def runMethodBlocking(self):
        mscan(static, 1, self, 1)

    #def runMethodNonBlocking(self):
    #REDO
     #   self.collectData()

    #def stop(self):
    #REDO
     #   self.fileWriter.completeCollection()


    def runMethod(self):
        self.runMethodBlocking()

    def runMethodAsync(self):
        self.startRunningMethod()
        print("Method running in background")


class CustomScanNumberFileWriter(MultipleImagesPerHDF5FileWriter):

	def __init__(self):
		self.thisScanNumber = None
	
	def getScanNumber(self):
		return self.thisScanNumber
	
	
	def setScanNumber(self, scanNumber):
		self.thisScanNumber = int(scanNumber)


iviumNdFilePb = NDPluginBaseImpl()
iviumNdFilePb.setBasePVName("BL07I-EA-IVIUM-01:HDF:")
iviumNdFilePb.setInitialArrayPort("ADSIM.CAM")
iviumNdFilePb.afterPropertiesSet()

iviumNdFile = NDFileImpl()
iviumNdFile.setBasePVName("BL07I-EA-IVIUM-01:HDF:")
iviumNdFile.setPluginBase(iviumNdFilePb)
iviumNdFile.setInitialWriteMode(0)
iviumNdFile.setInitialNumCapture(1)
iviumNdFile.setInitialFileName("ivium-method")
iviumNdFile.setInitialFileTemplate("%s%s.hdf5")
iviumNdFile.afterPropertiesSet()

iviumNdFileHdf = NDFileHDF5Impl()
iviumNdFileHdf.setFile(iviumNdFile)
iviumNdFileHdf.setBasePVName("BL07I-EA-IVIUM-01:HDF:")
iviumNdFileHdf.afterPropertiesSet()
#iviumNdFileHdf.configure()


fWriter = CustomScanNumberFileWriter()
fWriter.setNdFileHDF5(iviumNdFileHdf)
fWriter.setFileTemplate("%s%s-%d.hdf5")
fWriter.setFilePathTemplate("$datadir$")
fWriter.setFileNameTemplate("ivium-method")
fWriter.setFileNumberAtScanStart(-1)
fWriter.setLazyOpen(True)
fWriter.setSetFileNameAndNumber(True)
fWriter.afterPropertiesSet()
#fWriter.configure()

iviumMethod = IviumMethodRunner("iviumMethod", fWriter, iviumMethodS)

print "Ivium scripts loaded"
