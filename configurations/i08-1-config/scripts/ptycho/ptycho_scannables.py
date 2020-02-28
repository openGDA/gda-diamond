'''
Information monitors that can be used to get info into the nexus file.
'''
from gda.device.scannable import DummyScannable

'''
Calculate the pixel size of the Andor detector.
This should be initialised with a Monitor whose PV is a binning value, and its "position" is
calculated from the binning PV.
Functions other than getPosition() will be inherited from DummyScannable and should not be called.
'''
class andorPixelSizeCalc(DummyScannable):

    def __init__(self, monitor, name):
        self.monitor = monitor
        self.name = name
        self.setInputNames([self.name])

    def isBusy(self):
        return False

    def getLowerGdaLimits(self):
        return None

    def getUpperGdaLimits(self):
        return None

    def getPosition(self):
        return int(self.monitor.getPosition()) * 13e-6
