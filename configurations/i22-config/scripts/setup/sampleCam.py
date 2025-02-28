from uk.ac.gda.server.ncd.subdetector import NcdSubDetector
from gdascripts.utils import caput, caget
from gda.jython import InterfaceProvider
from gdaserver import ncddetectors

class AdCam(NcdSubDetector):
    """
    Wrapper around Epics AreaDetector to support inclusion in ncddetectors

    This allows non-standard detectors (eg visible light cameras) to be
    be included in data collections with hardware triggering (as opposed
    to single image per point).

    Example:
        >>> d12_cam = AdCam('d12_cam', d12gige)
        >>> ncddetectors.addDetector(d12_cam)
        >>> staticscan ncddetectors #  includes d12 in hardware triggered collection
    """
    def __init__(self, name, detector):
        """
        Create new detector wrapper using existing detector

        Args:
            name (str): The name of the detector. This will be the name that
                appears in the scan file.
            detector: The AreaDetector instance that should be wrapped. If the
                required detector does not exist within GDA, please contact
                GDA support.
        """
        self.setName(name)
        self.name = name
        self.setDetectorType("OTHER")
        self.detector = detector
        self.basePV = detector.getBasePVName()
        basePV = detector.getBasePVName()
        self.acquireImageCount = basePV + "CAM:NumImages"
        self.acquirePV = basePV + "CAM:Acquire"
        self.hdfImageCount = basePV + "HDF5:NumCapture"
        self.hdfStartAcquire = basePV + "HDF5:Capture"
        self.hdfFileName = basePV + "HDF5:FileTemplate"
        self.hdfCaptureMode = basePV + "HDF5:FileWriteMode"
        self.fileTemplate = "i22-%%d-%s.h5" %name

        self.extraDims = basePV + "HDF5:NumExtraDims"
        self.extraDimN = basePV + "HDF5:ExtraDimSizeN"
        self.extraDimX = basePV + "HDF5:ExtraDimSizeX"
        self.extraDimY = basePV + "HDF5:ExtraDimSizeY"

        self.thisFile = ""
    def atScanStart(self, info):

        frames = ncddetectors.getTimer().getFramesets().get(0).getFrameCount()

        scanNumber = info.getScanNumber()
        self.thisFile = "%s/%s" %(InterfaceProvider.getPathConstructor().createFromDefaultProperty(), self.fileTemplate %scanNumber)
        filename = [ord(x) for x in self.thisFile]+[0]

        self.detector.setTriggerMode(1) # External
        self.detector.setImageMode(1) # Multiple
        caput(self.hdfFileName, filename) #set hdf5 filename
        caput(self.hdfImageCount, frames) #set hdf5 frame count
        caput(self.extraDimN, frames)
        self._setDimensions(info)

        caput(self.acquireImageCount, caget(self.basePV + "HDF5:NumCapture_RBV"))#set camera frame count

        caput(self.hdfCaptureMode,2) #set camera capture mode to stream
        caput(self.hdfStartAcquire, 1) #set hdf5 to acquire
        caput(self.acquirePV, 1)#set camera to acquire

    def _setDimensions(self, currentScanInformation):
        dims = currentScanInformation.getDimensions()
        if len(dims) == 1:
            if dims[0] == 1:
                #single point no extra dimensions
                caput(self.extraDims, 0)
            else:
                #multiple points 1 extra 0dimension
                caput(self.extraDims, 1)
                caput(self.extraDimX, dims[0])
        elif len(dims) == 2:
            #2d scan - 2 extra dimensions
            caput(self.extraDims, 2)
            caput(self.extraDimX, dims[0])
            caput(self.extraDimY, dims[1])

    def atScanEnd(self):
        caput(self.acquirePV, 0)#set camera to not acquire
        caput(self.hdfStartAcquire, 0) #set hdf5 to not acquire
        caput(self.hdfCaptureMode,1) #set camera capture mode back to single

    def writeout(self, frames, dataTree):
        dataTree.addScanFileLink(self.getName(), "nxfile://" + self.thisFile + "#entry/instrument/detector/data")
        self.addMetadata(dataTree)

    def start(self):
        pass
    def stop(self):
        self.atScanEnd()
    def clear(self):
        pass

    def __eq__(self, other):
        return self.getDetector() == other.getDetector()


class AdOAVCam(NcdSubDetector):
    """
    Wrapper around Epics AreaDetector to support inclusion in ncddetectors

    This allows non-standard detectors (eg visible light cameras) to be
    be included in data collections with hardware triggering (as opposed
    to single image per point).

    Example:
        >>> d12_cam = AdCam('d12_cam', d12gige)
        >>> ncddetectors.addDetector(d12_cam)
        >>> staticscan ncddetectors #  includes d12 in hardware triggered collection
    """
    def __init__(self, name, detector):
        """
        Create new detector wrapper using existing detector

        Args:
            name (str): The name of the detector. This will be the name that
                appears in the scan file.
            detector: The AreaDetector instance that should be wrapped. If the
                required detector does not exist within GDA, please contact
                GDA support.
        """
        self.setName(name)
        self.setDetectorType("OTHER")
        self.detector = detector
        self.basePV = detector.getBasePVName()
        basePV = detector.getBasePVName()
        self.acquireImageCount = basePV + "NumImages"
        self.acquirePV = basePV + "Acquire"
        self.hdfImageCount = "BL22I-DI-OAV-01:HDF5:NumCapture"
        self.hdfStartAcquire = "BL22I-DI-OAV-01:HDF5:Capture"
        self.hdfFileName = "BL22I-DI-OAV-01:HDF5:FileTemplate"
        self.hdfCaptureMode = "BL22I-DI-OAV-01:HDF5:FileWriteMode"
        self.imageMode = "BL22I-DI-OAV-01:DET:ImageMode"

        self.fileTemplate = "i22-%%d-%s.h5" %name

        # BL22I-DI-OAV-01:HDF5:AutoSave = 1
        # BL22I-DI-OAV-01:HDF5:NumCapture = n
        # BL22I-DI-OAV-01:DET:NumImages
        # BL22I-DI-OAV-01:HDF5:Capture = 1
        # BL22I-DI-OAV-01:DET:Acquire = 1



        #self.extraDims = basePV + "BL22I-DI-OAV-01:HDF5:NumExtraDims"
        #self.extraDimN = basePV + "BL22I-DI-OAV-01:HDF5:ExtraDimSizeN"
        #self.extraDimX = basePV + "BL22I-DI-OAV-01:HDF5:ExtraDimSizeX"
        #self.extraDimY = basePV + "BL22I-DI-OAV-01:HDF5:ExtraDimSizeY"

        self.extraDims = "BL22I-DI-OAV-01:HDF5:NumExtraDims"
        self.extraDimN = "BL22I-DI-OAV-01:HDF5:ExtraDimSizeN"
        self.extraDimX = "BL22I-DI-OAV-01:HDF5:ExtraDimSizeX"
        self.extraDimY = "BL22I-DI-OAV-01:HDF5:ExtraDimSizeY"

        self.thisFile = ""
    def atScanStart(self, info):

        frames = ncddetectors.getTimer().getFramesets().get(0).getFrameCount()

        scanNumber = info.getScanNumber()
        self.thisFile = "%s/%s" %(InterfaceProvider.getPathConstructor().createFromDefaultProperty(), self.fileTemplate %scanNumber)
        filename = [ord(x) for x in self.thisFile]+[0]

        # self.detector.setTriggerMode(1) # External
        # self.detector.setImageMode(1) # Multiple
        caput(self.imageMode,1)
        caput(self.hdfFileName, filename) #set hdf5 filename
        caput(self.hdfImageCount, frames) #set hdf5 frame count
        caput(self.extraDimN, frames)
        self._setDimensions(info)

        caput(self.acquireImageCount, caget("BL22I-DI-OAV-01:HDF5:NumCapture_RBV"))#set camera frame count
        caput(self.hdfCaptureMode,2) #set camera capture mode to stream
        caput(self.hdfStartAcquire, 1) #set hdf5 to acquire
        caput(self.acquirePV, 1)#set camera to acquire


    def _setDimensions(self, currentScanInformation):
        dims = currentScanInformation.getDimensions()
        if len(dims) == 1:
            if dims[0] == 1:
                #single point no extra dimensions
                caput(self.extraDims, 0)
            else:
                #multiple points 1 extra 0dimension
                caput(self.extraDims, 1)
                caput(self.extraDimX, dims[0])
        elif len(dims) == 2:
            #2d scan - 2 extra dimensions
            caput(self.extraDims, 2)
            caput(self.extraDimX, dims[0])
            caput(self.extraDimY, dims[1])

    def atScanEnd(self):
        caput(self.acquirePV, 0)#set camera to not acquire
        # caput(self.hdfStartAcquire, 0) #set hdf5 to not acquire
        # caput(self.hdfFileWriteMode, 0)
        # self.detector.setImageMode(2) # continuous
        #
        caput(self.hdfStartAcquire, 0) #set hdf5 to not acquire
        caput(self.hdfCaptureMode,2) #set camera capture mode back to single
        ######

        detectorPVprefix = 'BL22I-DI-OAV-01'

        caput(detectorPVprefix + ':DET:TriggerMode', 'Off')
        caput(detectorPVprefix + ':DET:ImageMode', 'Continuous')
        caput(detectorPVprefix + ':DET:TriggerSource', 'Freerun')

        # Then TRS
        caput(detectorPVprefix + ':TRS:NDArrayPort', 'OAVC.cam')
        caput(detectorPVprefix + ':TRS:EnableCallbacks', 'Enable')
        caput(detectorPVprefix + ':TRS:Type', 'Mirror')

        # Then OVER
        caput(detectorPVprefix + ':OVER:NDArrayPort', 'OAVC.trs')
        caput(detectorPVprefix + ':OVER:EnableCallbacks', 'Enable')

        # Then ARR
        caput(detectorPVprefix + ':ARR:NDArrayPort', 'OAVC.over')
        caput(detectorPVprefix + ':ARR:EnableCallbacks', 'Enable')

        # Then HDF
        caput(detectorPVprefix + ':HDF5:NDArrayPort', 'OAVC.over')
        caput(detectorPVprefix + ':HDF5:EnableCallbacks', 'Enable')

        # And finally, MJPG
        caput(detectorPVprefix + ':MJPG:NDArrayPort', 'OAVC.over')
        caput(detectorPVprefix + ':MJPG:EnableCallbacks', 'Enable')

        # Turn back on acquisition!
        caput(detectorPVprefix + ':DET:Acquire', '1')




    def writeout(self, frames, dataTree):
        dataTree.addScanFileLink(self.getName(), "nxfile://" + self.thisFile + "#entry/instrument/detector/data")
        # dataTree.addScanFileLink(self.getName(), "nxfile://" + self.thisFile + "#entry/data/data")
        self.addMetadata(dataTree)

    def start(self):
        pass
    def stop(self):
        self.atScanEnd()
    def clear(self):
        pass

    def __eq__(self, other):
        return self.getDetector() == other.getDetector()

if __name__ == "__main__":
    pass
    #sampleCam = adCam("sampleCam", d11gige, "BL22I-DI-PHDGN-11:")
    #  ncddetectors.addDetector(sampleCam)
