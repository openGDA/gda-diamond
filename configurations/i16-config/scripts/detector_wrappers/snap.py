from time import sleep
from gda.device import DetectorSnapper
from gda.device.detector import DetectorBase
from org.eclipse.january.dataset import DatasetFactory
from uk.ac.diamond.scisoft.analysis import SDAPlotter
import scisoftpy as dnp

'''
I16 has a requirement to be able to take a single image from a detector, display it and calculate stats quickly and 
without saving the image.  This is no longer provided by the pos command as this is not supported by gda, so this script
has been added based on i07's ct.py script.
'''
class AdDetSnapper(DetectorSnapper, DetectorBase):

    def __init__(self, name, ad_base, nd_array, statsProcessor, plotName):
        self.setName(name)
        self.adBase = ad_base
        self.nd_array = nd_array
        self.statsProc = statsProcessor
        self.setInputNames([])
        self.setExtraNames(self.statsProc.getExtraNames())
        self.setOutputFormat(self.statsProc.getOutputFormat())
        self.currentStats = None
        self.plotName = plotName
        self.last_dataset = None

    def acquire(self):
        self.adBase.startAcquiring()
        while self.nd_array.getPluginBase().getArrayCounter_RBV() != 1:
            sleep(0.1)
        height = self.nd_array.getPluginBase().getArraySize0_RBV(); width = self.nd_array.getPluginBase().getArraySize1_RBV()
        image_data = self.nd_array.getImageData(height * width)
        dataset = DatasetFactory.createFromObject(image_data, width, height)
        SDAPlotter.imagePlot(self.plotName, dataset)
        self.currentStats = self.statsProc.process(self.getName(), "", dataset)
        self.last_dataset = dnp.reshape(image_data, [width, height])
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

from gdaserver import merlin, merlin_stats, pil3_100k, pilatus3_stats

mdet = merlin.getDetector()
merlin_snap_viewer = AdDetSnapper("merlin_snap_viewer", mdet.getCollectionStrategy().getAdBase(), mdet.getAdditionalPluginList()[1].getNdArray(), merlin_stats, "Merlin")
merlin_snap_viewer.array_port = "mpx2.cam"

pildet = pil3_100k.getDetector()
pil_snap_viewer = AdDetSnapper("pil_snap_viewer", pildet.getCollectionStrategy().getAdBase(), pildet.getAdditionalPluginList()[2].getNdArray(), pilatus3_stats, "Pilatus")
pil_snap_viewer.array_port = "PILATUS3.cam"

def snap(detector, count_time = 1):
    if detector == merlin :
        det = merlin_snap_viewer
    elif detector == pil3_100k :
        det = pil_snap_viewer
    else :
        det = detector
    pos(det, count_time)

from gda.jython.commands.GeneralCommands import alias 
alias("snap")