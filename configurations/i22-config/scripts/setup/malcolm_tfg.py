from uk.ac.gda.server.ncd.actions import NcdAction
from gda.device.detector.areadetector.v17.impl import NDPluginBaseImpl

# image mode as int
MULTIPLE = 1
# trigger mode as int
EXT_ENABLE = 1

class NcdPilatusReset(NcdAction):
    def __init__(self, detector):
        self.det = detector.controller
    def run(self):
        self.det.imageMode = MULTIPLE
        self.det.triggerMode = EXT_ENABLE

        self.det.codec.pluginBase.NDArrayPort = self.det.areaDetector.getPortName_RBV()

        self.det.HDF5.arrayPort = self.det.codec.pluginBase.getPortName_RBV()
        self.det.HDF5.compression = "Blosc"
        self.det.HDF5.predefinedPositionMode = False
        self.det.HDF5.layoutFileName = ""

class NcdTetrammReset(NcdAction):
    def __init__(self, detector):
        self.det = detector.controller
    def run(self):
        self.det.fileWriter.arrayPort = self.det.portName
        self.det.fileWriter.file.setFileWriteMode(2)
        self.det.fileWriter.file.pluginBase.NDArrayAddress = 11
        self.det.fileWriter.layoutFileName = ""
        self.det.fileWriter.predefinedPositionMode = False

