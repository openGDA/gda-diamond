from gda.device.scannable import ScannableMotionBase
import gda.factory.Finder as Finder
import sys
from time import sleep
from LookupTables import readLookupTable
from gda.device.scannable.scannablegroup import ScannableGroup
from gda.configuration.properties import LocalProperties
import logging
logger = logging.getLogger('__main__')

class SoftEnergy(ScannableMotionBase):
    """
    Create beam energy scannable that encapsulates and fan-outs control to
    ID gap and DCM energy.

    This pseudo device requires a lookup table object to provide allowed energy ranges.
    However The lookup table object must be created before
    the instance creation of this class.
    Equations to calculate insertion device gaps are hard-coded into this class.
    The child scannables or pseudo devices must exist in Jython's global
    namespace prior to any method call of this class instance.
    The lookup Table object is described by gda.function.LookupTable
    class.
    """

    def __init__(self, name, lut):
        """
        Constructor -
        Only succeeds if it finds the lookup table, otherwise raises exception.
        """
        finder = Finder.getInstance()
        self.lut = readLookupTable(LocalProperties.get("gda.config") + "/lookupTables/" + lut)
        self.gap = 'jgap'
        self.dcm = "pgmenergy"
        self.scannableNames = ["pgmenergy", "jgap"]
        self.scannables = ScannableGroup(name, [finder.find(x) for x in self.scannableNames])
        self._busy = 0
        self.setName(name)
        self.setLevel(3)
        self.setOutputFormat(["%10.6f"])
        self.inputNames = [name]
        self.order = 1
        self.polarisation = 'LH'
        self.jidphase = finder.find("jidphase")
        self.logger = logger.getChild(self.__class__.__name__)

    def setPolarisation(self, value):
        """Sets the polarisation."""
        if value == "LH":
            self.jidphase.hortizontal()
            self.polarisation = value
        elif value == "LH3":
            self.jidphase.hortizontal() 
            self.polarisation=value
        elif value == "LV":
            self.jidphase.vertical()
            self.polarisation = value
        elif value == "CL":
            self.jidphase.circular_left()
            self.polarisation = value
        elif value == "CR":
            self.jidphase.circular_right()
            self.polarisation = value
        else:
            raise ValueError("Input " + str(value) + " invalid. Valid values are 'LH', 'LV', 'CL' and 'CR'.")

        # Move back to the current position i.e. the correct gap for the new polarisation
        # Note this also causes the ID to actually move, if the gap demand is exactly the same it will never!
        self.asynchronousMoveTo(self.getPosition())
        while (self.isBusy()) :
            sleep(0.5)

    def getPolarisation(self):
        """Returns the current polarisation (cached in object not directly from EPICS)"""
        return self.polarisation 

    def harmonicEnergyRanges(self):
        """Prints out a table of harmonics with corresponding min and max energies"""
        print ("%s\t%s\t%s" % ("Harmonic", "Min Energy", "Max Energy"))
        keys = [int(key) for key in self.lut.keys()]
        for key in sorted(keys):
            print ("%8.0d\t%10.2f\t%10.2f" % (key, self.lut[key][2], self.lut[key][3]))

    def energyRangeForOrder(self, order):
        """Returns a tuple with min and max energies for a harmonic order

        Args:
            order (int): The order of the harmonic

        Returns:
            (min_energy, max_energy) (tuple)
        """
        return (self.lut[order][2], self.lut[order][3])

    def idgap(self, Ep, n):
        """
        Function to calculate the insertion device gap

        Arguments:
        Ep -- Energy
        n  -- order
        """
        gap = 20.0
        self.logger.debug("'idgap' function called with energy {} and order {}"
                          .format(Ep, n))
        self.logger.debug("Current cached polarisation is {}"
                          .format(self.polarisation))
        # Soft ID J branch
        # Linear Horizontal
        if self.getPolarisation() == "LH":
            if (Ep < 0.104 or Ep > 1.2):
                raise ValueError("Polarisation = LH  but the demanding energy is outside the valid range between 0.104 and 1.2 keV!")
#            gap=3.06965 +177.99974*Ep -596.79184*Ep**2 +1406.28911*Ep**3 -2046.90669*Ep**4 +1780.26621*Ep**5 -844.81785*Ep**6 +168.99039*Ep**7
#            gap=2.75529 + 184.24255*Ep - 639.07279*Ep**2 +1556.23192*Ep**3 -2340.01233*Ep**4 +2100.81252*Ep**5 -1027.88771*Ep**6 +211.47063*Ep**7
 	    gap=0.52071 + 238.56372*Ep - 1169.06966*Ep**2 +4273.03275*Ep**3 -10497.36261*Ep**4 +17156.91928*Ep**5 -18309.05195*Ep**6 +12222.50318*Ep**7 -4623.70738*Ep**8 +755.90853*Ep**9
            if (gap < 16 or gap > 60):
                raise ValueError("Required Soft X-Ray ID gap is out side allowable bound (16, 60)!")


        # Linear Horizontal 3rd Harmonic for 400 line/mm grating
        elif (self.getPolarisation()=="LH3"):
            if (Ep<0.7 or Ep > 1.95):
                raise ValueError("Polarisation = LH3  but the demanding energy is outside the valid range between 0.7 and 1.9 keV!")
            gap=10.98969 + 25.8301*Ep - 9.36535*Ep**2 + 1.74461*Ep**3
            if (gap < 16 or gap > 60):
                raise ValueError("Required Soft X-Ray ID gap is out side allowable bound (16, 60)!")

        # Linear Vertical
        elif self.getPolarisation() == "LV":
            if (Ep < 0.22 or Ep > 1.0):
                raise ValueError("Demanding energy must lie between 0.22 and 1.0 eV!")
            gap = (5.33595 + 72.53678 * Ep - 133.96826 * Ep ** 2 + 179.99229 * Ep ** 3
                   - 128.83048 * Ep ** 4 + 39.34346 * Ep ** 5)
            if (gap < 16.01 or gap > 60):
                raise ValueError("Required Soft X-Ray ID gap is out side allowable bound (16, 60)!")

        # Circular left
        elif self.getPolarisation() == "CL":
            if (Ep < 0.145 or Ep > 1.2):
                raise ValueError("Demanding energy must lie between 0.146 and 1.2 eV!")
            # Circular left gap polymonimal
            gap = (5.32869 + 101.28316 * Ep - 192.74788 * Ep ** 2 + 249.91788 * Ep ** 3
                   - 167.93323 * Ep ** 4 + 47.22008 * Ep ** 5 - 0.054 * Ep - .0723)

            # Check the gap is possible
            if (gap < 16.01 or gap > 60):
                raise ValueError("Required Soft X-Ray ID gap is out side allowable bound (16, 60)!")

        # Circular right
        elif self.getName() == "jenergy" and self.getPolarisation() == "CR":
            if (Ep < 0.145 or Ep > 1.2):
                raise ValueError("Demanding energy must lie between 0.1 and 1.2 eV!")
            # Circular right gap polymonimal
            gap = (5.32869 + 101.28316 * Ep - 192.74788 * Ep ** 2 + 249.91788 * Ep ** 3
                   - 167.93323 * Ep ** 4 + 47.22008 * Ep ** 5)

            # Check the gap is possible
            if (gap < 16.01 or gap > 60):
                raise ValueError("Required Soft X-Ray ID gap is out side allowable bound (16, 60)!")

        # Unsupported
        else:
            raise ValueError("Unsupported scannable or polarisation mode")
        return gap

    def rawGetPosition(self):
        """returns the current position of the beam energy."""
        return self.scannables.getGroupMember(self.scannableNames[0]).getPosition()/1000.0

    def calc(self, energy, order):
        return self.idgap(energy, order)

    def rawAsynchronousMoveTo(self, new_position):
        """
        move beam energy to specified value.
        At the background this moves both ID gap and Mono Bragg to the values corresponding to this energy.
        If a child scannable can not be reached for whatever reason, it just prints out a message, then continue to next.
        """
        energy = float(new_position)
        gap = self.idgap(energy, self.order)

        for s in self.scannables.getGroupMembers():
            if s.getName() == self.gap:
                try:
                    self.logger.debug("Calling asynchronousMoveTo() on {} with gap {}"
                                      .format(s.getName(), gap))
                    s.asynchronousMoveTo(gap)
                except:
                    self.logger.error("cannot set " + s.getName() + " to " + str(gap), exc_info=True)
                    raise
            else:
                try:
                    self.logger.debug("Calling asynchronousMoveTo() on {} with energy {}"
                                      .format(s.getName(), energy * 1000))
                    s.asynchronousMoveTo(energy * 1000)
                    # Allow time for s to become busy
                    sleep(0.1)
                except:
                    self.logger.error("Can not set " + s.getName() + " to " + str(energy), exc_info=True)
                    raise

    def rawIsBusy(self):
        """
        checks the busy status of all child scannable.

        If and only if all child scannable are done this will be set to False.
        """
        self._busy = 0
        for s in self.scannables.getGroupMembers():
            try:
                self._busy += s.isBusy()
            except:
                print s.getName() + " isBusy() throws exception ", sys.exc_info()
                raise
        if self._busy == 0:
            return 0
        else:
            return 1

    def toString(self):
        """formats what to print to the terminal console."""
        return self.name + " : " + str(self.rawGetPosition())
