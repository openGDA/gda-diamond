"""
Lookup energy scannable
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
from energyScannableBase import EnergyScannableBase
from idPosition import IdPosition
from scisoftpy.external import create_function
from scisoftpy._external.ordereddict import OrderedDict

class EnergyScannableLookup(EnergyScannableBase):
    
    def __init__(self, name, id_gap_scannable, id_rowphase1_scannable,
                 id_rowphase2_scannable, id_rowphase3_scannable,
                 id_rowphase4_scannable, id_jawphase_scannable, 
                 pgm_energy_scannable,
                 gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase_lookup):
        
        EnergyScannableBase.__init__(self, name, id_gap_scannable,
            id_rowphase1_scannable, id_rowphase2_scannable,
            id_rowphase3_scannable, id_rowphase4_scannable,
            id_jawphase_scannable, pgm_energy_scannable)
        
        self.gap = gap
        self.rowphase1 = rowphase1
        self.rowphase2 = rowphase2
        self.rowphase3 = rowphase3
        self.rowphase4 = rowphase4
        
        # Do some minimal sanity checking on the _lookup. 
        assert(type(jawphase_lookup)==type({}))
        
        self.jawphase_lookup = jawphase_lookup
        jawphase_lookup_sorted = OrderedDict(sorted(jawphase_lookup.items()))
        self.jawphase_lookup_x = jawphase_lookup_sorted.keys()
        self.jawphase_lookup_y = jawphase_lookup_sorted.values()
        
        # Note that this function has been added to scisoft as of master (destined for gda-8.45)
        self.interp = create_function('interp', 'numpy', dls_module=True) # TODO: Replace with scisoft function in gda-8.46

    def __repr__(self):
        format = "EnergyScannableLookup(%r, %r, %r, %r, %r, %r, %r, %r, gap=%r, " + \
            "rowphase1=%r, rowphase2=%r, rowphase3=%r, rowphase4=%r, " + \
            "jawphase_lookup=%r)"
        return format % (self.name, self.id_gap.name,
            self.id_rowphase1.name, self.id_rowphase2.name,
            self.id_rowphase3.name, self.id_rowphase4.name,
            self.id_jawphase.name, self.pgm_energy.name,
            self.gap, self.rowphase1, self.rowphase2,
            self.rowphase3, self.rowphase4, self.jawphase_lookup)

    def getEnergy(self, idPosition):
        if idPosition.jawphase < self.jawphase_lookup_y[0]:
            raise ValueError("jawphase %r below minimum of %r" % (idPosition.jawphase, self.jawphase_lookup_y[0]))
        if idPosition.jawphase > self.jawphase_lookup_y[-1]:
            raise ValueError("jawphase %r above maximum of %r" % (idPosition.jawphase, self.jawphase_lookup_y[-1]))
        return self.interp(idPosition.jawphase, self.jawphase_lookup_y, self.jawphase_lookup_x)

    """ Annoyingly, sometimes this fails and returns the input value as it's output value!
        See I10 logs where id_energy_followermoves to pgm_energy=831.408565 (jawphase from getIdPosition 831.2583050847456!):
        2015-05-20 18:01:25,297 INFO  FollowerScannable:id_energy_follower - Moving idu_circ_pos_energy to 831.408565 (831.2583050847456)  

    def getIdPosition(self, energy_eV):
        if energy_eV < self.jawphase_lookup_x[0]:
            raise ValueError("energy_eV %r below minimum of %r" % (energy_eV, self.jawphase_lookup_x[0]))
        if energy_eV > self.jawphase_lookup_x[-1]:
            raise ValueError("energy_eV %r above maximum of %r" % (energy_eV, self.jawphase_lookup_x[-1]))
        jawphase = self.interp(energy_eV, self.jawphase_lookup_x, self.jawphase_lookup_y)
        return IdPosition(self.gap, self.rowphase1, self.rowphase2, self.rowphase3, self.rowphase4, jawphase)
"""
    def getIdPosition(self, energy_eV):
        below=above=None
        for key in sorted(self.jawphase_lookup.iterkeys()):
            #print "energy_eV = %r, key = %r" % (energy_eV, key)
            if key <= energy_eV:
                below = key
            if above == None and key >= energy_eV:
                above = key
        #print "energy_ev = %r, above = %r, below=%r" % (energy_eV, above, below)
        if below == None:
            raise ValueError("energy_eV %r below minimum of %r" % (energy_eV, sorted(self.jawphase_lookup.iterkeys())[0]))
        if above == None:
            raise ValueError("energy_eV %r above maximum of %r" % (energy_eV, sorted(self.jawphase_lookup.iterkeys(), reverse=True)[0]))
        if above == below:
            jawphase = self.jawphase_lookup[below]
            #print "jawphase = %r" % (jawphase)
        else:
            a, b = self.jawphase_lookup[above], self.jawphase_lookup[below]
            slope = (a-b)/(above-below)
            jawphase = b + slope*(energy_eV-below)
            #print "jawphase = %r (lookup above=%r, lookup below=%r, slope=%r)" % (jawphase, a, b, slope)
        return IdPosition(self.gap, self.rowphase1, self.rowphase2, self.rowphase3, self.rowphase4, jawphase)

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
