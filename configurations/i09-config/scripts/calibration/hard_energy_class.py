from gda.device.scannable import ScannableMotionBase
import gda.factory.Finder as Finder
import sys
import math
from time import sleep
from LookupTables import readLookupTable
from gda.device.scannable.scannablegroup import ScannableGroupNamed
from gda.configuration.properties import LocalProperties
import logging
from gdascripts.utils import caput
logger = logging.getLogger('__main__')


class HardEnergy(ScannableMotionBase):
    """
    Create beam energy scannable that encapsulates and fan-outs control to
    ID gap and DCM energy.

    This pseudo device requies a lookup table object to provide ID
    parameters for calculation of ID gap from beam energy required
    and harmonic order. The lookup table object must be created before
    the instance creation of this class.
    The child scannables or pseudo devices must exist in jython's global
    namespace prior to any method call of this class instance.
    The lookup Table object is described by gda.function.LookupTable
    class.
    """

    def __init__(self, name, lut, gap_offset=None, feedbackPVs=None):
        """
        Constructor - Only succeeds if it finds the lookup table,
        otherwise raises exception.
        """
        finder = Finder.getInstance()
        self.lut = readLookupTable(LocalProperties.get("gda.config")
                                   + "/lookupTables/" + lut)
        self.gap = "igap"
        self.dcm = "dcmenergy"
        self.lambdau = 27  # undulator period
        self.scannableNames = ["dcmenergy", "igap"]
        self.scannables = ScannableGroupNamed(name,[finder.find(x) for x in self.scannableNames])
        self.detune=gap_offset
        self.feedbackPVs=feedbackPVs
        self._busy = 0
        self.setName(name)
        self.setLevel(3)
        self.setOutputFormat(["%10.6f"])
        self.inputNames = [name]
        self.order = 3
        self.SCANNING=False
        self.logger = logger.getChild(self.__class__.__name__)

    def harmonicEnergyRanges(self):
        """
        Prints out a table of harmonics with corresponding min
        and max energies
        """
        print ("%s\t%s\t%s" % ("Harmonic", "Min Energy", "Max Energy"))
        keys = [int(key) for key in self.lut.keys()]
        for key in sorted(keys):
            print ("%8.0d\t%10.2f\t%10.2f" % (key, self.lut[key][2],
                                              self.lut[key][3]))

    def energyRangeForOrder(self, order):
        """Returns a tuple with min and max energies for a harmonic order

        Args:
            order (int): The order of the harmonic

        Returns:
            (min_energy, max_energy) (tuple)
        """
        return (self.lut[order][2], self.lut[order][3])

    def setOrder(self, n):
        """Method to set the harmonic order"""
        self.order = n

    def getOrder(self):
        """Method to retrieve the harmonic order"""
        return self.order

    def idgap(self, Ep, n):
        """
        Function to calculate the insertion device gap

        Arguments:
        Ep -- Energy
        n  -- order
        """
        lambdaU = self.lambdau
        M = 4
        h = 16
        me = 0.510999
        gamma = 1000 * self.lut[n][0] / me
        Ksquared = (4.959368e-6 * (n * gamma * gamma / (lambdaU * Ep)) - 2)
        if Ksquared < 0:
            raise ValueError("Ksquared must be positive!")
        K = math.sqrt(Ksquared)
        A = ((2 * 0.0934 * lambdaU * self.lut[n][1] * M / math.pi) * math.sin(math.pi / M)
             * (1 - math.exp(-2 * math.pi * h / lambdaU)))
        gap = (lambdaU / math.pi) * math.log(A / K) + self.lut[n][6]
        self.logger.debug("Required gap calculated to be {}".format(gap))

        return gap

    def rawGetPosition(self):
        """Returns the current position of the beam energy."""
        return self.scannables.getGroupMember(self.scannableNames[0]).getPosition()
    
    def calc(self, energy, order):
        return self.idgap(energy, order)

    def moveDevices(self, energy, gap):
        for scannable in self.scannables.getGroupMembers():
            if scannable.getName() == self.gap:
                try:
                    if self.detune:
                        gap = gap + float(self.detune.getPosition())
                    scannable.asynchronousMoveTo(gap)
                except:
                    print "cannot set " + scannable.getName() + " to " + str(gap)
                    raise
            elif scannable.getName() == self.dcm:
                try:
                    scannable.asynchronousMoveTo(energy) # Allow time for s to become busy
                    sleep(0.1)
                except:
                    print "cannot set " + scannable.getName() + " to " + str(energy)
                    raise

    def rawAsynchronousMoveTo(self, new_position):
        """
        move beam energy to specified value.
        In the background this moves both ID gap and Mono Bragg to the values
        corresponding to this energy. If a child scannable can not be reached
        for whatever reason, it just prints out a message, then continue to next.
        """
        min_energy, max_energy = self.energyRangeForOrder(self.order)
        energy = float(new_position)
        self.logger.debug(("rawAsynchronousMoveTo called for energy {}. "
                           "min_energy for order is: {}, max_energy is: {}")
                          .format(energy, min_energy, max_energy))
        gap = 7
        try:
            gap = self.idgap(energy, self.order)
        except:
            raise
        if not min_energy < energy < max_energy:
            raise ValueError(("Requested photon energy {} is out of range for "
                              "harmonic {}: min: {}, max: {}")
                             .format(energy, self.order, min_energy, max_energy))
            
        if self.feedbackPVs is not None and not self.SCANNING:
            caput(self.feedbackPVs[0], 1)
            caput(self.feedbackPVs[1], 1)
            self.moveDevices(energy, gap)
            self.waitWhileBusy()
            caput(self.feedbackPVs[0], 0)
            caput(self.feedbackPVs[1], 0)
        else:
            self.moveDevices(energy, gap)

    def rawIsBusy(self):
        """
        Checks the busy status of all child scannable.

        If and only if all child scannable are done this will be set to False.
        """
        self._busy = 0
        for scannable in self.scannables.getGroupMembers():
            try:
                self._busy += scannable.isBusy()
            except:
                self.logger.error(scannable.getName() + "isBusy() method threw exception:",
                                  exc_info=True)
                raise
        if self._busy == 0:
            return 0
        else:
            return 1

    def toString(self):
        """formats what to print to the terminal console."""
        return self.name + " : " + str(self.rawGetPosition())

    def atScanStart(self):
        self.SCANNING=True
        if self.feedbackPVs is not None:
            #during scan, stop feedback
            caput(self.feedbackPVs[0], 1)
            caput(self.feedbackPVs[1], 1)
            
    def atScanEnd(self):
        self.SCANNING=False
        if self.feedbackPVs is not None:
            #restore feedback
            caput(self.feedbackPVs[0], 0)
            caput(self.feedbackPVs[1], 0)

