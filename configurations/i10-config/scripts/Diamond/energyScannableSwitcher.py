"""
Switcher scannable which switches between switchable energy scannables
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
#from math import sin, asin, pi
try:
    from gda.device.scannable import ScannableMotionBase
except ImportError:
    ScannableMotionBase = object

class EnergyScannableSwitcher(ScannableMotionBase):
    
    def __init__(self, name, energy_scannable_switchable):
        
        self.name = name
        self.energy_scannable_switchable = energy_scannable_switchable
        self.energy_scannable_switchable.setNextScannable(0)
        
        self.inputNames = [name]
        self.extraNames = self.getExtraNames()
        self.outputFormat = self.getOutputFormat()
        
        self.verbose = False

    def __str__(self):
        format=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        position = self.getPosition()
        return format % self.getPosition()

    def __repr__(self):
        format = "EnergyScannableSwitchable(%r, %r)"
        return format % (self.name, self.energy_scannable_switchable.name)

    def isBusy(self):
        return False

    def asynchronousMoveTo(self, next_scannable):
        next_scannable = int(next_scannable)
        if self.verbose:
            print "%s: next_scannable=%r" % (self.name, next_scannable)
        self.energy_scannable_switchable.setNextScannable(next_scannable)

    def getExtraNames(self): 
        return []
        
    def getOutputFormat(self):
        return [ "%d" ]

    def getPosition(self):
        return self.energy_scannable_switchable.getNextScannable()