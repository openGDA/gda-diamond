from gdascripts.analysis.io.DatasetProvider import LazyDataSetProvider
import gda.device.Detector
"""
Simple class to be used instead of ProcessingDetectorWrapper that supports NXDetectorDataWithFilepathForSrs

import dataset_provider

from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.analysis.datasetprocessor.twod.PixelIntensity import PixelIntensity

detDSProvider = dataset_provider.NXDetectorDataWithFilepathForSrsDatasetProvider(detector)

peak2d = DetectorDataProcessorWithRoi('peak2d', detDSProvider, [TwodGaussianPeak()])
max2d = DetectorDataProcessorWithRoi('max2d', detDSProvider, [SumMaxPositionAndValue()])
intensity2d = DetectorDataProcessorWithRoi('intensity2d', detDSProvider, [PixelIntensity()])

scan detector peak2d max2d intensity2d
"""
class NXDetectorDataWithFilepathForSrsDatasetProvider:
    def __init__(self, det,fileLoadTimout=None):
        self.det=det
        self.fileLoadTimout = fileLoadTimout
    def getDatasetProvider(self):
        dataset = self.det.readout()
        if isinstance(dataset, gda.device.detector.NXDetectorDataWithFilepathForSrs):
            path = dataset.getFilepath()
            print "Loading dataset from " + path
            return LazyDataSetProvider(path,fileLoadTimout=self.fileLoadTimout)
        raise Exception("readout did not return NXDetectorDataWithFilepathForSrs")
    def addShape(self,detectorDataProcessor, shapeid, shape):
        pass
    def removeShape(self,detectorDataProcessor, shapeid):
        pass
    