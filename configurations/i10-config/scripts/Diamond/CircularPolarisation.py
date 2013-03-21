"""
Circular Polarisation Energy scannable for use with GDA at Diamond Light Source

NOTE:
    This Class is deprecated - to use circular polarisation, it will need
    to be converted for use with the new quad rowphase ID.
    
    It was retained as it started to implement reverse translation which
    might be useful later.
"""
#from math import sin, asin, pi
from Poly import Poly
from gda.device.scannable import ScannableMotionBase

class CircularPolarisationDeprecated(ScannableMotionBase):
    
    def __init__(self, name, id_gap_scannable, id_rp_upper_scannable, 
                 id_rp_lower_scannable, pgm_energy_scannable,
                 gap_poly, row_phase_poly, energy_poly=None, positiveDirection=True):
        
        self.name = name
        
        self.id_gap = id_gap_scannable  
        self.id_rp_upper = id_rp_upper_scannable
        self.id_rp_lower = id_rp_lower_scannable 
        self.pgm_energy = pgm_energy_scannable
        self.gap_poly=gap_poly
        self.row_phase_poly=row_phase_poly
        self.energy_poly=energy_poly
        self.row_phase_multiplier=(1 if positiveDirection else -1)
        
        self.inputNames = [name]
        self.extraNames = [id_gap_scannable.name,
            id_rp_upper_scannable.name, id_rp_lower_scannable.name,
            pgm_energy_scannable.name, "diff_energy" ]
        
        self.outputFormat = ['%f', '%f', '%f', '%f', '%f', '%f']

        # Do some minimal sanity checking on the _poly's. 
        assert(type(gap_poly)==type(Poly([])))
        assert(type(row_phase_poly)==type(Poly([])))
        if self.energy_poly is not None:
            assert(type(energy_poly)==type(Poly([])))

    def __str__(self):
        format=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        return format % self.getPosition()

    def __repr__(self):
        format = "CircularPolarisation(%r, %r, %r, %r, %r, gap_poly=%r, " + \
            "row_phase_poly=%r, energy_poly=%r, positiveDirection=%r)"  
        return format % (self.name, self.id_gap.name, self.id_rp_upper.name,
            self.id_rp_lower.name, self.pgm_energy.name, self.gap_poly,
            self.row_phase_poly, self.energy_poly, self.row_phase_multiplier==1)

    def isBusy(self):
        return (self.id_gap.isBusy() or 
                self.id_rp_upper.isBusy() or
                self.id_rp_lower.isBusy() or 
                self.pgm_energy.isBusy() )
    
    def asynchronousMoveTo(self, energy_eV):
        gap = self.gap_poly(energy_eV)
        row_phase = self.row_phase_poly(gap)*self.row_phase_multiplier
        
        self.id_gap.asynchronousMoveTo(gap)
        self.id_rp_upper.asynchronousMoveTo(row_phase)
        self.id_rp_lower.asynchronousMoveTo(row_phase)
        self.pgm_energy.asynchronousMoveTo(energy_eV)
        
    def getPosition(self):
        id_gap = self.id_gap.getPosition()
        pgm_energy = self.pgm_energy.getPosition()
        if self.energy_poly is None:
            id_energy=pgm_energy
        else:
            id_energy=self.energy_poly(id_gap)
            
        diff = id_energy - pgm_energy
        return (id_energy, id_gap, self.id_rp_upper.getPosition(),
                self.id_rp_lower.getPosition(), pgm_energy, diff)
