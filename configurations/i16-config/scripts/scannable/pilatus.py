from gda.device.scannable import ScannableBase
from gda.device.detector.areadetector.v17.ADDriverPilatus import Gain
class PilatusThreshold(ScannableBase):
    
    def __init__(self, name, adDriverPilatus):
        self.name = name
        self.inputNames = [name + '_keV']
        self.outputFormat = ['%.3f']
        self.adDriverPilatus = adDriverPilatus

    def asynchronousMoveTo(self, threshold):
        self.adDriverPilatus.setThresholdEnergy(float(threshold))

    def isBusy(self):
        return False # asynchMoveTo blocks

    def getPosition(self):
        return self.adDriverPilatus.getThresholdEnergy_RBV()


class PilatusGain(ScannableBase):
    
    def __init__(self, name, adDriverPilatus):
        self.name = name
        self.inputNames = [name]
        self.outputFormat = ['%i']
        self.adDriverPilatus = adDriverPilatus

    def asynchronousMoveTo(self, gainObject):
        if isinstance(gainObject, Gain):
            gainEnum = gainObject
        elif isinstance(gainObject, str):
            gainEnum = Gain.valueOf(gainObject.upper())
        else: # assume number like
            gainEnum = Gain.values()[int(gainObject)] #@UndefinedVariable
        self.adDriverPilatus.setGain(gainEnum)

    def isBusy(self):
        return False # asynchMoveTo blocks

    def getPosition(self):
        return int(self.adDriverPilatus.getGain().ordinal())
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        gainNumber = self.getPosition()
        gainEnum = Gain.values()[gainNumber]
        result = self.name + ' : ' + str(gainNumber) + ' (' + str(gainEnum) + ')'
        return result