"""
Energy scannable for use with I10 insertion devices at Diamond Light Source
"""

from energyScannablePoly import EnergyScannablePoly

class EnergyScannable(EnergyScannablePoly):
    def __repr__(self):
        format = "EnergyScannable(%r, %r, %r, %r, %r, %r, %r, %r, gap=%r, " + \
            "rowphase1=%r, rowphase2=%r, rowphase3=%r, rowphase4=%r, " + \
            "jawphase_poly=%r)"
        return format % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name,
            self.gap, self.rowphase1, self.rowphase2,
            self.rowphase3, self.rowphase4, self.jawphase_poly)
