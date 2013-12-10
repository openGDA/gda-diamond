"""
Polynomial energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from gda.device.scannable import ScannableMotionBase

from energyScannableBase import EnergyScannableBase
from Poly import Poly
from idPosition import IdPosition

class EnergyScannableEnum(EnergyScannableBase):
    
    def __init__(self, name, id_gap_scannable, id_rowphase1_scannable,
                 id_rowphase2_scannable, id_rowphase3_scannable,
                 id_rowphase4_scannable, id_jawphase_scannable, 
                 pgm_energy_scannable, energyPositions):
        
        EnergyScannableBase.__init__(self, name, id_gap_scannable,
            id_rowphase1_scannable, id_rowphase2_scannable,
            id_rowphase3_scannable, id_rowphase4_scannable,
            id_jawphase_scannable, pgm_energy_scannable)
        
        self.energyPositions = energyPositions

    def __repr__(self):
        format = "EnergyScannableEnum(%r, %r, %r, %r, %r, %r, %r, %r, " + \
            "energyPositions=%r)"
        return format % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name,
            self.energyPositions)

    def getIdPosition(self, energy_eV):
        return self.energyPositions[energy_eV]
