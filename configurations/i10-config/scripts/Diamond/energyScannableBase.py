"""
Energy scannable base class
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from gda.device.scannable import ScannableMotionBase
from idPosition import IdPosition
from Poly import Poly
from collections import OrderedDict
from scisoftpy.jython.jymaths import interp

class EnergyScannableBase(ScannableMotionBase):
    
    class ValueLookup():
        def __init__(self, value_from_index, unit):
            self.value_from_index = value_from_index
            self.unit = unit
            
            if type(self.value_from_index) == type({}):
                # Do some minimal sanity checking on the lookups. 
                value_from_index_sorted = OrderedDict(sorted(value_from_index.items()))
                self.value_lookup_x = value_from_index_sorted.keys()
                self.value_lookup_y = value_from_index_sorted.values()

        def __call__(self, index):
            if self.value_from_index == None:
                return None
    
            if type(self.value_from_index) == type(Poly([])):
                return self.value_from_index(index)
    
            if type(self.value_from_index) == type({}):
                sorted_keys = sorted(self.value_from_index.iterkeys())
                if index < sorted_keys[0]:
                    raise ValueError("%s %r below minimum of %r" % (self.unit, index, sorted_keys[0]))
                if index > sorted_keys[-1]:
                    raise ValueError("%s %r above maximum of %r" % (self.unit, index, sorted_keys[-1]))
                interp_value= interp(index, self.value_lookup_x, self.value_lookup_y)
                # print "### value returned from jymath.interp: %f" % (interp_value)
                return interp_value
            return self.value_from_index

        def __repr__(self):
            return self.value_from_index.__repr__()

        def index(self, value):
            if type(self.value_from_index) != type({}):
                return None
            # Only lookup tables provide back reliable reverse transforms
            if value < self.value_lookup_y[0]:
                raise ValueError("motor position %r below minimum of %r" % (value, self.value_lookup_y[0]))
            if value > self.value_lookup_y[-1]:
                raise ValueError("motor position %r above maximum of %r" % (value, self.jawphase_lookup_y[-1]))
            interp_value= interp(value, self.value_lookup_y, self.value_lookup_x)
#             print "### value returned from jymath.interp: %f" % (interp_value)
            return interp_value

    def __init__(self, name, id_gap_scannable,
                 id_rowphase1_scannable, id_rowphase2_scannable,
                 id_rowphase3_scannable, id_rowphase4_scannable,
                 id_jawphase_scannable, pgm_energy_scannable,
                 gap_from_energy, rowphase1_from_energy, rowphase2_from_energy, 
                 rowphase3_from_energy, rowphase4_from_energy, jawphase_from_energy):

        self.name = name
        self.id_gap = id_gap_scannable
        self.id_rowphase1 = id_rowphase1_scannable
        self.id_rowphase2 = id_rowphase2_scannable
        self.id_rowphase3 = id_rowphase3_scannable
        self.id_rowphase4 = id_rowphase4_scannable
        self.id_jawphase = id_jawphase_scannable
        self.pgm_energy = pgm_energy_scannable

        self.inputNames = [name]
        self.extraNames = self.getExtraNames()
        self.outputFormat = self.getOutputFormat()
        self.last_energy_eV = 0

        self.gap_from_energy = EnergyScannableBase.ValueLookup(gap_from_energy, "energy_eV")
        self.rowphase1_from_energy = EnergyScannableBase.ValueLookup(rowphase1_from_energy, "energy_eV")
        self.rowphase2_from_energy = EnergyScannableBase.ValueLookup(rowphase2_from_energy, "energy_eV")
        self.rowphase3_from_energy = EnergyScannableBase.ValueLookup(rowphase3_from_energy, "energy_eV")
        self.rowphase4_from_energy = EnergyScannableBase.ValueLookup(rowphase4_from_energy, "energy_eV")
        self.jawphase_from_energy = EnergyScannableBase.ValueLookup(jawphase_from_energy, "energy_eV")

        self.verbose = False
        self.concurrentRowphaseMoves=False
        self.energyMode=False #default to jawphase energy, if True gap controlled energy
        self.IamBusy=False

    def __str__(self):
        myformat=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        return myformat % self.getPosition()

    def __repr__(self):
        myformat = "EnergyScannableBase(%r, %r, %r, %r, %r, %r, %r, %r, gap=%r, " + \
            "rowphase1=%r, rowphase2=%r, rowphase3=%r, rowphase4=%r, " + \
            "jawphase=%r)"
        return myformat % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name,
            self.gap_from_energy, self.rowphase1_from_energy, self.rowphase2_from_energy,
            self.rowphase3_from_energy, self.rowphase4_from_energy, self.jawphase_from_energy)
        
    def stop(self):
        self.id_gap.stop()
        self.id_rowphase1.stop()
        self.id_rowphase2.stop()
        self.id_rowphase3.stop()
        self.id_rowphase4.stop()
        self.id_jawphase.stop()
        self.pgm_energy.stop()        

    def isBusy(self):
#         print "id_gap is busy: %s" % (self.id_gap.isBusy())
#         print "id_rowphase1 is busy: %s" % (self.id_rowphase1.isBusy())
#         print "id_rowphase2 is busy: %s" % (self.id_rowphase2.isBusy())
#         print "id_rowphase3 is busy: %s" % (self.id_rowphase3.isBusy())
#         print "id_rowphase4 is busy: %s" % (self.id_rowphase4.isBusy())
#         print "id_jawphase is busy: %s" % (self.id_jawphase.isBusy())
#         print "pgm_energy is busy: %s" % (self.pgm_energy.isBusy())       
        return (self.IamBusy or self.id_gap.isBusy() or 
                self.id_rowphase1.isBusy() or
                self.id_rowphase2.isBusy() or
                self.id_rowphase3.isBusy() or
                self.id_rowphase4.isBusy() or
                self.id_jawphase.isBusy() or 
                self.pgm_energy.isBusy() )
        
    def moveToMayWait(self, scannable, position, wait=False):
        from time import sleep
        
        if self.verbose:
            print "Moving %s to %f" % (scannable.name, position)
            
        scannable.asynchronousMoveTo(position)
        
        if wait:
            while scannable.isBusy():
                sleep(0.1)

    def moveTwoToSync(self, scannable1, position1, scannable2, position2, wait=False):
        from time import sleep
        
        if self.verbose:
            print "Moving %s to %f & %s to %f " % (
                scannable1.name, position1, scannable2.name, position2)
            
        scannable1.asynchronousMoveTo(position1)
        scannable2.asynchronousMoveTo(position2)
        
        if wait:
            while scannable1.isBusy() or scannable2.isBusy():
                sleep(0.1)

    def idMotorsAsynchronousMoveTo(self, idPosition, energy_eV, set_pgm_energy=True):
        self.last_energy_eV = 0
        self.IamBusy=True

        #Move ID polarisation correction for this energy must be move 1st
        if self.concurrentRowphaseMoves:
            self.moveTwoToSync(self.id_rowphase1, idPosition.rowphase1, 
                               self.id_rowphase3, idPosition.rowphase3, wait=True)
            self.moveTwoToSync(self.id_rowphase2, idPosition.rowphase2,
                               self.id_rowphase4, idPosition.rowphase4, wait=True)
        else:
            self.moveToMayWait(self.id_rowphase1, idPosition.rowphase1, wait=True)
            self.moveToMayWait(self.id_rowphase2, idPosition.rowphase2, wait=True)
            self.moveToMayWait(self.id_rowphase3, idPosition.rowphase3, wait=True)
            self.moveToMayWait(self.id_rowphase4, idPosition.rowphase4, wait=True)
        #move ID gap for this energy
        self.moveToMayWait(self.id_gap, idPosition.gap, wait=False)
        #then move PGM energy to this energy
        if set_pgm_energy:
            self.moveToMayWait(self.pgm_energy, energy_eV, wait=False)
        #jaw phase cannot be move when row phase is moving thus polarisation move need to wait above!
        self.moveToMayWait(self.id_jawphase, idPosition.jawphase, wait=False)
        
        self.last_energy_eV = energy_eV
        self.IamBusy=False

    def getIdPosition(self, energy_eV):
        return IdPosition(self.gap_from_energy(energy_eV), self.rowphase1_from_energy(energy_eV), self.rowphase2_from_energy(energy_eV),
                          self.rowphase3_from_energy(energy_eV), self.rowphase4_from_energy(energy_eV), self.jawphase_from_energy(energy_eV))

    def getExtraNames(self): 
        return [self.id_gap.name, self.id_rowphase1.name,
                self.id_rowphase2.name, self.id_rowphase3.name,
                self.id_rowphase4.name, self.id_jawphase.name, 
                self.pgm_energy.name, "diff_energy" ]
        
    def getOutputFormat(self):
        return ['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f']

    def getPosition(self):
        pgmenergy = self.pgm_energy.getPosition()
        diff = self.last_energy_eV - pgmenergy
        return (self.last_energy_eV, self.id_gap.getPosition(),
                self.id_rowphase1.getPosition(), self.id_rowphase2.getPosition(),
                self.id_rowphase3.getPosition(), self.id_rowphase4.getPosition(),
                self.id_jawphase.getPosition(), pgmenergy, diff)

    # Derived classes must either implement getIdPosition or override asynchronousMoveTo

    def asynchronousMoveTo(self, energy_eV):
        idPosition = self.getIdPosition(energy_eV)
        self.idMotorsAsynchronousMoveTo(idPosition, energy_eV)
