"""
Polynomial energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from gda.device.scannable import ScannableMotionBase

from energyScannableBase import EnergyScannableBase
from Poly import Poly
from idPosition import IdPosition

class EnergyScannableLinearArbitrary(EnergyScannableBase):
    
    def __init__(self, name, id_gap_scannable, id_rowphase1_scannable,
                 id_rowphase2_scannable, id_rowphase3_scannable,
                 id_rowphase4_scannable, id_jawphase_scannable, 
                 pgm_energy_scannable, pol_angle_scannable_name,
                 angle_min_Deg, angle_max_Deg, angle_threshold_Deg,
                 energy_min_eV, energy_max_eV,
                 rowphase1, rowphase2, rowphase3, rowphase4,
                 gap_poly, jawphase_poly):
        
        self.pol_angle_scannable_name = pol_angle_scannable_name
        self.angle_min_Deg = angle_min_Deg
        self.angle_max_Deg = angle_max_Deg
        self.angle_threshold_Deg = angle_threshold_Deg
        self.energy_min_eV = energy_min_eV
        self.energy_max_eV = energy_max_eV
        self.rowphase1 = rowphase1
        self.rowphase2 = rowphase2
        self.rowphase3 = rowphase3
        self.rowphase4 = rowphase4

        self.gap_poly = gap_poly
        self.jawphase_poly = jawphase_poly
        
        # Do some minimal sanity checking on the _poly's. 
        assert(type(gap_poly)==type(Poly([])))
        assert(type(jawphase_poly)==type(Poly([])))
        
        self.angle_Deg = 0

        EnergyScannableBase.__init__(self, name, id_gap_scannable,
            id_rowphase1_scannable, id_rowphase2_scannable,
            id_rowphase3_scannable, id_rowphase4_scannable,
            id_jawphase_scannable, pgm_energy_scannable,
            gap_poly, rowphase1, rowphase2, rowphase3, rowphase4, jawphase_poly)

    def __repr__(self):
        format = "EnergyScannableLinearArbitrary(%r, %r, %r, %r, %r, %r, " + \
            "%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)"
        return format % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name,
            self.angle_min_Deg, self.angle_max_Deg, self.angle_threshold_Deg, 
            self.energy_min_eV, self.energy_max_eV,
            self.rowphase1, self.rowphase2, self.rowphase3, self.rowphase4,
            self.gap_poly, self.jawphase_poly)

    def getIdPosition(self, energy_eV):
        assert self.angle_min_Deg <= self.angle_Deg , \
            "Requested polarisation angle (%f) " %  self.angle_Deg + \
            "is less than %f degrees" % self.angle_min_Deg 
        assert self.angle_Deg <= self.angle_max_Deg , \
            "Requested polarisation angle (%f) " %  self.angle_Deg + \
            "is greater than %f degrees" % self.angle_max_Deg
        assert self.energy_min_eV <= energy_eV , \
            "Requested energy (%f eV) " % energy_eV + \
            "is less than %f eV"  % self.energy_min_eV
        assert energy_eV <= self.energy_max_eV , \
            "Requested energy (%f eV) " % energy_eV + \
            "is greater than %f eV" % self.energy_max_eV

        gap = self.gap_poly(energy_eV)
        rowphase1 = self.rowphase1
        rowphase2 = self.rowphase2
        rowphase3 = self.rowphase3
        rowphase4 = self.rowphase4

        #alpha_real = self.angle_Deg + 180. \
        #    if self.angle_Deg <= self.angle_threshold_Deg else self.angle_Deg

        alpha_real = self.angle_Deg if self.angle_Deg > self.angle_threshold_Deg \
                else self.angle_Deg + 180.

        jawphase = self.jawphase_poly(alpha_real)

        return IdPosition(gap, rowphase1, rowphase2, rowphase3, rowphase4,
            jawphase)

    def getExtraNames(self): 
        return [self.pol_angle_scannable_name, self.id_gap.name,
                self.id_rowphase1.name, self.id_rowphase2.name,
                self.id_rowphase3.name, self.id_rowphase4.name, 
                self.id_jawphase.name, self.pgm_energy.name, "diff_energy" ]
        
    def getOutputFormat(self):
        return ['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f']

    def getPosition(self):
        pgm_energy = self.pgm_energy.getPosition()
        diff = self.last_energy_eV - pgm_energy
        return (self.last_energy_eV, self.angle_Deg, self.id_gap.getPosition(),
                self.id_rowphase1.getPosition(), self.id_rowphase2.getPosition(),
                self.id_rowphase3.getPosition(), self.id_rowphase4.getPosition(),
                self.id_jawphase.getPosition(), pgm_energy, diff)

class PolarisationAngleScannable(ScannableMotionBase):
    
    def __init__(self, name, id_energy_scannable):
        self.name = name
        self.id_energy_scannable = id_energy_scannable

        self.inputNames = [name]
        self.extraNames = self.getExtraNames()
        self.outputFormat = self.getOutputFormat()

    def __str__(self):
        format=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        return format % self.getPosition()

    def __repr__(self):
        format = "PolarisationAngleScannable(%r, %r)"
        return format % (self.name, self.id_energy_scannable.name)

    def isBusy(self):
        return self.id_energy_scannable.isBusy()
    
    def asynchronousMoveTo(self, angle_Deg):
        self.id_energy_scannable.angle_Deg = angle_Deg
        self.id_energy_scannable.asynchronousMoveTo(
            self.id_energy_scannable.pgm_energy.getPosition())

    # Swap energy and angle values for angle scannable
    def getExtraNames(self): 
        extraNames = self.id_energy_scannable.getExtraNames()
        extraNames[0] = self.id_energy_scannable.name
        return extraNames
        
    def getOutputFormat(self):
        outputFormat = self.id_energy_scannable.getOutputFormat()
        return [outputFormat[1], outputFormat[0]] + outputFormat[2:]

    def getPosition(self):
        position = self.id_energy_scannable.getPosition()
        return (position[1], position[0]) + position[2:]
        