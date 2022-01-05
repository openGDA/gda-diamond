from gda.device import DetectorSnapper
from Diamond.Analysis.Analyser import AnalyserDetectorClass
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass

class AnalyserNxDetectorClass(AnalyserDetectorClass, DetectorSnapper):

    def __init__(self, name, detector, detector_for_snaps, processors=[], panelName="Area Detector", iFileLoader=None):
        AnalyserDetectorClass.__init__(self, name, detector, processors, panelName, iFileLoader)
        self.detector_for_snaps = detector_for_snaps

    def prepareForAcquisition(self, collectionTime):
        self.cached_readout = None
        self.setCollectionTime(collectionTime)

    def acquire(self):
        self.detector_for_snaps.atScanStart()
        self.detector_for_snaps.atScanLineStart()
        self.detector_for_snaps.collectData()
        self.detector_for_snaps.waitWhileBusy()
        self.cached_readout = self.detector_for_snaps.readout()
        self.detector_for_snaps.atScanLineEnd()
        self.detector_for_snaps.atScanEnd()

    def detectorReadout(self):
        return self.cached_readout if self.cached_readout is not None else self.detector.readout()

    def atScanLineStart(self):
        self.cached_readout = None
        AnalyserDetectorClass.atScanLineStart(self)

    def setCollectionTime(self, collectionTime):
        self.detector_for_snaps.setCollectionTime(collectionTime)
        AnalyserDetectorClass.setCollectionTime(self, collectionTime)

class AnalyserNxWithRectangularROIClass(AnalyserWithRectangularROIClass, DetectorSnapper):

    def __init__(self, name, detector, detector_for_snaps, processors=[], panelName="Area Detector", iFileLoader=None):
        self.detector_for_snaps = detector_for_snaps
        AnalyserWithRectangularROIClass.__init__(self, name, detector, processors, panelName, iFileLoader)

    def prepareForAcquisition(self, collectionTime):
        self.cached_readout = None
        self.updateRoiList()
        self.setCollectionTime(collectionTime)
        self.setScannableFormat(len(self.roiList))

    def acquire(self):
        self.detector_for_snaps.atScanStart()
        self.detector_for_snaps.atScanLineStart()
        self.detector_for_snaps.collectData()
        self.detector_for_snaps.waitWhileBusy()
        self.cached_readout = self.detector_for_snaps.readout()
        self.detector_for_snaps.atScanLineEnd()
        self.detector_for_snaps.atScanEnd()

    def detectorReadout(self):
        return self.cached_readout if self.cached_readout is not None else self.detector.readout()

    def atScanLineStart(self):
        self.cached_readout = None
        AnalyserWithRectangularROIClass.atScanLineStart(self)