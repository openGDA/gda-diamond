from gda.device.scannable import ScannableBase

class ADTemperature(ScannableBase):
    
    def __init__(self, name, adBase):
        self.name = name
        self.inputNames = [name + '_set_c']
        self.extraNames = [name + '_c']
        self.outputFormat = ['%.3f']
        self.adBase = adBase

    def asynchronousMoveTo(self, temp):
        self.adBase.setTemperature(float(temp))

    def isBusy(self):
        return False # asynchMoveTo blocks

    def getPosition(self):
        return float(self.adBase.getTemperature()), float(self.adBase.getTemperature_RBV())
