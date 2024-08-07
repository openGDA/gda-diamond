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
        self.setDetectorType("OTHER")
        self.detector = detector
        self.basePV = detector.getBasePVName()
        basePV = detector.getBasePVName()
        self.acquireImageCount = basePV + "CAM:NumImages"
        self.acquirePV = basePV + "CAM:Acquire"
        self.hdfImageCount = basePV + "HDF5:NumCapture"
        self.hdfStartAcquire = basePV + "HDF5:Capture"
        self.hdfFileName = basePV + "HDF5:FileTemplate"
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

if __name__ == "__main__":
    pass
    #sampleCam = adCam("sampleCam", d11gige, "BL22I-DI-PHDGN-11:")
  #  ncddetectors.addDetector(sampleCam)
