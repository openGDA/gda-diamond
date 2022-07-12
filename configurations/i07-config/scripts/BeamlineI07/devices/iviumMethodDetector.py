from gda.device.detector.addetector.filewriter import MultipleImagesPerHDF5FileWriter
from gda.device.detector.areadetector.v17.impl import NDFileHDF5Impl, NDPluginBaseImpl, NDFileImpl
from gda.device.detector import NXDetectorData


class IviumMethodRunner(DetectorBase):


    def __init__(self, name, fileWriter, methodScannable):
        self.setName(name)
        self.setExtraNames(["datapath"])
        self.setOutputFormat(["%s"])
        self.setInputNames([])
        self.fileWriter = fileWriter
        self.methodScannable = methodScannable
        self.lastReadout = None

    def collectData(self):
        self.lastReadout = None
        self.methodScannable.asynchronousMoveTo(None)
        while not self.methodScannable.isBusy():
            sleep(1)

        self.fileWriter.prepareForCollection(1, None)



    def isBusy(self):
        return self.fileWriter.getNdFileHDF5().getCapture_RBV() == 1

    def getStatus(self):
        return 0

    def readout(self):
        if self.lastReadout == None:
            data = self.fileWriter.read(10)
            self.lastReadout = NXDetectorData(["datapath"], ["%s"], "ivium")
            data.get(0).appendTo(self.lastReadout, "iviumMethod")
        return self.lastReadout

    def createsOwnFiles(self):
        return True

    def atScanEnd(self):
        self.fileWriter.completeCollection()

    def runMethodBlocking(self):
        staticscan(self)

    def runMethodNonBlocking(self):
        self.collectData()



iviumNdFilePb = NDPluginBaseImpl()
iviumNdFilePb.setBasePVName("BL07I-EA-IVIUM-01:HDF:")
iviumNdFilePb.setInitialArrayPort("CompactStat.Port")
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


fWriter = MultipleImagesPerHDF5FileWriter()
fWriter.setNdFileHDF5(iviumNdFileHdf)
fWriter.setFileTemplate("%s%s-%d.hdf5")
fWriter.setFilePathTemplate("$datadir$")
fWriter.setFileNameTemplate("ivium-method")
fWriter.setFileNumberAtScanStart(-1)
fWriter.setSetFileNameAndNumber(True)
fWriter.afterPropertiesSet()
#fWriter.configure()

iviumMethod = IviumMethodRunner("iviumMethod", fWriter, iviumMethodS)

