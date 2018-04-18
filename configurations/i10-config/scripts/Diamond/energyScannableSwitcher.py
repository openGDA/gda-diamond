"""
Switcher scannable which switches between switchable energy scannables
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from gda.device.scannable import ScannableMotionBase

class EnergyScannableSwitcher(ScannableMotionBase):
    """ The energy scannable switcher scannable is intended to be used in the same scan as an switchable energy scannable
    
    One use of this would be to specify two energy scannables with different polarisations.
    
    If the switcher is specified before the switchable then each energy will be scanned for each polarisation. For example:
        scan idu_pos_neg_switcher (0 1) idu_pos_neg_switchable 780 783 1

    If the switchable is specified before the switcher then each polarisation will be scanned for each energy. For example:
        scan idu_pos_neg_switchable 780 783 1 idu_pos_neg_switcher (0 1)
    """
    def __init__(self, name, energy_scannable_switchable):
        
        self.name = name
        self.energy_scannable_switchable = energy_scannable_switchable
        
        self.inputNames = [name]
        self.extraNames = self.getExtraNames()
        self.outputFormat = self.getOutputFormat()
        
        self.level = energy_scannable_switchable.level
        self.verbose = False

    def __str__(self):
        myformat=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        return myformat % self.getPosition()

    def __repr__(self):
        myformat = "EnergyScannableSwitchable(%r, %r)"
        return myformat % (self.name, self.energy_scannable_switchable.name)

    def atScanStart(self):
        self.energyScannableInsideSwitcher=None

    def isBusy(self):
        return self.energy_scannable_switchable.isBusy()

    def asynchronousMoveTo(self, next_scannable):
        if self.energyScannableInsideSwitcher == None:
            self.energyScannableInsideSwitcher = (self.energy_scannable_switchable.getCurrentEnergy() == None)
            if self.verbose:
                print "%s: energyScannableInsideSwitcher=%r" % (self.name, self.energyScannableInsideSwitcher)

        next_scannable = int(next_scannable)
        if self.verbose:
            print "%s: next_scannable=%r" % (self.name, next_scannable)
        
        self.energy_scannable_switchable.setNextScannable(next_scannable)
        if not self.energyScannableInsideSwitcher: # Then energy will not be moved every time and we have to move it ourselves
            self.energy_scannable_switchable.asynchronousMoveToNext(self.energy_scannable_switchable.getCurrentEnergy())

    def getExtraNames(self): 
        return []
        
    def getOutputFormat(self):
        return [ "%d" ]

    def getPosition(self):
        return self.energy_scannable_switchable.getNextScannable()
