from gda.device.scannable import ScannableMotionBase
from time import sleep
from gdaserver import e_id_gap_lookup_table as table, idgap, dcm1energy
import logging
logger = logging.getLogger('__main__')


class Energy_Scannable(ScannableMotionBase):
    """
    Create beam energy scannable that encapsulates and fan-outs control to ID 
    gap and DCM energy.

    This pseudo device requies a lookup table object to provide ID gap and 
    energy max/min values for whichever harmonics are to be used.  The lookup 
    Table object is described by gda.function.LookupTable class, 
    which must be created before this class.
    """

    def __init__(self, name, dcm1en, id_gap):
        self.detune = 0
        self.setName(name)
        self.setLevel(3)
        self.idgap = id_gap
        self.dcm1energy = dcm1en
        self.setOutputFormat(["%10.6f", "%10.5f"])
        self.inputNames = [name]
        self.extraNames = [id_gap.getName()]
        self.order = 3
        self.logger = logger.getChild(self.__class__.__name__)

    def harmonicEnergyRanges(self):
        """
        Prints out a table of harmonics with corresponding minimum and maximum energies
        """
        print ("%s\t%s\t%s\t%s\t%s\t%s" % ("Order", "Min Energy", "Max Energy", "Min Id Gap", "Max Id Gap", "Id Gap Offset"))
        keys = table.getLookupKeys()
        for key in sorted(keys):
            print ("%8.0d\t%10.2f\t%10.2f\t%10.2f\t%10.2f\t%10.2f" % (key, table.lookupValue(key, "E_min"), table.lookupValue(key, "E_max"), table.lookupValue(key, "gap_min"), table.lookupValue(key, "gap_max"), table.lookupValue(key, "gap_offset")))

    def energyRangeForOrder(self, the_order):
        """
        Returns a tuple with min and max energies for a given harmonic order
        """
        if the_order is None :
            the_order = self.getOrder()
        
        if the_order in table.getLookupKeys() :
            return (table.lookupValue(the_order, "E_min"), table.lookupValue(the_order, "E_max"))
        else: 
            print "Harmonic order not specified in table"

    def setOrder(self, n):
        """Method to set the harmonic order"""
        if n in table.getLookupKeys() :
            self.order = n
        else :
            print "Harmonic order not specified in table"

    def getOrder(self):
        """Method to retrieve the harmonic order"""
        return self.order

    def rawGetPosition(self):
        """Returns the current position of the beam energy."""
        return self.dcm1energy.getPosition(), self.idgap.getPosition()
    
    def moveDevices(self, energy, gap):
        self.idgap.asynchronousMoveTo(gap)
        self.dcm1energy.asynchronousMoveTo(energy) 
        sleep(0.1) # Allow time for s to become busy

    def rawAsynchronousMoveTo(self, new_position):
        """
        Move beam energy to specified value, moving id gap to match.
        """
        min_energy, max_energy = self.energyRangeForOrder(self.order)
        energy = float(new_position)
        self.logger.debug(("rawAsynchronousMoveTo called for energy {}. "
                           "min_energy for order is: {}, max_energy is: {}")
                          .format(energy, min_energy, max_energy))

        if not min_energy < energy < max_energy:
            raise ValueError(("Requested photon energy {} is out of range for "
                              "harmonic {}: min: {}, max: {}")
                             .format(energy, self.order, min_energy, max_energy))

        proportion = (energy - min_energy) / (max_energy - min_energy)
        gap_min = table.lookupValue(self.order, "gap_min")
        gap_max = table.lookupValue(self.order, "gap_max")
        offset_for_order = table.lookupValue(self.order, "gap_offset")
        new_gap = gap_min + ((gap_max - gap_min)*proportion) + offset_for_order + self.detune
        
        self.moveDevices(energy, new_gap)

    def isBusy(self):
        """
        Checks the busy status of all child scannables.

        If and only if all child scannables are done this will be False.
        """
        return self.idgap.isBusy() or self.dcm1energy.isBusy()

    def toString(self):
        return self.name + " : " + str(self.rawGetPosition())

energy = Energy_Scannable("energy", dcm1energy, idgap)
