'''
A single 'energy' scannable that controls source energy of X-ray beam.

It records and stores cached ID gaps for the specified energy which are used to offset harmonics.  
Created on 21 Apr 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from i06shared.scannables.sourceModes import SourceMode
from i06shared.scannables.polarisation import Polarisation

class CombinedEnergy(ScannableBase):
    '''
    scannable delegates energy control to different energy scannables based on source mode and polaristaion mode.
    '''

    def __init__(self, name, iddgap, idugap, drpenergy, urpenergy, pgmenergy, smode, pol, offhar, detune=100.0, opengap=100.0):
        '''
        Constructor - default energy is set to 400.0 eV
        '''
        self.setName(name)
        self.iddgap=iddgap
        self.idugap=idugap
        self.drpenergy=drpenergy
        self.urpenergy=urpenergy
        self.pgmenergy=pgmenergy
        self.smode=smode
        self.pol=pol
        self.offhar=offhar
        self.detune=detune
        self.opengap=opengap
        self.currpol='pc'

    def setOpenGap(self, gap):
        self.opengap=gap
    
    def getOpenGap(self):
        return self.opengap
    
    def setDetune(self, val):
        self.detune=val
        
    def getDetune(self):
        return self.detune
    
    def getPosition(self):
        ''' get X-ray beam energy from EPICS
        '''
        return float(self.pgmenergy.getPosition())
    
    def asynchronousMoveTo(self, value):
        '''set X-ray beam energy
        '''
        newenergy=float(value)
        mode=self.smode.getPosition()
        offhar=float(self.offhar.getPosition())
        self.currpol=self.pol.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            self.drpenergy.asynchronousMoveTo(newenergy+offhar)
            self.idugap.asynchronousMoveTo(self.opengap)
        elif mode == SourceMode.SOURCE_MODES[1]:
            self.urpenergy.asynchronousMoveTo(newenergy+offhar)
            self.iddgap.asynchronousMoveTo(self.opengap)
        elif mode == SourceMode.SOURCE_MODES[2]:
            self.drpenergy.asynchronousMoveTo(newenergy+offhar)
            self.urpenergy.asynchronousMoveTo(newenergy+offhar)
        elif mode == SourceMode.SOURCE_MODES[3]:
            if self.currpol == Polarisation.POLARISATIONS[0] or self.currpol == Polarisation.POLARISATIONS[2]:
                self.drpenergy.asynchronousMoveTo(newenergy+offhar)
                self.urpenergy.asynchronousMoveTo(newenergy+self.detune)
            elif self.currpol == Polarisation.POLARISATIONS[1] or self.currpol == Polarisation.POLARISATIONS[3]:
                self.drpenergy.asynchronousMoveTo(newenergy+self.detune)
                self.urpenergy.asynchronousMoveTo(newenergy+offhar)
            elif self.currpol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.pgmenergy.asynchronousMoveTo(newenergy)

        
    def isBusy(self):
        mode=self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            return self.drpenergy.isBusy() or self.idugap.isBusy() or self.pgmenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[1]:
            return self.urpenergy.isBusy() or self.iddgap.isBusy() or self.pgmenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[2]:
            return self.drpenergy.isBusy() or self.urpenergy.isBusy() or self.pgmenergy.isBusy()
        elif mode == SourceMode.SOURCE_MODES[3]:
            if self.currpol == Polarisation.POLARISATIONS[0] or self.currpol == Polarisation.POLARISATIONS[2]:
                return self.drpenergy.isBusy() or self.urpenergy.isBusy() or self.pgmenergy.isBusy()
            elif self.currpol == Polarisation.POLARISATIONS[1] or self.currpol == Polarisation.POLARISATIONS[3]:
                return self.drpenergy.isBusy() or self.urpenergy.isBusy() or self.pgmenergy.isBusy()
            elif self.currpol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        return False
    