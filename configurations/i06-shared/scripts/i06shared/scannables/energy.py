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

    def __init__(self, name, denergy, uenergy, duenergy, iddgap, idugap, smode, pol, offhar=0.0, PositionTolerance=0.0001, defaultenergy=400.0):
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
        self.offhar=offhar
        self.tolerance=PositionTolerance
        
    def setOffhar(self,offset):
        haroff=float(offset)
        mode = self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            if abs(self.energy.dgap - float(self.dgap.getPosition()))<=self.tolerance+self.offhar:
                self.dgap.asynchronousMoveTo(self.energy.dgap+haroff)
            else:
                print "ID gap is not at the energy %f! Please update energy again before applying harmonic offset."
        elif mode == SourceMode.SOURCE_MODES[1]:
            if abs(self.energy.ugap - float(self.ugap.getPosition()))<=self.tolerance+self.offhar:
                self.ugap.asynchronousMoveTo(self.energy.ugap+haroff)
            else:
                print "ID gap is not at the energy %f! Please update energy again before applying harmonic offset."
        elif mode == SourceMode.SOURCE_MODES[3]:
            if abs(self.energy.dgap - float(self.dgap.getPosition()))<=self.tolerance+self.offhar:
                self.dgap.asynchronousMoveTo(self.energy.dgap+haroff)
            else:
                print "ID gap is not at the energy %f! Please update energy again before applying harmonic offset."
            if abs(self.energy.ugap - float(self.ugap.getPosition()))<=self.tolerance+self.offhar:
                self.ugap.asynchronousMoveTo(self.energy.ugap+haroff)
            else:
                print "ID gap is not at the energy %f! Please update energy again before applying harmonic offset."
        elif mode == SourceMode.SOURCE_MODES[3]:
            pol=self.pol.getPosition()
            if pol == Polarisation.POLARISATIONS[0] or pol == Polarisation.POLARISATIONS[2]:
                if abs(self.energy.dgap - float(self.dgap.getPosition()))<=self.tolerance+self.offhar:
                    self.dgap.asynchronousMoveTo(self.energy.dgap+haroff)
                else:
                    print "ID gap is not at the energy %f! Please update energy again before applying harmonic offset."
            elif pol == Polarisation.POLARISATIONS[1] or pol == Polarisation.POLARISATIONS[3]:
                if abs(self.energy.ugap - float(self.ugap.getPosition()))<=self.tolerance+self.offhar:
                    self.ugap.asynchronousMoveTo(self.energy.ugap+haroff)
                else:
                    print "ID gap is not at the energy %f! Please update energy again before applying harmonic offset."
            elif pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.offhar=haroff
        
    def getOffhar(self):
        mode = self.smode.getPosition()
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
            pol=self.pol.getPosition()
            if pol == Polarisation.POLARISATIONS[0] or pol == Polarisation.POLARISATIONS[2]:
                position = float(self.dgap.getPosition())
                haroff = position - self.energy.dgap
            elif pol == Polarisation.POLARISATIONS[1] or pol == Polarisation.POLARISATIONS[3]:
                position = float(self.ugap.getPosition())
                haroff = position - self.energy.ugap
            elif pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.offhar=haroff
        return self.offhar

        
    def isHaroffBusy(self):
        return self.dgap.isBusy() or self.ugap.isBusy()
        
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
        self.offhar=0.0
        self.energy=newenergy
        
    def isBusy(self):
        return self.denergy.isBusy() or self.uenergy.isBusy() or self.duenergy.isBusy()
    