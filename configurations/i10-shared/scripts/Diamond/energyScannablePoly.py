"""
Polynomial energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""

from energyScannableBase import EnergyScannableBase
from Poly import Poly


class EnergyScannablePoly(EnergyScannableBase):

    def __init__(self, name, id_gap_scannable, id_rowphase1_scannable,
                 id_rowphase2_scannable, id_rowphase3_scannable,
                 id_rowphase4_scannable, id_jawphase_scannable,
                 pgm_energy_scannable,
                 gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase_poly):

        EnergyScannableBase.__init__(self, name, id_gap_scannable,
            id_rowphase1_scannable, id_rowphase2_scannable,
            id_rowphase3_scannable, id_rowphase4_scannable,
            id_jawphase_scannable, pgm_energy_scannable,
            gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase_poly)

        # Do some minimal sanity checking on the _poly's.
        assert(type(jawphase_poly) == type(Poly([])))

    def __repr__(self):
        format = "EnergyScannablePoly(%r, %r, %r, %r, %r, %r, %r, %r, gap=%r, " + \
            "rowphase1=%r, rowphase2=%r, rowphase3=%r, rowphase4=%r, " + \
            "jawphase_poly=%r)"
        return format % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name,
            self.gap_from_energy, self.rowphase1_from_energy, self.rowphase2_from_energy,
            self.rowphase3_from_energy, self.rowphase4_from_energy, self.jawphase_from_energy)
