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

    def __init__(self, name, ad_base, nd_array, statsProcessor, plotName, array_port):
        self.setName(name)
        self.adBase = ad_base
        self.nd_array = nd_array
        self.statsProc = statsProcessor
        self.setInputNames([])
        self.setExtraNames(self.statsProc.getExtraNames())
        self.setOutputFormat(self.statsProc.getOutputFormat())
        self.currentStats = None
        self.plotName = plotName
        self.array_port = array_port
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

from gdaserver import merlin, merlin_stats, pil3_100k, pilatus3_stats, pil2M, pilatus2_stats, cam1, cam1_stats, cam2, cam2_stats, camd3, camd3_stats, camd4, camd4_stats, camd5, camd5_stats

mdet = merlin.getDetector()
merlin_snap_viewer = AdDetSnapper("merlin_snap_viewer", mdet.getCollectionStrategy().getAdBase(), mdet.getAdditionalPluginList()[1].getNdArray(), merlin_stats, "Merlin", "mpx2.cam")

pildet = pil3_100k.getDetector()
pil_snap_viewer = AdDetSnapper("pil_snap_viewer", pildet.getCollectionStrategy().getAdBase(), pildet.getAdditionalPluginList()[2].getNdArray(), pilatus3_stats, "Pilatus", "PILATUS3.cam")

pil2det = pil2M.getDetector()
pil2_snap_viewer = AdDetSnapper("pil2_snap_viewer", pil2det.getCollectionStrategy().getAdBase(), pil2det.getAdditionalPluginList()[2].getNdArray(), pilatus2_stats, "Pilatus", "PILATUS2.CAM")

cam1det = cam1.getDetector()
cam1_snap_viewer = AdDetSnapper("cam1_snap_viewer", cam1det.getCollectionStrategy().getAdBase(), cam1det.getAdditionalPluginList()[2].getNdArray(), cam1_stats, "CAM1", "CAM01.CAM")

cam2det = cam2.getDetector()
cam2_snap_viewer = AdDetSnapper("cam2_snap_viewer", cam2det.getCollectionStrategy().getAdBase(), cam2det.getAdditionalPluginList()[2].getNdArray(), cam2_stats, "CAM2", "CORCAM.CAM")

camd3det = camd3.getDetector()
camd3_snap_viewer = AdDetSnapper("camd3_snap_viewer", camd3det.getCollectionStrategy().getAdBase(), camd3det.getAdditionalPluginList()[2].getNdArray(), camd3_stats, "CAMD3", "D3CAM.CAM")

camd4det = camd4.getDetector()
camd4_snap_viewer = AdDetSnapper("camd4_snap_viewer", camd4det.getCollectionStrategy().getAdBase(), camd4det.getAdditionalPluginList()[2].getNdArray(), camd4_stats, "CAMD4", "D4CAM.CAM")

camd5det = camd5.getDetector()
camd5_snap_viewer = AdDetSnapper("camd5_snap_viewer", camd5det.getCollectionStrategy().getAdBase(), camd5det.getAdditionalPluginList()[2].getNdArray(), camd5_stats, "CAMD5", "D5CAM.CAM")

detectors_by_name = {"merlin" : merlin_snap_viewer, "pil3_100k" : pil_snap_viewer, "pil2M" : pil2_snap_viewer, "cam1" : cam1_snap_viewer, "cam2" : cam2_snap_viewer, "camd3" : camd3_snap_viewer,
                    "camd4" : camd4_snap_viewer, "camd5" : camd5_snap_viewer}

def snap(detector, count_time = 1):
    if detector.getName() in detectors_by_name :
        det = detectors_by_name[detector.getName()]
    else :
        det = detector

    pos(det, count_time)

from gda.jython.commands.GeneralCommands import alias
alias("snap")