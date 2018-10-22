'''
Scannable to offset ID harmonic at current energy of the X-ray beam.

Created on 21 Apr 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from i06shared.scannables.sourceModes import SourceMode
from i06shared.scannables.polarisation import Polarisation
from scisoftpy.jython.fitcore import poly1d

class HarmonicOffset(ScannableBase):
    '''
    offset current energy harmonic.
    '''


    def __init__(self, name, smode, dpol,upol, drpenergy, urpenergy, pgmenergy, offhar=0.0):
        '''
        Constructor - delegate to energy to handle harmonic offset.
        '''
        self.setName(name)
        self.smode=smode
        self.dpol=dpol
        self.upol=upol
        self.drpenergy=drpenergy
        self.urpenergy=urpenergy
        self.pgmenergy=pgmenergy
        self.offhar=offhar
        self.polscannable=None
        self.pol='pc'

    def setPolScannable(self, pol):
        self.polscannable=pol
    
    def getPolScannable(self):
        return self.polscannable
    
    def asynchronousMoveTo(self,offset):
        haroff=float(offset)
        mode = self.smode.getPosition()
        energy=float(self.pgmenergy.getPosition())
        self.pol = self.polscannable.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            self.drpenergy.asynchronousMoveTo(energy+haroff)
        elif mode == SourceMode.SOURCE_MODES[1]:
            self.urpenergy.asynchronousMoveTo(energy+haroff)
        elif mode == SourceMode.SOURCE_MODES[2]:
            self.drpenergy.asynchronousMoveTo(energy+haroff)
            self.urpenergy.asynchronousMoveTo(energy+haroff)
        elif mode == SourceMode.SOURCE_MODES[3]:
            if self.pol == Polarisation.POLARISATIONS[0] or self.pol == Polarisation.POLARISATIONS[2]:
                self.drpenergy.asynchronousMoveTo(energy+haroff)
            elif self.pol == Polarisation.POLARISATIONS[1] or self.pol == Polarisation.POLARISATIONS[3]:
                self.urpenergy.asynchronousMoveTo(energy+haroff)
            elif self.pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.offhar=haroff
        
    def getPosition(self):
        return self.offhar
                 
    def isBusy(self):
        mode = self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            return self.drpenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[1]:
            return self.urpenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[2]:
            return self.drpenergy.isBusy() or self.urpenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[3]:
            if self.pol == Polarisation.POLARISATIONS[0] or self.pol == Polarisation.POLARISATIONS[2]:
                return self.drpenergy.isBusy()
            elif self.pol == Polarisation.POLARISATIONS[1] or self.pol == Polarisation.POLARISATIONS[3]:
                return self.urpenergy.isBusy()
            elif self.pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        return False
           
        