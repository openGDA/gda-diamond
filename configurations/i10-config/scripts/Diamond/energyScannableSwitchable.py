"""
Switchable energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
#from math import sin, asin, pi
try:
    from gda.device.scannable import ScannableMotionBase
except ImportError:
    ScannableMotionBase = object

class EnergyScannableSwitchable(ScannableMotionBase):
    
    def __init__(self, name, scannable_list):
        
        self.name = name
        self.scannable_list = scannable_list
        self.next_scannable = 0
        self.current_scannable = 0
        
        self.inputNames = [name]
        self.extraNames = self.getExtraNames()
        self.outputFormat = self.getOutputFormat()
        
        self.verbose = False
        
        extraNameLen0 = len(scannable_list[0].getExtraNames())
        for scannable in scannable_list:
            assert (len(scannable.getExtraNames()) == extraNameLen0)

    def __str__(self):
        format=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        return format % self.getPosition()

    def __repr__(self):
        format = "EnergyScannableSwitchable(%r, %r)"
        return format % (self.name, [x.name for x in self.scannable_list])

    def isBusy(self):
        return self.scannable_list[self.current_scannable].isBusy()

    def asynchronousMoveTo(self, energy_eV):
        if self.verbose:
            print "%s: energy_eV=%r" % (self.name, energy_eV)
        self.current_scannable = self.next_scannable
        self.scannable_list[self.current_scannable].asynchronousMoveTo(energy_eV)

    def getExtraNames(self): 
        return self.scannable_list[0].getExtraNames()
        
    def getOutputFormat(self):
        return self.scannable_list[0].getOutputFormat()

    def getPosition(self):
        return self.scannable_list[self.current_scannable].getPosition()

    def getCurrentScannable(self):
        return self.current_scannable

    def getNextScannable(self):
        return self.next_scannable

    def setNextScannable(self, next_scannable):
        self.next_scannable = next_scannable