"""
Pair energy scannable class
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from energyScannableBase import EnergyScannableBase
from gda.device.scannable import ScannableMotionBase

class EnergyScannablePair(ScannableMotionBase):
    
    def __init__(self, name, idu_scannable, idd_scannable):
        
        self.name = name
        self.idu_scannable = idu_scannable
        self.idd_scannable = idd_scannable

        self.inputNames = [name]
        self.extraNames = self.getExtraNames()
        self.outputFormat = self.getOutputFormat()
        self.last_energy_eV = 0
        
        self.verbose = False
        self.concurrentRowphaseMoves=False

        # Do some minimal sanity checking on the _poly's. 
        assert(issubclass(type(idu_scannable), EnergyScannableBase))
        assert(issubclass(type(idd_scannable), EnergyScannableBase))

    def __str__(self):
        format=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        return format % self.getPosition()
 
    def __repr__(self):
        return "EnergyScannablePair(%r, %r, %r)" % (self.name,
            self.idu_scannable.name, self.idd_scannable.name)
 
    def isBusy(self):
        return (self.idu_scannable.isBusy() or 
                self.idd_scannable.isBusy() )

    def getExtraNames(self): 
        return self.idu_scannable.getExtraNames()[:6] + self.idd_scannable.getExtraNames()[:6] + \
               [ self.idu_scannable.pgm_energy.name, "diff_energy" ]

    def getOutputFormat(self):
        return ['%f'] + self.idu_scannable.getOutputFormat()[1:7] + self.idd_scannable.getOutputFormat()[1:7] + ['%f', '%f']

    def getPosition(self):
        pgm_energy = self.idu_scannable.pgm_energy.getPosition()
        diff = self.last_energy_eV - pgm_energy
        return (self.last_energy_eV,) + self.idu_scannable.getPosition()[1:7] + self.idd_scannable.getPosition()[1:7] + (pgm_energy, diff)

    def asynchronousMoveTo(self, energy_eV):
        iduPosition = self.idu_scannable.getIdPosition(energy_eV)
        iddPosition = self.idd_scannable.getIdPosition(energy_eV)
        
        self.idu_scannable.idMotorsAsynchronousMoveTo(iduPosition, energy_eV)
        self.idd_scannable.idMotorsAsynchronousMoveTo(iddPosition, energy_eV, set_pgm_energy=False)
        self.last_energy_eV = energy_eV
