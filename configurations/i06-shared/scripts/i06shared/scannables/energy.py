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

    def __init__(self, name, denergy, uenergy, duenergy, iddgap, idugap, smode, pol, defaultenergy=400.0):
        '''
        Constructor - default energy is set to 400.0 eV
        '''
        self.setName(name)
        self.denergy=denergy
        self.uenergy=uenergy
        self.duenergy=duenergy
        self.iddgap=iddgap
        self.idugap=idugap
        self.smode=smode
        self.pol=pol
        self.energy=defaultenergy
        self.dgap=0.0
        self.ugap=0.0
        
    def getPosition(self):
        ''' get X-ray beam energy from EPICS
        '''
        mode=self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            position = float(self.denergy.getPosition())
            self.dgap= float(self.iddgap.getPosition())
        elif mode == SourceMode.SOURCE_MODES[1]:
            position = float(self.uenergy.getPosition())
            self.ugap= float(self.idugap.getPosition())
        elif mode == SourceMode.SOURCE_MODES[2]:
            position = float(self.duenergy.getPosition())
            self.dgap = float(self.iddgap.getPosition())
            self.ugap = float(self.idugap.getPosition())
        elif mode == SourceMode.SOURCE_MODES[3]:
            pol=self.pol.getPosition()
            if pol == Polarisation.POLARISATIONS[0] or pol == Polarisation.POLARISATIONS[2]:
                position = float(self.denergy.getPosition())
                self.dgap= float(self.iddgap.getPosition())
            elif pol == Polarisation.POLARISATIONS[1] or pol == Polarisation.POLARISATIONS[3]:
                position = float(self.uenergy.getPosition())
                self.ugap= float(self.idugap.getPosition())
            elif pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.energy=position       
        return self.energy
    
    def asynchronousMoveTo(self, value):
        '''set X-ray beam energy
        '''
        newenergy=float(value)
        mode=self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            self.denergy.asynchronousMoveTo(newenergy)
        elif mode == SourceMode.SOURCE_MODES[1]:
            self.uenergy.asynchronousMoveTo(newenergy)
        elif mode == SourceMode.SOURCE_MODES[2]:
            self.duenergy.asynchronousMoveTo(newenergy)
        elif mode == SourceMode.SOURCE_MODES[3]:
            pol=self.pol.getPosition()
            if pol == Polarisation.POLARISATIONS[0] or pol == Polarisation.POLARISATIONS[2]:
                self.denergy.asynchronousMoveTo(newenergy)
            elif pol == Polarisation.POLARISATIONS[1] or pol == Polarisation.POLARISATIONS[3]:
                self.uenergy.asynchronousMoveTo(newenergy)
            elif pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.energy=newenergy
        
    def isBusy(self):
        return self.denergy.isBusy() or self.uenergy.isBusy() or self.duenergy.isBusy()
    