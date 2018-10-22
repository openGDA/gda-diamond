"""
Switchable energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from gda.device.scannable import ScannableMotionBase

class EnergyScannableSwitchable(ScannableMotionBase):
    """ The energy scannable switcher scannable is intended to be used in the same scan as an switchable energy scannable
    
    One use of this would be to specify two energy scannables with different polarisations.
    
    If the switcher is specified before the switchable then each energy will be scanned for each polarisation. For example:
        scan idu_pos_neg_switcher (0 1) idu_pos_neg_switchable 780 783 1

    If the switchable is specified before the switcher then each polarisation will be scanned for each energy. For example:
        scan idu_pos_neg_switchable 780 783 1 idu_pos_neg_switcher (0 1)
    """
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
        myformat=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        return myformat % self.getPosition()

    def __repr__(self):
        myformat = "EnergyScannableSwitchable(%r, %r)"
        return myformat % (self.name, [x.name for x in self.scannable_list])

    def atScanStart(self):
        self.energyScannableInsideSwitcher=None
        self.next_scannable=None
        self.energy_eV=None

    def isBusy(self):
        return self.scannable_list[self.current_scannable].isBusy()

    def asynchronousMoveTo(self, energy_eV):
        if self.energyScannableInsideSwitcher == None:
            self.energyScannableInsideSwitcher = (self.next_scannable != None)
            if self.verbose:
                print "%s: energyScannableInsideSwitcher=%r" % (self.name, self.energyScannableInsideSwitcher)

        if self.energyScannableInsideSwitcher: # Then it will be called every time and we expect the next scannable to be set
            return self.asynchronousMoveToNext(energy_eV)
        else: # the energy scannable will not be called every time, so we have to record the required energy.
            if self.verbose:
                print "%s: future energy_eV=%r " % (self.name, energy_eV)
            self.energy_eV = energy_eV

    def asynchronousMoveToNext(self, energy_eV):
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

    def getCurrentEnergy(self):
        return self.energy_eV