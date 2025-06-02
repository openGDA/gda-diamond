from time import sleep

from gda.device import DetectorSnapper
from gda.device.detector import DetectorBase
from org.eclipse.january.dataset import DatasetFactory
from uk.ac.diamond.scisoft.analysis import SDAPlotter


class AdDetSnapper(DetectorSnapper, DetectorBase):

    def __init__(self, name, ad_base, nd_array, statsProcessor, plotName, mask):
        self.setName(name)
        self.adBase = ad_base
        self.nd_array = nd_array
        self.statsProc = statsProcessor
        self.setInputNames([])
        self.setExtraNames(self.statsProc.getExtraNames())
        self.setOutputFormat(self.statsProc.getOutputFormat())
        self.currentStats = None
        self.plotName = plotName
        self.mask = mask

    def acquire(self):
        self.adBase.startAcquiring()
        while self.nd_array.getPluginBase().getArrayCounter_RBV() != 1:
            sleep(0.1)
        height = self.nd_array.getPluginBase().getArraySize0_RBV(); width = self.nd_array.getPluginBase().getArraySize1_RBV()
        imageData = DatasetFactory.createFromObject(self.nd_array.getImageData(height * width), width, height)
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
        self.nd_array.getPluginBase().setDroppedArrays(0);
        self.nd_array.getPluginBase().setArrayCounter(0);
        self.nd_array.getPluginBase().setNDArrayPort(self.array_port);
        self.nd_array.getPluginBase().enableCallbacks()
        self.currentStats = None

from gdaserver import p2r, p2_mask, pilatus2_stats_verbose, p3r, p3_mask, pilatus3_stats_verbose

p2_ad_base = p2r.getDetector().getCollectionStrategy().getDecoratee().getDecoratee().getDecoratee().getAdBase()
p2_snap = AdDetSnapper("p2_snap", p2_ad_base, p2r.getDetector().getNdArray(), pilatus2_stats_verbose, "Pilatus 2", p2_mask)
p2_snap.array_port = "pilatus2.CAM"
p3_ad_base = p3r.getDetector().getCollectionStrategy().getDecoratee().getDecoratee().getDecoratee().getAdBase()
p3_snap = AdDetSnapper("p3_snap", p3_ad_base, p3r.getDetector().getNdArray(), pilatus3_stats_verbose, "Pilatus 3", p3_mask)
p3_snap.array_port = "pilatus3.CAM"

