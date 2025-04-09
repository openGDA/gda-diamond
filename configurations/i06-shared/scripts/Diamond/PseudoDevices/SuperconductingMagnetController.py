'''
class that implements support for the Superconducting Magnet Controller
Created on 19 Dec 2024

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class SuperconductingMagnetControllerClass(ScannableMotionBase):
    '''
    implements support for the Superconducting Magnet Controller
    '''


    def __init__(self, name, pv):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.chin = CAClient(pv + ':SET:DMD:RAMPRATE:TPM')
        self.chout = CAClient(pv + ':STS:RAMPRATE:TPM')
        self.chlimit = CAClient(pv + ':LIM:RAMPRATE:TPM')
        self._myBusy = False
        
    def configure(self):
        if self.isConfigured():
            return
        if not self.chin.isConfigured():
            self.chin.configure()
        if not self.chout.isConfigured():
            self.chout.configure()
        if not self.chlimit.isConfigured():
            self.chlimit.configure()
        self.setConfigured(True)
        
    def getPosition(self):
        self.configure()
        return float(self.chout.caget())
    
    def asynchronousMoveTo(self, val):
        self._myBusy = True
        self.configure()
        self.chin.caput(float(val))
        self._myBusy = False
        
    def isBusy(self):
        return self._myBusy
    
    def get_ramp_rate_limit(self):
        self.configure()
        return float(self.chlimit.caget())
    
magx_ramp_rate = SuperconductingMagnetControllerClass('magx_ramp_rate', 'BL06J-EA-SMC-01')
magy_ramp_rate = SuperconductingMagnetControllerClass('magy_ramp_rate', 'BL06J-EA-SMC-02')
magz_ramp_rate = SuperconductingMagnetControllerClass('magz_ramp_rate', 'BL06J-EA-SMC-03')
