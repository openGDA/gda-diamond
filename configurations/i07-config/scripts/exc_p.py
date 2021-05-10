from gda.device import DetectorSnapper
from gda.device.detector import DetectorBase
from uk.ac.diamond.scisoft.analysis import SDAPlotter
from time import sleep
from gdascripts.utils import caget, caput


"""Temporary script for testing extra Excalibur functionality"""

class ExcPvaSnapper(DetectorSnapper, DetectorBase):

    def __init__(self, name, collectionStrategy, pvaPlugin, statsProcessor):
        self.setName(name)
        self.collectionStrategy = collectionStrategy
        self.adBase = self.collectionStrategy.getDecoratee().getDecoratee().getDecoratee().getAdBase()
        self.pvaPlugin = pvaPlugin
        self.statsProc = statsProcessor
        self.setInputNames([])
        self.setExtraNames(self.statsProc.getExtraNames())
        self.setOutputFormat(self.statsProc.getOutputFormat())
        self.currentStats = None

    def acquire(self):
        #self.collectionStrategy
        self.adBase.startAcquiring()
        while self.pvaPlugin.getPluginBase().getArrayCounter_RBV() != 1:
            sleep(0.1)
        imageData = self.pvaPlugin.getImageDataset()
        SDAPlotter.imagePlot("Area Detector", imageData)
        # Acquire
        # Get image
        self.currentStats = self.statsProc.process(self.getName(), "", imageData)
        caput("BL07I-EA-EXCBR-01:CAM:ContinuePolling", 1)
        # Plot and print
        return [""]

    def getAcquirePeriod(self):
        return 0.0

    def atCommandFailure(self):
        print("Command failure called")
        pass

    def waitWhileBusy(self):
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
        pass

    def prepareForAcquisition(self, collectionTime):
        caput("BL07I-EA-EXCBR-01:CAM:PausePolling", 1)
        self.adBase.setAcquireTime(collectionTime)
        self.adBase.setImageMode(0)
        self.adBase.setTriggerMode(0)
        self.pvaPlugin.getPluginBase().setDroppedArrays(0);
        self.pvaPlugin.getPluginBase().setArrayCounter(0);
        self.currentStats = None

# exc_pva.getAdditionalPluginList()[0].getNdPva()
#exc_pva.getCollectionStrategy().getDecoratee().getDecoratee().getDecoratee().getAdBase()
