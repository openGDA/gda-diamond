'''
Created on 15 Jan 2025

@author: fy65
'''

from gda.epics import CAClient
from gda.device.scannable import ScannableMotionBase
'''
BL06J-EA-MAG-01:Z:DMD
BL06J-EA-MAG-01:Z:RBV
BL06J-EA-MAG-01:Z:AI:RBV
BL06J-EA-MAG-01:STARTRAMP.PROC
BL06J-EA-MAG-01:RAMPSTATUS

BL06J-EA-SMC-03:SET:DMD:RAMPRATE:TPM
BL06J-EA-SMC-03:STS:RAMPRATE:TPM
BL06J-EA-SMC-03:LIM:RAMPRATE:TPM
'''
class MagnetFieldControl(ScannableMotionBase):
    '''
    classdocs
    '''

    def __init__(self, name, field_pv_root, axis_name, controller_pv_root):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames(["ramp_rate"])
        self.setOutputFormat(["%5.2f"])
        self.setExtraNames([])
        self.target = None
        self.ramprate = None
        self.field_dmd = CAClient(field_pv_root + ":" + axis_name + ":DMD")
        self.start_ramp = CAClient(field_pv_root + ":STARTRAMP.PROC")
        self.ramp_rate_dmd = CAClient(controller_pv_root + ":SET:DMD:RAMPRATE:TPM")
        self.ramp_rate_rdv = CAClient(controller_pv_root + ":STS:RAMPRATE:TPM")
        
    def configure(self):
        if self.isConfigured():
            return
        else:
            self.field_dmd.configure()
            self.start_ramp.configure()
            self.ramp_rate_dmd.configure()
            self.ramp_rate_rdv.configure()
            self.setConfigured(True)
    
    def atScanStart(self):
        self.start_ramp.caput(1)
        
    def rawAsynchronousMoveTo(self, fld):
        pass
    
    def rawGetPosition(self):
        return float(self.ramp_rate_rdv.caget())
    
    def rawIsBusy(self):
        return False
        
    def setRampRate(self, rate):
        self.ramprate = rate
        self.ramp_rate_dmd.caput(self.ramprate)
        
    def setFieldTarget(self, val):
        self.target = val
        self.field_dmd.caput(self.target)
        
magz_c = MagnetFieldControl("magz_c", "BL06J-EA-MAG-01", "Z", "BL06J-EA-SMC-03"); magz_c.configure()
magy_c = MagnetFieldControl("magy_c", "BL06J-EA-MAG-01", "Y", "BL06J-EA-SMC-02"); magy_c.configure()
magx_c = MagnetFieldControl("magx_c", "BL06J-EA-MAG-01", "X", "BL06J-EA-SMC-01"); magx_c.configure()

        