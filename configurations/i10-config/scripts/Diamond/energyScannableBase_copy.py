"""
Energy scannable base class
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
import warnings
warnings.warn("the try_continuous_energy module is deprecated. All objects in this module are already imported into GDA.", 
              DeprecationWarning,
              stacklevel=2)

from gda.device.scannable import ScannableMotionBase
from idPosition import IdPosition
from Poly import Poly
from collections import OrderedDict
from scisoftpy.external import create_function

python_path="/dls_sw/i21/software/miniconda2/envs/gdaenv/lib/python2.7/"
python_exe="/dls_sw/i21/software/miniconda2/envs/gdaenv/bin/python"
local_module_path="/dls_sw/i21/software/miniconda2/lib/python2.7/site-packages"

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
                # Note that this function has been added to scisoft as of master (destined for gda-8.45)
                self.interp = create_function('interp', module='numpy', exe=python_exe, path=[python_path], extra_path=[local_module_path], dls_module=False, keep=False) # TODO: Replace with scisoft function in gda-8.46

        """ Annoyingly, sometimes self.interp fails and returns the input value as it's output value!
            See I10 logs where id_energy_follower moves to pgm_energy=831.408565 (jawphase from getIdPosition 831.2583050847456!):
            2015-05-20 18:01:25,297 INFO  FollowerScannable:id_energy_follower - Moving idu_circ_pos_energy to 831.408565 (831.2583050847456)  
    
        def getIdPosition(self, energy_eV):
            if energy_eV < self.jawphase_lookup_x[0]:
                raise ValueError("energy_eV %r below minimum of %r" % (energy_eV, self.jawphase_lookup_x[0]))
            if energy_eV > self.jawphase_lookup_x[-1]:
                raise ValueError("energy_eV %r above maximum of %r" % (energy_eV, self.jawphase_lookup_x[-1]))
            jawphase = self.interp(energy_eV, self.jawphase_lookup_x, self.jawphase_lookup_y)
            return IdPosition(self.gap, self.rowphase1, self.rowphase2, self.rowphase3, self.rowphase4, jawphase)
"""

        def __call__(self, index):
            if self.value_from_index == None:
                return None
    
            if type(self.value_from_index) == type(Poly([])):
                return self.value_from_index(index)
    
            if type(self.value_from_index) == type({}):
                below=above=None
                for key in sorted(self.value_from_index.iterkeys()):
                    #print "energy_eV = %r, key = %r" % (energy_eV, key)
                    if key <= index:
                        below = key
                    if above == None and key >= index:
                        above = key
                #print "energy_ev = %r, above = %r, below=%r" % (energy_eV, above, below)
                if below == None:
                    raise ValueError("%s %r below minimum of %r" % (self.unit, index, sorted(self.value_from_index.iterkeys())[0]))
                if above == None:
                    raise ValueError("%s %r above maximum of %r" % (self.unit, index, sorted(self.value_from_index.iterkeys(), reverse=True)[0]))
                if above == below:
                    value = self.value_from_index[below]
                    #print "jawphase = %r" % (jawphase)
                else:
                    a, b = self.value_from_index[above], self.value_from_index[below]
                    slope = (a-b)/(above-below)
                    value = b + slope*(index-below)
                    #print "jawphase = %r (lookup above=%r, lookup below=%r, slope=%r)" % (jawphase, a, b, slope)
                return value
            return self.value_from_index

        def __repr__(self):
            return self.value_from_index.__repr__()

        def index(self, value):
            if type(self.value_from_index) != type({}):
                return None
                # Only lookup tables provide back reliable reverse transforms
            if value < self.value_lookup_y[0]:
                raise ValueError("jawphase %r below minimum of %r" % (value, self.value_lookup_y[0]))
            if value > self.value_lookup_y[-1]:
                raise ValueError("jawphase %r above maximum of %r" % (value, self.jawphase_lookup_y[-1]))
#             print "### call numpy.interp method ..."
            interp_value= self.interp(value, self.value_lookup_y, self.value_lookup_x)
#             print "### value returned from numpy.interp: %f" % (interp_value)
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

    def __str__(self):
        format=", ".join([ a + "=" + b for (a,b) in zip(
              self.inputNames+self.extraNames,self.outputFormat)])
        return format % self.getPosition()

    def __repr__(self):
        format = "EnergyScannableBase(%r, %r, %r, %r, %r, %r, %r, %r, gap=%r, " + \
            "rowphase1=%r, rowphase2=%r, rowphase3=%r, rowphase4=%r, " + \
            "jawphase=%r)"
        return format % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name,
            self.gap_from_energy, self.rowphase1_from_energy, self.rowphase2_from_energy,
            self.rowphase3_from_energy, self.rowphase4_from_energy, self.jawphase_from_energy)

    def isBusy(self):
#         print "id_gap is busy: %s" % (self.id_gap.isBusy())
#         print "id_rowphase1 is busy: %s" % (self.id_rowphase1.isBusy())
#         print "id_rowphase2 is busy: %s" % (self.id_rowphase2.isBusy())
#         print "id_rowphase3 is busy: %s" % (self.id_rowphase3.isBusy())
#         print "id_rowphase4 is busy: %s" % (self.id_rowphase4.isBusy())
#         print "id_jawphase is busy: %s" % (self.id_jawphase.isBusy())
#         print "pgm_energy is busy: %s" % (self.pgm_energy.isBusy())       
        return (self.id_gap.isBusy() or 
                self.id_rowphase1.isBusy() or
                self.id_rowphase2.isBusy() or
                self.id_rowphase3.isBusy() or
                self.id_rowphase4.isBusy() or
                self.id_jawphase.isBusy() or 
                self.pgm_energy.isBusy() )

    def moveToMayWait(self, scannable, position, wait):
        from time import sleep
        
        if self.verbose:
            print "Moving %s to %f" % (scannable.name, position)
            
        scannable.asynchronousMoveTo(position)
        
        if wait:
            while scannable.isBusy():
                sleep(0.1)

    def moveTwoToSync(self, scannable1, position1, scannable2, position2):
        from time import sleep
        
        if self.verbose:
            print "Moving %s to %f & %s to %f " % (
                scannable1.name, position1, scannable2.name, position2)
            
        scannable1.asynchronousMoveTo(position1)
        scannable2.asynchronousMoveTo(position2)
        
        while scannable1.isBusy() or scannable2.isBusy():
            sleep(0.1)

    def idMotorsAsynchronousMoveTo(self, idPosition, energy_eV, set_pgm_energy=True):
        self.last_energy_eV = 0

        self.moveToMayWait(self.id_gap, idPosition.gap, wait=True)
        if self.concurrentRowphaseMoves:
            self.moveTwoToSync(self.id_rowphase1, idPosition.rowphase1, 
                               self.id_rowphase3, idPosition.rowphase3)
            self.moveTwoToSync(self.id_rowphase2, idPosition.rowphase2,
                               self.id_rowphase4, idPosition.rowphase4)
        else:
            self.moveToMayWait(self.id_rowphase1, idPosition.rowphase1, wait=True)
            self.moveToMayWait(self.id_rowphase2, idPosition.rowphase2, wait=True)
            self.moveToMayWait(self.id_rowphase3, idPosition.rowphase3, wait=True)
            self.moveToMayWait(self.id_rowphase4, idPosition.rowphase4, wait=True)
        self.moveToMayWait(self.id_jawphase, idPosition.jawphase, wait=False)
        
        if set_pgm_energy:
            self.moveToMayWait(self.pgm_energy, energy_eV, wait=False)
        
        self.last_energy_eV = energy_eV

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
