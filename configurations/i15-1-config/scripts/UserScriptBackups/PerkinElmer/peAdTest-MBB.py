from gda.device.detector.areadetector.v17 import NDfile, ADBaseImpl
from org.slf4j import LoggerFactory
"""
import org.eclipse.dawnsci.nexus.NXdetector;
import org.eclipse.dawnsci.nexus.NexusNodeFactory;
"""
from time import sleep
from uk.ac.diamond.daq.detectors.addetector import AbstractAreaDetectorRunnableDeviceDelegate

class PeAdTest (AbstractAreaDetectorRunnableDeviceDelegate):
    logger = LoggerFactory.getLogger("PeAdTest");
    sleepTime = 1 # Used to slow everything down so we can see what it is doing

    def __init__(self):
        self.adBase = self.getRunnableDeviceProxy().getDetector().getAdBase()
        self.ndFile = self.getRunnableDeviceProxy().getDetector().getNdFile()

    def preConfigure(self, info):
        self.logger.info("preConfigure({})", info)

        # From detSetupStream()
        ##currentScanNumber = NumTracker("i15-1").getCurrentFileNumber()
        # Don't need this as we will get it from the nexus file name later.

        ##caput(detPVs[det]+"PROC3:EnableCallbacks",0)
        self.adBase.setIntBySuffix("PROC3:EnableCallbacks",0);

        ##if dark == False:
        ##    hdfPlugin = "HDF5:"
        ##else:
        ##    hdfPlugin = "HDF5B:"
        self.hdfPlugin = "HDF5:"

        ##if caget(detPVs[det]+hdfPlugin+"Capture") != "0": #If file writer is not idle, reset it
        ##    caput(detPVs[det]+hdfPlugin+"Capture",0)
        ##    sleep(1) #Required if the file-writer already has data in it
        if self.adBase.getIntBySuffix(self.hdfPlugin+"Capture") != 0:
            self.adBase.setIntBySuffix(self.hdfPlugin+"Capture", 0)
            sleep(1)

        ##caput(detPVs[det]+hdfPlugin+"NumCapture",repeats)
        self.adBase.setIntBySuffix(self.hdfPlugin+"NumCapture", info.getSize())

        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.preConfigure(self, info);

    def configure(self, model):
        self.logger.info("configure({})", model)
        # Configure accumulating proc with the exposure time

        # From detCollection()
        ##acquireTime = detGetAcquireTime(det)
        self.acquireTime = float(caget(detZebraTimePVs[det]))/1000.
        ##caput(detPVs[det]+"CAM:AcquireTime",exposure)
        self.exposureTime = model.getExposureTime()
        self.adBase.setDoubleBySuffix("CAM:AcquireTime", self.exposureTime)
        # Note that AquireTime is ignored with TriggerMode External on the PE detector
        #      so this is used to 

        ##if (exposure % acquireTime) < 1e-10:
        ##    acquisitions = int(exposure / acquireTime)
        ##    print "Setting up "+str(acquisitions)+" x "+str(acquireTime)+" second acquisition"
        ##    ##setup the collection
        ##    caput(detPVs[det]+"PROC1:NumFilter",acquisitions)
        ##    caput(detPVs[det]+"PROC3:NumFilter",acquisitions)
        ##    detWaitForNewAcquisition(det)
        ##    detGrabFrameToStream(det,dark,acquisitions)
        ##    print "...collection complete!"
        ##    detRestoreAfterCollect(det)
        ##else:
        ##    raise Exception("exposure time must be a multiple of the acquire time, currently "+str(acquireTime)+" s")

        """
        self.model= model
        self.fileName = ?

        # This means we need to know the scan number before postConfigure
        
            // FIXME This only handles raster type scans (not snake) and ones in a line square or cube.
            // Think the solution is to use the POS plugin to tell AD in advance where the frames are going
            int[] scanShape = information.getShape();
            switch (information.getRank()) {
            case 1: // 1D Scan
                ndFileHDF5.setNumExtraDims(0); // 1D scan so no extra dims
                ndFileHDF5.setNumCapture(scanShape[0]);
                break;
            case 2: // 2D Scan (like a map)
                ndFileHDF5.setNumExtraDims(1); // 1D scan so no extra dims
                ndFileHDF5.setExtraDimSizeN(scanShape[1]);
                ndFileHDF5.setExtraDimSizeX(scanShape[0]);
                break;
            case 3: // 3D Scan (like a map at multiple temperatures)
                ndFileHDF5.setNumExtraDims(2); // 1D scan so no extra dims
                ndFileHDF5.setExtraDimSizeN(scanShape[2]);
                ndFileHDF5.setExtraDimSizeX(scanShape[1]);
                ndFileHDF5.setExtraDimSizeY(scanShape[0]);
                break;
            default:
                throw new DeviceException(
                        "Area Detector can't handle file writing when scan is >3D. Scan dimensions = " + scanShape.length);
            }
        """

        if (self.exposureTime % self.acquireTime) < 1e-10:
            acquisitions = int(self.exposureTime / self.acquireTime)
            self.logger.info("Setting up {} x {}  second acquisition", acquisitions, self.acquireTime)
            ##setup the collection
            self.adBase.setIntBySuffix("PROC1:NumFilter",acquisitions)
            self.adBase.setIntBySuffix("PROC3:NumFilter",acquisitions)
            # The rest happens later
        else:
            raise Exception("exposure time must be a multiple of the acquire time, currently "+str(self.acquireTime)+" s")

        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.configure(self, model)

    def postConfigure(self, info):
        self.logger.info("postConfigure({})", info)
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.postConfigure(self, info);

    def getNexusProvider(self, info):
        self.logger.info("getNexusProvider({}) returning None", info);
        
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

        ##// Get the NexusOjbectWrapper wrapping the detector
        ##NexusObjectWrapper<NXdetector> nexusObjectWrapper = new NexusObjectWrapper<NXdetector>(
        ##        getName(), nxDetector);
        nexusObjectWrapper = getNexusObjectWrapper(getName(), nxDetector)

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
        return nexusObjectWrapper
"""
        
        sleep(sleepTime)
        return AbstractAreaDetectorRunnableDeviceDelegate.getNexusProvider(self, info)

    def scanStart(self, info):
        self.logger.info("scanStart({})", info)

        # This is the first place we have a filename for now (MG will hopefully get his set earlier)

        nexusFilePath = info.getFilePath()
        visitDir = os.path.dirname(nexusFilePath) # Get visit dir from nexus file

        windowsDir = pe1AD.getNdFile().getFilePathConverter().converttoInternal(visitDir)

        self.adBase.setStringBySuffix(self.hdfPlugin+"FileTemplate", "%s%s.h5")
        self.adBase.setStringBySuffix(self.hdfPlugin+"FilePath", windowsDir)

        # Use the nexus filename as a base for
        scanPrefix = os.path.basename(nexusFilePath).replace(".nxs","")

        # From detSetupStream()
        ##caputS(detPVs[det]+hdfPlugin+"FileName",det+"_"+str(currentScanNumber)+str(filename))
        self.adBase.setStringBySuffix(self.hdfPlugin+"FileName", scanPrefix+"_"+ self.getRunnableDeviceProxy().getName())
        ##caput(detPVs[det]+hdfPlugin+"Capture",1)
        self.adBase.setIntBySuffix(self.hdfPlugin+"Capture", 1)

        #getRunnableDeviceProxy().getDetector().getNdFile().stopCapture()

        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.scanStart(self, info);

    def pointStart(self, point):
        self.logger.info("pointStart({})", point)
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.pointStart(self, point);

    def levelStart(self, info):
        self.logger.info("levelStart({})", info)
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.levelStart(self, info);

    def run(self, position):
        self.logger.info("run({})", position);

        sleep(sleepTime)

        # From detCollection()
        ##    detWaitForNewAcquisition(det)
        ##    detGrabFrameToStream(det,dark,acquisitions)
        ##    print "...collection complete!"
        ##    detRestoreAfterCollect(det)

        # From detWaitForNewAcquisition()
        ##acquireTime = detGetAcquireTime(det)
        # Already in self.acquireTime
        ##nextFrame = int(caget(detPVs[det]+"CAM:ArrayCounter_RBV"))+1
        nextFrame = self.adBase.getIntBySuffix("CAM:ArrayCounter_RBV")+1

        ##print "Waiting for next new acquisition..."
        self.logger.info("Waiting for next new acquisition... {}", nextFrame);

        ##waitFor(detPVs[det]+"CAM:ArrayCounter_RBV",nextFrame,checkTime=acquireTime/10.,timeOut=acquireTime*2.)
        waitFor("CAM:ArrayCounter_RBV", nextFrame, checkTime=self.acquireTime/10., timeOut=self.acquireTime*2.)

        ##print "...ready to collect data!"
        self.logger.info("...ready to collect data!");

        ###waitFor(detPVs[det]+"CAM:ArrayCounter_RBV",nextFrame+1,checkTime=0.1,timeOut=acquireTime*2.)

        # From detGrabFrameToStream()

        ##if dark == False:
        ##    hdfPlugin = "HDF5:"
        ##else:
        ##    caput(detPVs[det]+"PROC2:EnableBackground","0") #For file writing
        ##    hdfPlugin = "HDF5B:"
        ##acquireTime = detGetAcquireTime(det)
        # Already in self.acquireTime
        ##exposure = float(caget("BL15J-EA-DET-01:CAM:AcquireTime"))
        # Already in self.exposureTime

        ##caput(detPVs[det]+"PROC1:EnableCallbacks","0")
        ##caput(detPVs[det]+"PROC3:EnableCallbacks","0")
        ##caput(detPVs[det]+"PROC1:ResetFilter","1")
        ##caput(detPVs[det]+"PROC3:ResetFilter","1")
        ##caput(detPVs[det]+hdfPlugin+"EnableCallbacks","1")
        self.adBase.setIntBySuffix("PROC1:EnableCallbacks",0)
        self.adBase.setIntBySuffix("PROC3:EnableCallbacks",0)
        self.adBase.setIntBySuffix("PROC1:ResetFilter",1)
        self.adBase.setIntBySuffix("PROC3:ResetFilter",1)
        self.adBase.setIntBySuffix(self.hdfPlugin+":EnableCallbacks",1)

        ##nextArrayCounter = int(caget(detPVs[det]+"PROC3:ArrayCounter_RBV")) + acquisitions
        ##nextFileCounter = int(caget(detPVs[det]+hdfPlugin+"NumCaptured_RBV")) + 1
        acquisitions = self.adBase.getIntBySuffix("PROC1:NumFilter")
        nextArrayCounter = self.adBase.getIntBySuffix("PROC3:ArrayCounter_RBV") + acquisitions
        nextFileCounter = self.adBase.getIntBySuffix(self.hdfPlugin+"NumCaptured_RBV") + 1

        ##caput(detPVs[det]+"PROC1:EnableCallbacks","1")
        ##caput(detPVs[det]+"PROC3:EnableCallbacks","1")
        self.adBase.setIntBySuffix("PROC1:EnableCallbacks",1)
        self.adBase.setIntBySuffix("PROC3:EnableCallbacks",1)

        ##waitFor(detPVs[det]+"PROC3:ArrayCounter_RBV",nextArrayCounter,checkTime=acquireTime/10.,timeOut=exposure*3.)
        waitFor("PROC3:ArrayCounter_RBV", nextArrayCounter,checkTime=self.acquireTime/10.,timeOut=self.exposureTime*3.)
        ##caput(detPVs[det]+"PROC1:EnableCallbacks","0")
        self.adBase.setIntBySuffix("PROC1:EnableCallbacks",0)
        ##waitFor(detPVs[det]+hdfPlugin+"NumCaptured_RBV",nextFileCounter,checkTime=exposure/10.,timeOut=exposure*3.+2.)
        waitFor(self.hdfPlugin+"NumCaptured_RBV", nextFileCounter,checkTime=self.exposureTime/10.,timeOut=self.exposureTime*3.)
        ##caput(detPVs[det]+hdfPlugin+"EnableCallbacks","0")
        self.adBase.setIntBySuffix(self.hdfPlugin+":EnableCallbacks",0)

        ##if dark == True:
        ##    caput("BL15J-EA-DET-01:PROC2:SaveBackground","1")
        ##    caput("BL15J-EA-DET-01:PROC2:EnableBackground","1")

        AbstractAreaDetectorRunnableDeviceDelegate.run(self, position)

    def waitFor(suffix,value,checkTime=0.5,timeOut=30):
        i = 0
        timeOut = int(float(timeOut) / float(checkTime))
        sleep(float(checkTime))
        while str(self.adBase.getIntBySuffix(suffix)) != str(value):
            sleep(float(checkTime))
            i += 1
            if i > timeOut:
                raise NameError("waitFor timed out while waiting for "+ str(suffix) + " to change to " + str(value))

    def levelEnd(self, info):
        self.logger.info("levelEnd({})", info)
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.levelEnd(self, info);

    # levelStart again

    # levelEnd again, simultaneous with:

    def write(self, position):
        self.logger.info("write({})", position);
        sleep(sleepTime)
        return AbstractAreaDetectorRunnableDeviceDelegate.write(self, position);

    def pointEnd(self, point):
        self.logger.info("pointEnd({})", point)
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.pointEnd(self, point);

    def scanFinally(self, info):
        self.logger.info("scanFinally({})", info)
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.scanFinally(self, info);

    def scanEnd(self, info):
        self.logger.info("scanEnd({})", info)
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.scanEnd(self, info);

    # Not called in a normal scan

    def scanAbort(self, info):
        self.logger.info("scanAbort({})", info)
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.scanAbort(self, info);

    def scanFault(self, info):
        self.logger.info("scanFault({})", info)
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.scanFault(self, info);

    def scanPause(self):
        self.logger.info("scanPause()")
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.scanPause(self);

    def scanResume(self):
        self.logger.info("scanResume()")
        sleep(sleepTime)
        AbstractAreaDetectorRunnableDeviceDelegate.scanResume(self);
