#from gda.device.detector.areadetector.v17 import NDfile, ADBaseImpl
from org.slf4j import LoggerFactory
from time import sleep
from uk.ac.diamond.daq.detectors.addetector import AbstractAreaDetectorRunnableDeviceDelegate
from gdascripts.utils import caget, caput #Necessary?
import os
from org.eclipse.dawnsci.nexus import NXdetector
from org.eclipse.dawnsci.nexus import NexusNodeFactory

class PeAdTest (AbstractAreaDetectorRunnableDeviceDelegate):
    logger = LoggerFactory.getLogger("PeAdTest");
    #sleepTime = 0.1 # Used to slow everything down so we can see what it is doing

    #def __init__(self):
    #    self.adBase = self.getRunnableDeviceProxy().getDetector().getAdBase()
    #    self.ndFile = self.getRunnableDeviceProxy().getDetector().getNdFile()

    def waitFor(self,pv,value,checkTime=0.5,timeOut=30):
        """MBB: to use this do:
            self.waitForAd("BL15J-EA-DET-01:HDF5:Capture",0,checkTime=1.,timeOut=30.)
        """
        i = 0
        timeOut = int(float(timeOut) / float(checkTime))
        sleep(float(checkTime))
        while str(caget(pv)) != str(value):
            sleep(float(checkTime))
            i += 1
            if i > timeOut:
                raise NameError("waitFor timed out while waiting for "+ str(pv) + " to change to " + str(value)) 

    def preConfigure(self, info):
        self.logger.info("preConfigure({})", info)
        
        #self.adBase = self.getRunnableDeviceProxy().getDetector().getAdBase()
        #self.ndFile = self.getRunnableDeviceProxy().getDetector().getNdFile()
        self.hdfPlugin = "HDF5:"
        
        """caput method"""
        caput("BL15J-EA-DET-01:PROC1:EnableCallbacks",0)
        caput("BL15J-EA-DET-01:PROC3:EnableCallbacks",0)
        if caget("BL15J-EA-DET-01:HDF5:Capture") != "0":
            caput("BL15J-EA-DET-01:HDF5:Capture",0)
            self.waitFor("BL15J-EA-DET-01:HDF5:Capture",0,checkTime=1.,timeOut=30.)
            self.logger.info("preConfigure({})", "File writer found to be busy. Waiting for file writer to reset...")

        """GDA method"""
        #if self.ndFile.getCapture() != 0:
        #    self.ndFile.stopCapture()
        #    sleep(1)
        # Disable PROC3 callbacks
        #self.adBase.getIntBySuffix("PROC3:EnableCallbacks");
        #self.adBase.setIntBySuffix("PROC3:EnableCallbacks",0);
        #self.adBase.getDoubleBySuffix("...:...");
        #self.adBase.getStringBySuffix("...:...");
        #sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.preConfigure(self, info);

    def configure(self, model):
        self.logger.info("configure({})", model)
        # Configure accumulating proc with the exposure time
        
        self.model = model
        
        acquirePeriod = float(caget("BL15J-EA-ZEBRA-02:DIV1_DIV"))/1000
        caput("BL15J-EA-DET-01:CAM:AcquirePeriod",acquirePeriod)
        exposureTime = model.getExposureTime()
        caput("BL15J-EA-DET-01:CAM:AcquireTime",exposureTime)
        
        if (exposureTime % acquirePeriod) < 1e-10:
            acquisitions = int(exposureTime / acquirePeriod)
            caput("BL15J-EA-DET-01:PROC1:NumFilter",acquisitions)
            caput("BL15J-EA-DET-01:PROC3:NumFilter",acquisitions)
        else:
            raise Exception("exposureTime time must be a multiple of the acquire period, currently "+str(acquirePeriod)+" s")
    
        #sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.configure(self, model)

    def postConfigure(self, info):
        self.logger.info("postConfigure({})", info)
        
        nexusFilePath = info.getFilePath()
        visitDir = os.path.dirname(nexusFilePath) # Get visit dir from nexus file
        scanPrefix = os.path.basename(nexusFilePath).replace(".nxs","")
        self.fileName = scanPrefix+"_"+ self.getRunnableDeviceProxy().getName() +".hdf5"
        #self.adBase.setStringBySuffix(self.hdfPlugin+"FileTemplate", "%s%s")
        uTemplate = map(ord,"%s%s"+u"\u0000")
        caput("BL15J-EA-DET-01:"+self.hdfPlugin+"FileTemplate",uTemplate)
        
        #self.adBase.setStringBySuffix(self.hdfPlugin+"FilePath", visitDir)
        uDir = map(ord,visitDir+u"\u0000")
        caput("BL15J-EA-DET-01:HDF5:FilePath",uDir)
        
        #self.adBase.setStringBySuffix(self.hdfPlugin+"FileName", self.fileName)
        uFile = map(ord,self.fileName+u"\u0000")
        caput("BL15J-EA-DET-01:HDF5:FileName",uFile)
        
        
        """caput method"""
        caput("BL15J-EA-DET-01:HDF5:NumCapture",info.getSize())
        
        """GDA method"""
        #self.getRunnableDeviceProxy().getDetector().getNdFile().setNumCapture(info.getSize())
        #sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.postConfigure(self, info);

    def getNexusProvider(self, info):
        self.logger.info("getNexusProvider({})", info);
        #sleep(1)
        
        """ Playing with NexusNodeFactory
        #nxSample = NexusNodeFactory.createNXsample()
        #nxInstrument = NexusNodeFactory.createNXinstrument()
        #nxMonitor = NexusNodeFactory.createNXmonitor()
        #sampleStageCollection = NexusNodeFactory.createNXcollection()
        nxMonitor = NexusNodeFactory.createNXmonitor()
        """
        
        ##final NXdetector nxDetector = NexusNodeFactory.createNXdetector();
        nxDetector = NexusNodeFactory.createNXdetector()

        ##nxDetector.setCount_timeScalar(model.getExposureTime());
        nxDetector.setCount_timeScalar(self.model.getExposureTime())

        ##// The link is relative and relies on the AD file and the NeXus being in the same directory
        ##nxDetector.addExternalLink(NXdetector.NX_DATA, fileName, PATH_TO_DATA_NODE);
        nxDetector.addExternalLink(NXdetector.NX_DATA, self.fileName, "/entry/instrument/detector/data")

        ##// Add the link for the total
        ##nxDetector.addExternalLink(FIELD_NAME_STATS_TOTAL, fileName, PATH_TO_STATS_TOTAL_NODE);
        nxDetector.addExternalLink("total", self.fileName, "/entry/instrument/NDAttributes/StatsTotal")
        
        """ Playing with nxDetector
        #nxDetector.setAttribute(null, "signal", "data");
        nxDetector.setX_pixel_sizeScalar(0.1);
        nxDetector.setAttribute(nxDetector.NX_X_PIXEL_SIZE, "units", "um");
        #nxDetector.setY_pixel_sizeScalar(0.1);
        #nxDetector.setAttribute(NXdetector.NX_Y_PIXEL_SIZE, "units", "um");
        """
        
        ##// Get the NexusOjbectWrapper wrapping the detector
        ##NexusObjectWrapper<NXdetector> nexusObjectWrapper = new NexusObjectWrapper<NXdetector>(
        ##        getName(), nxDetector);
        nexusObjectWrapper = self.getNexusObjectWrapper(self.getRunnableDeviceProxy().getName(), nxDetector)

        """
        nexusMonObjectWrapper = self.getNexusObjectWrapper(self.getRunnableDeviceProxy().getName(), nxMonitor)
        nexusMonObjectWrapper.addAdditionalPrimaryDataFieldName("totallyMonitorMon")
        """

        ##int scanRank = scanInfo.getRank();
        scanRank = info.getRank()

        ##// Set the external file written by this detector which will be linked to
        ##nexusObjectWrapper.setDefaultExternalFileName(fileName);
        nexusObjectWrapper.setDefaultExternalFileName(self.fileName)

        ##// Setup the primary NXdata. Add 2 to the scan rank as AD returns 2D data
        ##nexusObjectWrapper.setPrimaryDataFieldName(NXdetector.NX_DATA);
        nexusObjectWrapper.setPrimaryDataFieldName(NXdetector.NX_DATA)
        ##nexusObjectWrapper.setExternalDatasetRank(NXdetector.NX_DATA, scanRank + 2);
        nexusObjectWrapper.setExternalDatasetRank(NXdetector.NX_DATA, scanRank + 2)

        ##// Add an additional NXData for the stats total. This is also scanRank + 2 as AD writes [y,x,1,1]
        ##nexusObjectWrapper.addAdditionalPrimaryDataFieldName(FIELD_NAME_STATS_TOTAL);
        nexusObjectWrapper.addAdditionalPrimaryDataFieldName("total")
        ##nexusObjectWrapper.setExternalDatasetRank(FIELD_NAME_STATS_TOTAL, scanRank + 2);
        nexusObjectWrapper.setExternalDatasetRank("total", scanRank + 2)

        ##return nexusObjectWrapper;
        self.logger.info("...getNexusProvider returning {}", nexusObjectWrapper);
        return nexusObjectWrapper #, nexusMonObjectWrapper

        #return AbstractAreaDetectorRunnableDeviceDelegate.getNexusProvider(self, info)
        #sleep(sleepTime)

    def scanStart(self, info):
        self.logger.info("scanStart({})", info)
        self.logger.info("scanStart({})", info.getFilePath())
        
        """caput method"""
        """
        linuxFullPath =  info.getFilePath()
        winFullPath = "x:"+linuxFullPath[15:].replace("/","\\")
        winDir = winFullPath[:18]
        winFile = winFullPath[18:]
        winFile = winFile[:-4]+"-pe1AD"
        uDir = map(ord,winDir+u"\u0000")
        #caput("BL15J-EA-DET-01:HDF5:FilePath",uDir)
        uFile = map(ord,winFile+u"\u0000")
        caput("BL15J-EA-DET-01:HDF5:FileName",uFile)
        """
        caput("BL15J-EA-DET-01:HDF5:Capture",1)
        
        """ MBB: See my scanStart function in peAdTest-MBB.py
        
        converttoInternal() is the tried and trusted way to convert unix paths to windows paths.
        
        Also, self.adBase.setStringBySuffix() is much easier to use for strings than caput. You will need to
        uncomment this classes __init__ function to use that though.
        """
        
        
        # This is the first place we have a filename, but how do we set it?
        #getRunnableDeviceProxy().getDetector().getNdFile().stopCapture()
        #sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.scanStart(self, info);

    def pointStart(self, point):
        self.logger.info("pointStart({})", point)
        
        #sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.pointStart(self, point);

    def levelStart(self, info):
        self.logger.info("levelStart({})", info)
        
        #sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.levelStart(self, info);

    def run(self, position):
        self.logger.info("run({})", position);
        
        acquirePeriod = float(caget("BL15J-EA-DET-01:CAM:AcquirePeriod"))
        exposureTime = float(caget("BL15J-EA-DET-01:CAM:AcquireTime"))
        acquisitions = int(float(exposureTime) / float(acquirePeriod))
        nextFrame = int(caget("BL15J-EA-DET-01:CAM:ArrayCounter_RBV"))+1
        
        self.logger.info("run({})", "Waiting for next frame...")
        self.waitFor("BL15J-EA-DET-01:CAM:ArrayCounter_RBV",nextFrame,checkTime=acquirePeriod/10.,timeOut=acquirePeriod*2.)
        
        self.logger.info("run({})", "Starting collection...")
        caput("BL15J-EA-DET-01:PROC1:ResetFilter",1)
        caput("BL15J-EA-DET-01:PROC3:ResetFilter",1)
        caput("BL15J-EA-DET-01:HDF5:EnableCallbacks",1)
        nextArrayCounter = int(caget("BL15J-EA-DET-01:PROC3:ArrayCounter_RBV")) + acquisitions
        nextFileCounter = int(caget("BL15J-EA-DET-01:HDF5:NumCaptured_RBV")) + 1
        caput("BL15J-EA-DET-01:PROC1:EnableCallbacks","1")
        caput("BL15J-EA-DET-01:PROC3:EnableCallbacks","1")
        
        self.logger.info("run({})", "Waiting for next array to be collected...")
        self.waitFor("BL15J-EA-DET-01:PROC3:ArrayCounter_RBV",nextArrayCounter,checkTime=acquirePeriod/10.,timeOut=exposureTime*3.)
        self.logger.info("run({})", "Array collected...")
        caput("BL15J-EA-DET-01:PROC1:EnableCallbacks","0")
        
        self.logger.info("run({})", "Waiting for next array to be written...")
        self.waitFor("BL15J-EA-DET-01:HDF5:NumCaptured_RBV",nextFileCounter,checkTime=exposureTime/10.,timeOut=exposureTime*3.+2.)
        self.logger.info("run({})", "Array written...")
        
        caput("BL15J-EA-DET-01:HDF5:EnableCallbacks","0")
        
        caput("BL15J-EA-DET-01:PROC1:NumFilter","1")
        caput("BL15J-EA-DET-01:PROC1:ResetFilter","1")
        caput("BL15J-EA-DET-01:PROC1:EnableCallbacks","1")
        
        #sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.run(self, position)

    def levelEnd(self, info):
        self.logger.info("levelEnd({})", info)
        #sleep(1)
        AbstractAreaDetectorRunnableDeviceDelegate.levelEnd(self, info);

    # levelStart again

    # levelEnd again, simultaneous with:

    def write(self, position):
        self.logger.info("write({})", position);
        #sleep(1)
        return AbstractAreaDetectorRunnableDeviceDelegate.write(self, position);

    def pointEnd(self, point):
        self.logger.info("pointEnd({})", point)
        #sleep(1)
        AbstractAreaDetectorRunnableDeviceDelegate.pointEnd(self, point);

    def scanFinally(self, info):
        self.logger.info("scanFinally({})", info)
        #sleep(1)
        AbstractAreaDetectorRunnableDeviceDelegate.scanFinally(self, info);

    def scanEnd(self, info):
        self.logger.info("scanEnd({})", info)
        #sleep(1)
        AbstractAreaDetectorRunnableDeviceDelegate.scanEnd(self, info);

    # Not called in a normal scan

    def scanAbort(self, info):
        self.logger.info("scanAbort({})", info)
        #sleep(1)
        AbstractAreaDetectorRunnableDeviceDelegate.scanAbort(self, info);

    def scanFault(self, info):
        self.logger.info("scanFault({})", info)
        #sleep(1)
        AbstractAreaDetectorRunnableDeviceDelegate.scanFault(self, info);

    def scanPause(self):
        self.logger.info("scanPause()")
        #sleep(1)
        AbstractAreaDetectorRunnableDeviceDelegate.scanPause(self);

    def scanResume(self):
        self.logger.info("scanResume()")
        #sleep(1)
        AbstractAreaDetectorRunnableDeviceDelegate.scanResume(self);
