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
        self.dgap=None
        self.ugap=None
        self.offhar=offhar
        self.tolerance=PositionTolerance
        
    def setOffhar(self,offset):
        haroff=float(offset)
        mode = self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            if self.dgap is None:
                self.getPosition()
            if abs(self.dgap - float(self.iddgap.getPosition()))<=self.tolerance+self.offhar:
                self.iddgap.asynchronousMoveTo(self.dgap+haroff)
            else:
                print "IDD gap is not at the energy %f! Please set energy again before applying harmonic offset." % (self.energy)
        elif mode == SourceMode.SOURCE_MODES[1]:
            if self.ugap is None:
                self.getPosition()
            if abs(self.ugap - float(self.idugap.getPosition()))<=self.tolerance+self.offhar:
                self.idugap.asynchronousMoveTo(self.ugap+haroff)
            else:
                print "IDU gap is not at the energy %f! Please set energy again before applying harmonic offset." % (self.energy)
        elif mode == SourceMode.SOURCE_MODES[2]:
            if self.dgap is None:
                self.getPosition()
            if abs(self.dgap - float(self.iddgap.getPosition()))<=self.tolerance+self.offhar:
                self.idddgap.asynchronousMoveTo(self.dgap+haroff)
            else:
                print "IDD gap is not at the energy %f! Please set energy again before applying harmonic offset." % (self.energy)
            if self.ugap is None:
                self.getPosition()
            if abs(self.ugap - float(self.idugap.getPosition()))<=self.tolerance+self.offhar:
                self.idugap.asynchronousMoveTo(self.ugap+haroff)
            else:
                print "IDU gap is not at the energy %f! Please set energy again before applying harmonic offset." % (self.energy)
        elif mode == SourceMode.SOURCE_MODES[3]:
            pol=self.pol.getPosition()
            if pol == Polarisation.POLARISATIONS[0] or pol == Polarisation.POLARISATIONS[2]:
                if abs(self.dgap - float(self.iddgap.getPosition()))<=self.tolerance+self.offhar:
                    self.iddgap.asynchronousMoveTo(self.dgap+haroff)
                else:
                    print "IDD gap is not at the energy %f! Please set energy again before applying harmonic offset." % (self.energy)
            elif pol == Polarisation.POLARISATIONS[1] or pol == Polarisation.POLARISATIONS[3]:
                if abs(self.ugap - float(self.idugap.getPosition()))<=self.tolerance+self.offhar:
                    self.idugap.asynchronousMoveTo(self.ugap+haroff)
                else:
                    print "IDU gap is not at the energy %f! Please set energy again before applying harmonic offset." % (self.energy)
            elif pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.offhar=haroff
        
    def getOffhar(self):
        mode = self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            position = float(self.iddgap.getPosition())
            haroff=position-self.dgap
        elif mode == SourceMode.SOURCE_MODES[1]:
            position = float(self.idugap.getPosition())
            haroff=position-self.ugap
        elif mode == SourceMode.SOURCE_MODES[2]:
            position = float(self.iddgap.getPosition())
            haroff = position-self.dgap            
        elif mode == SourceMode.SOURCE_MODES[3]:
            pol=self.pol.getPosition()
            if pol == Polarisation.POLARISATIONS[0] or pol == Polarisation.POLARISATIONS[2]:
                position = float(self.iddgap.getPosition())
                haroff = position - self.dgap
            elif pol == Polarisation.POLARISATIONS[1] or pol == Polarisation.POLARISATIONS[3]:
                position = float(self.idugap.getPosition())
                haroff = position - self.ugap
            elif pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        self.offhar=haroff
        return self.offhar

        
    def isHaroffBusy(self):
        mode = self.smode.getPosition()
        if mode == SourceMode.SOURCE_MODES[0]:
            return self.iddgap.isBusy()
        elif mode == SourceMode.SOURCE_MODES[1]:
            return self.idugap.isBusy()
        elif mode == SourceMode.SOURCE_MODES[2]:
            return self.iddgap.isBusy() or self.idugap.isBusy()
        elif mode == SourceMode.SOURCE_MODES[3]:
            pol=self.pol.getPosition()
            if pol == Polarisation.POLARISATIONS[0] or pol == Polarisation.POLARISATIONS[2]:
                return self.iddgap.isBusy()
            elif pol == Polarisation.POLARISATIONS[1] or pol == Polarisation.POLARISATIONS[3]:
                return self.idugap.isBusy()
            elif pol == Polarisation.POLARISATIONS[4]:
                message="Linear Polarisation is not supported in '%s' source mode" % (mode)
                raise RuntimeError(message)
        return self.iddgap.isBusy() or self.idugap.isBusy()
        
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
    