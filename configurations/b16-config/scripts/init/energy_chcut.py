from gda.device.scannable import ScannableBase
from gda.device.scannable import ScannableUtils
import math
from gdascripts.utils import caget


# channel cut PV that drives monochromator energy in electron volts
class EnergyChcut(ScannableBase):
    # silicon d spacing in Angstroms
    a0 = 5.4307
    # 311 reflection
    h, k, l = 3, 1, 1
    # mono d spacing in Angstroms
    dmono = a0 / math.sqrt (h*h + k*k + l*l)
    # hc/e - constant to convert wavelength (in Angstroms) to energy in eV
    const = 12398.521
    #
    pi = 4*math.atan (1.0)

    def __init__(self):
        name = 'energy_chcut'
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])

    def getPosition(self):
        """returns the mono energy in eV"""
        theta_deg = float (caget ('BL16B-OP-DCM-01:XTAL1:BRAGG.VAL'))
        theta_rad = theta_deg*self.pi/180.0
        lam = 2.0 * self.dmono * math.sin (theta_rad)
        eev = self.const / lam
        self.currentposition = eev
        return self.currentposition

    def asynchronousMoveTo(self, eev):
        """Moves mono energy to position (in eV)."""
        lam = self.const / eev
        theta_deg = 180 / self.pi * math.asin (lam / 2.0 / self.dmono)
        caput ('BL16B-OP-DCM-01:XTAL1:BRAGG.VAL', unicode(theta_deg))
        self.currentposition = eev

    def isBusy(self):
        """Returns the status of this Scannable."""
        return int (caget ('BL16B-OP-DCM-01:XTAL1:BRAGG.MOVN'))

energy_chcut = EnergyChcut()
