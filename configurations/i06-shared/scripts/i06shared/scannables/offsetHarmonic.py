'''
Scannable to offset harmonic at current energy of the X-ray beam.

Created on 21 Apr 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from i06shared.scannables.sourceModes import SourceMode
from i06shared.scannables.polarisation import Polarisation

class HarmonicOffset(ScannableBase):
    '''
    offset current energy harmonic.
    '''


    def __init__(self, name, iddgap, idugap, smode, pol, energy, defaultharoff=0.0):
        '''
        Constructor - default harmonic offset is 0.0
        '''
        self.setName(name)
        self.dgap=iddgap
        self.ugap=idugap
        self.smode=smode
        self.pol=pol
        self.energy=energy
        self.haroff=defaultharoff
        
    def getPosition(self):
        mode = self.smode.getPosition()
        pol=self.pol.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            position = float(self.dgap.getPosition())
            haroff=position-self.energy.dgap
        elif mode == SourceMode.SOURCE_MODES[1]:
            position = float(self.ugap.getPosition())
            haroff=position-self.energy.ugap
        elif mode == SourceMode.SOURCE_MODES[3]:
            position = float(self.dgap.getPosition())
            haroff = position-self.energy.dgap            
        elif mode == SourceMode.SOURCE_MODES[3]:
            if pol == Polarisation.POLARISATIONS[0] or pol == Polarisation.POLARISATIONS[2]:
                position = float(self.dgap.getPosition())
                haroff = position - self.energy.dgap
            elif pol == Polarisation.POLARISATIONS[1] or pol == Polarisation.POLARISATIONS[3]:
                position = float(self.ugap.getPosition())
                haroff = position - self.energy.ugap
            elif pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.haroff=haroff
        return self.haroff
    
    def asynchronousMoveTo(self, value):
        haroff=float(value)
        mode = self.smode.getPosition()
        pol=self.pol.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            self.dgap.asynchronousMoveTo(self.energy.dgap+haroff)
        elif mode == SourceMode.SOURCE_MODES[1]:
            self.ugap.asynchronousMoveTo(self.energy.ugap+haroff)
        elif mode == SourceMode.SOURCE_MODES[3]:
            self.dgap.asynchronousMoveTo(self.energy.dgap+haroff)
            self.ugap.asynchronousMoveTo(self.energy.ugap+haroff)
        elif mode == SourceMode.SOURCE_MODES[3]:
            if pol == Polarisation.POLARISATIONS[0] or pol == Polarisation.POLARISATIONS[2]:
                self.dgap.asynchronousMoveTo(self.energy.dgap+haroff)
            elif pol == Polarisation.POLARISATIONS[1] or pol == Polarisation.POLARISATIONS[3]:
                self.ugap.asynchronousMoveTo(self.energy.ugap+haroff)
            elif pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.haroff=haroff
                
    def isBusy(self):
        return self.dgap.isBusy() or self.ugap.isBusy()        
                
           
        