'''
Information monitors that can be used to get info into the nexus file.
'''
from gda.device.scannable import DummyScannable

'''
Calculate the binned pixel size of a detector.
This should be initialised with two scannables: the pixel size of the detector and its binning value.  
The "position" of the BinnedPixelSize scannable is calculated from these two values.
Functions other than getPosition() will be inherited from DummyScannable and should not be called.
'''
class BinnedPixelSize(DummyScannable):

    def __init__(self, pixel_size, binning, name):
        self.pixel_size = pixel_size
        self.binning = binning
        self.name = name
        self.setInputNames([self.name])

    def isBusy(self):
        return False

    def getLowerGdaLimits(self):
        return None

    def getUpperGdaLimits(self):
        return None

    def getPosition(self):
        return self.pixel_size.getPosition() * self.binning.getPosition() / 1e6 # convert to metres
