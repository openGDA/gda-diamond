'''
A scannable to be used to control the angle of X-ray beam in Linear Polarisation mode.

Created on 21 Apr 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase
from i06shared.scannables.sourceModes import SourceMode
from i06shared.scannables.polarisation import Polarisation

class LinearArbitraryAngle(ScannableBase):
    '''
    This class only works in Linear Arbitrary Polarisation mode.
    '''

    def __init__(self, name, iddlaangle, idulaangle, smode, pol):
        '''
        Constructor
        '''
        self.setName(name)
        self.dlaangle=iddlaangle
        self.ulaangle=idulaangle
        self.smode=smode
        self.pol=pol
        self.angle=0.0
        
    def getPosition(self):
        '''get the angle of Linear Polarisation from EPICS
        '''
        mode = self.smode.getPosition()
        pol = self.pol.getPosition()
        if  pol != Polarisation.POLARISATIONS[4]:
            message="Angle is not available in polarisation %s in source mode %s" % (pol, mode)
            raise RuntimeError(message)
        if mode==SourceMode.SOURCE_MODES[0]:
            angle=self.dlaangle.getPosition()
        elif mode==SourceMode.SOURCE_MODES[1]:
            angle=self.ulaangle.getPosition()
        elif mode==SourceMode.SOURCE_MODES[2]:
            angle=self.dlaangle.getPosition()
        elif mode==SourceMode.SOURCE_MODES[3]:
            message="Angle not available: Linear Polarisation is not supported in '%s' source mode" % (mode)
            raise RuntimeError(message)
        self.angle=float(angle)
        return self.angle
    
    def asynchronousMoveTo(self, angle):
        '''set the angle for the Linear Polarisation of the X-ray source
        '''
        newangle=float(angle)
        mode = self.smode.getPosition()
        pol=self.pol.getPosition()
        if  pol != Polarisation.POLARISATIONS[4]:
            message="Angle control is not available in polarisation %s in source mode %s" % (pol, mode)
            raise RuntimeError(message)
        if mode==SourceMode.SOURCE_MODES[0]:
            self.dlaangle.asynchronousMoveTo(newangle)
        elif mode==SourceMode.SOURCE_MODES[1]:
            self.ulaangle.asynchronousMoveTo(newangle)
        elif mode==SourceMode.SOURCE_MODES[2]:
            self.dlaangle.asynchronousMoveTo(newangle)
            self.ulaangle.asynchronousMoveTo(newangle)
        elif mode==SourceMode.SOURCE_MODES[3]:
            message="Angle control is not available: Linear Polarisation is not supported in '%s' source mode" % (mode)
            raise RuntimeError(message)
        self.angle=newangle
        
    def isBusy(self):
        return self.dlaangle.isBusy() or self.ulaangle.isBusy()
    
        
            