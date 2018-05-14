from gdascripts.scan.concurrentScanWrapper import ConcurrentScanWrapper
from gda.device.detector.xmap.edxd.EDXDController import COLLECTION_MODES
from gda.device.detector.xmap.edxd.EDXDController import PRESET_TYPES
from gda.epics import CAClient
import time

class EnergyStepScan(ConcurrentScanWrapper):

    def __init__(self,idEnergy,xmap,scanListeners = None):
        ConcurrentScanWrapper.__init__(self, returnToStart=False, relativeScan=False, scanListeners=scanListeners)
        self.xmap = xmap
        self.idEnergy = idEnergy

    def __call__(self, *args):
        self.PrepareForCollection()
        ConcurrentScanWrapper.__call__(self,args)

    def setROI1(self,energyStart,energyEnd):
        windowStart = self.getROIEnergy(energyStart)
        self.xmap.getController().getEdxdController().getSubDetector(0).setLowROIs([windowStart])
        windowEnd = self.getROIEnergy(energyEnd)
        self.xmap.getController().getEdxdController().getSubDetector(0).setHighROIs([windowEnd])

    def PrepareForCollection(self):
        self.xmap.getController().getEdxdController().setCollectionMode(COLLECTION_MODES.MCA_MAPPING)
        self.xmap.getController().getEdxdController().setIgnoreGate(True)
        time.sleep(1)
        self.xmap.getController().getEdxdController().setCollectionMode(COLLECTION_MODES.MCA_SPECTRA)
        self.xmap.getController().getEdxdController().setPresetType(PRESET_TYPES.REAL_TIME)

    def convertArgStruct(self, argStruct):
        return argStruct

    def getROIEnergy(self,energy):
        energyBinWidth = float(CAClient().get("BL08I-EA-DET-02:DXP1:MCABinWidth_RBV"))
        return int(energy/energyBinWidth)
