"""
Lookup energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from energyScannableBase import EnergyScannableBase
from idPosition import IdPosition

class EnergyScannableLookup(EnergyScannableBase):
    
    def __init__(self, name, id_gap_scannable, id_rowphase1_scannable,
                 id_rowphase2_scannable, id_rowphase3_scannable,
                 id_rowphase4_scannable, id_jawphase_scannable, 
                 pgm_energy_scannable,
                 gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase_lookup):
        
        EnergyScannableBase.__init__(self, name, id_gap_scannable,
            id_rowphase1_scannable, id_rowphase2_scannable,
            id_rowphase3_scannable, id_rowphase4_scannable,
            id_jawphase_scannable, pgm_energy_scannable,
            gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase_lookup)

    def __repr__(self):
        myformat = "EnergyScannableLookup(%r, %r, %r, %r, %r, %r, %r, %r, gap=%r, " + \
            "rowphase1=%r, rowphase2=%r, rowphase3=%r, rowphase4=%r, " + \
            "jawphase_lookup=%r)"
        return myformat % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name,
            self.gap_from_energy, self.rowphase1_from_energy, self.rowphase2_from_energy,
            self.rowphase3_from_energy, self.rowphase4_from_energy, self.jawphase_from_energy)

    def getEnergy(self, idPosition):
        if self.energyMode:
            id_energy = self.gap_from_energy.index(idPosition.gap)
        else:
            id_energy = self.jawphase_from_energy.index(idPosition.jawphase)
        if id_energy == None:
            id_energy = self.last_energy_eV
        return id_energy

    def getExtraNames(self):
        extraNames = EnergyScannableBase.getExtraNames(self)
        extraNames.extend(['id_energy', 'id_diff'])
        return extraNames
        
    def getOutputFormat(self):
        outputFormat = EnergyScannableBase.getOutputFormat(self)
        outputFormat.extend(['%f', '%f'])
        return outputFormat

    def getPosition(self):
        (energy_eV, gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase, pgm_energy, pgm_diff) = EnergyScannableBase.getPosition(self)
        id_energy = self.getEnergy(IdPosition(gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase))
        id_diff = energy_eV - id_energy
        return (energy_eV, gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase, pgm_energy, pgm_diff, id_energy, id_diff)
