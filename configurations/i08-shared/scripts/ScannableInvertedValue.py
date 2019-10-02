from gda.device.scannable import PseudoDevice
from gda.factory import Finder
from java.lang.Math import abs


class PositionInvertedValue(PseudoDevice):
    def __init__(self,name,scannableName):
        self.name = name
        self.scannable= Finder.getInstance().find(scannableName)
        self.iambusy = 0
        self.setInputNames([name])
        self.currentposition = abs((float)(self.scannable.getPosition()))

    def getPosition(self):
        self.currentposition = abs((float)(self.scannable.getPosition()))
        return [self.currentposition]

    def isBusy(self):
        return self.iambusy

    def rawAsynchronousMoveTo(self,new_position):
        self.iambusy = 1
        self.currentposition = new_position
        self.iambusy = 0