from uk.ac.gda.server.ncd.subdetector import NcdSubDetector
from gda.jython import InterfaceProvider
from gda.data import PathConstructor

class adCam(NcdSubDetector):
    def __init__(self, name, detector, basePV="BL22I-DI-PHDGN-11:"):
        self.setName(name)
        self.setDetectorType("OTHER")
        self.detector = detector
        self.basePV = basePV
        self.acquireImageCount = basePV + "CAM:NumImages"
        self.acquirePV = basePV + "CAM:Acquire"
        self.hdfImageCount = basePV + "HDF5:NumCapture"
        self.hdfStartAcquire = basePV + "HDF5:Capture"
        self.hdfFileName = basePV + "HDF5:FileTemplate"#BL22I-DI-PHDGN-11:HDF5:FileTemplate
        self.fileTemplate = "i22-%%d-%s.h5" %name

        self.extraDims = basePV + "HDF5:NumExtraDims"#BL22I-DI-PHDGN-11:HDF5:NumExtraDims
        self.extraDimN = basePV + "HDF5:ExtraDimSizeN"
        self.extraDimX = basePV + "HDF5:ExtraDimSizeX"
        self.extraDimY = basePV + "HDF5:ExtraDimSizeY"

        #self.dataDir = PathConstructor.createFromDefaultProperty()
        self.thisFile = ""
    def atScanStart(self):
        csih = InterfaceProvider.getCurrentScanInformationHolder()
        csc = csih.getCurrentScanInformation()
        
        frames = ncddetectors.getTimer().getFramesets().get(0).getFrameCount()
        
        scanNumber = csc.getScanNumber()
        self.thisFile = "%s/%s" %(PathConstructor.createFromDefaultProperty(), self.fileTemplate %scanNumber)
        filename = [ord(x) for x in self.thisFile]+[0]
        
        caput(self.hdfFileName, filename) #set hdf5 filename
        caput(self.hdfImageCount, frames) #set hdf5 frame count
        caput(self.extraDimN, frames)
        self._setDimensions(csc) 
        
        caput(self.acquireImageCount, caget("BL22I-DI-PHDGN-11:HDF5:NumCapture_RBV"))#set camera frame count

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
    sampleCam = adCam("sampleCam", d11gige, "BL22I-DI-PHDGN-11:")
    ncddetectors.addDetector(sampleCam)
