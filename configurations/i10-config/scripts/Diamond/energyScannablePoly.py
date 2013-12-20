"""
Polynomial energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from gda.device.scannable import ScannableMotionBase

from energyScannableBase import EnergyScannableBase
from Poly import Poly
from idPosition import IdPosition

class EnergyScannablePoly(EnergyScannableBase):
    
    def __init__(self, name, id_gap_scannable, id_rowphase1_scannable,
                 id_rowphase2_scannable, id_rowphase3_scannable,
                 id_rowphase4_scannable, id_jawphase_scannable, 
                 pgm_energy_scannable,
                 gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase_poly):
        
        EnergyScannableBase.__init__(self, name, id_gap_scannable,
            id_rowphase1_scannable, id_rowphase2_scannable,
            id_rowphase3_scannable, id_rowphase4_scannable,
            id_jawphase_scannable, pgm_energy_scannable)
        
        self.gap = gap
        self.rowphase1 = rowphase1
        self.rowphase2 = rowphase2
        self.rowphase3 = rowphase3
        self.rowphase4 = rowphase4
        
        self.jawphase_poly = jawphase_poly
        
        # Do some minimal sanity checking on the _poly's. 
        assert(type(jawphase_poly)==type(Poly([])))

    def __repr__(self):
        format = "EnergyScannablePoly(%r, %r, %r, %r, %r, %r, %r, %r, gap=%r, " + \
            "rowphase1=%r, rowphase2=%r, rowphase3=%r, rowphase4=%r, " + \
            "jawphase_poly=%r)"
        return format % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name,
            self.gap, self.rowphase1, self.rowphase2,
            self.rowphase3, self.rowphase4, self.jawphase_poly)

    def getIdPosition(self, energy_eV):
        return IdPosition(self.gap,
            self.rowphase1, self.rowphase2, self.rowphase3, self.rowphase4,
            self.jawphase_poly(energy_eV))
