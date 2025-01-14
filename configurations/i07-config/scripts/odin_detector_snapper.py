from gda.device import DetectorSnapper
from gda.device.detector import DetectorBase
from uk.ac.diamond.scisoft.analysis import SDAPlotter
from time import sleep
from gdascripts.utils import caput
from org.eclipse.january.dataset import DatasetFactory

"""Required for ct 'scan' for Odin detectors."""

class OdinPvaSnapper(DetectorSnapper, DetectorBase):

    def __init__(self, name, collectionStrategy, pvaPlugin, statsProcessor, plotName, mask):
        self.setName(name)
        self.collectionStrategy = collectionStrategy
        self.adBase = self.collectionStrategy.getDecoratee().getDecoratee().getDecoratee().getAdBase()
        self.pvaPlugin = pvaPlugin
        self.statsProc = statsProcessor
        self.setInputNames([])
        self.setExtraNames(self.statsProc.getExtraNames())
        self.setOutputFormat(self.statsProc.getOutputFormat())
        self.currentStats = None
        self.plotName = plotName
        self.mask = mask

    def acquire(self):
        self.adBase.startAcquiring()
        while self.pvaPlugin.getPluginBase().getArrayCounter_RBV() != 1:
            sleep(0.1)
        imageData = DatasetFactory.createFromObject(self.pvaPlugin.getImageObject(), self.pvaPlugin.getHeight(), self.pvaPlugin.getWidth())
        maskedImageData = self.mask.createDataSet(imageData)
        SDAPlotter.imagePlot(self.plotName, maskedImageData)
        self.currentStats = self.statsProc.process(self.getName(), "", maskedImageData)
        return [""]

    def getAcquirePeriod(self):
        return 0.0

    def atCommandFailure(self):
        print("Command failure called")

    def waitWhileBusy(self):
        'Should never wait'
        pass

    def readout(self):
        return self.currentStats.getDoubleVals()

    def createsOwnFiles(self):
        return False

    def getStatus(self):
        return 0

    def getAcquireTime(self):
        return 0.0

    def collectData(self):
        'Collection not managed by this object.'
        pass

    def prepareForAcquisition(self, collectionTime):
        self.adBase.setAcquireTime(collectionTime)
        self.adBase.setImageMode(0)
        self.adBase.setTriggerMode(0)
        self.adBase.setNumImages(1)
        self.pvaPlugin.getPluginBase().setDroppedArrays(0);
        self.pvaPlugin.getPluginBase().setArrayCounter(0);
        self.currentStats = None


class ExcPvaSnapper(OdinPvaSnapper):

    def acquire(self):
        return_val = OdinPvaSnapper.acquire(self)
        caput("BL07I-EA-EXCBR-01:CAM:ContinuePolling", 1)
        return return_val

    def prepareForAcquisition(self, collectionTime):
        caput("BL07I-EA-EXCBR-01:CAM:PausePolling", 1)
        OdinPvaSnapper.prepareForAcquisition(self, collectionTime)

class EigPvaSnapper(OdinPvaSnapper):

    def prepareForAcquisition(self, collectionTime):
        OdinPvaSnapper.prepareForAcquisition(self, collectionTime)
        caput("BL07I-EA-EIGER-01:CAM:ManualTrigger", 0)

    def acquire(self):
        return_val = OdinPvaSnapper.acquire(self)
        caput("BL07I-EA-EIGER-01:CAM:ManualTrigger", 1)
        caput("BL07I-EA-EIGER-01:CAM:Acquire", 0)
        return return_val