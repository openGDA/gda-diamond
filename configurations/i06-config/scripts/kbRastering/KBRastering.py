'''
Created on 25 Jan 2019

@author: fy65
'''
#Keysight
from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caput

KEYSIGHT_AMPLITUDE_VFM_PV="BL06I-EA-SGEN-01:CH2:AMP"
KEYSIGHT_AMPLITUDE_HFM_PV="BL06I-EA-SGEN-01:CH1:AMP"
#Kentec
HYTEC_AMPLITUDE_VFM_PV="BL06I-OP-KBM-01:VFM:FPITCH:AMPL"
HYTEC_AMPLITUDE_HFM_PV="BL06I-OP-KBM-01:HFM:FPITCH:AMPL"

ON=0.5
OFF=0

class KBRasteringControl(ScannableMotionBase):
    def __init__(self, name, pvname_vfm, pvname_hkm):
        self.setName(name)
        self.pv_vfm=pvname_vfm
        self.pv_hfm=pvname_hkm
        
    def hron(self):
        '''sets horizontal rastering on
        '''
        caput(self.pv_hfm, ON)
        
    def vron(self):
        '''sets vertical rastering on
        '''
        caput(self.pv_vfm, ON)  
        
    def hroff(self):
        '''sets horizontal rastering off
        '''
        caput(self.pv_hfm, OFF)
        
    def vroff(self):
        '''set vertical rastering off
        '''
        caput(self.pv_vfm, OFF)
        
    def horizontal(self):
        '''set horizontal rastering
        '''
        caput(self.pv_hfm, ON)
        caput(self.pv_vfm, OFF)
    
    def vertical(self):
        '''set vertical rastering
        '''
        caput(self.pv_hfm, OFF)
        caput(self.pv_vfm, ON)
        
    def rawGetPosition(self):
        pass
    
    def rawAsynchronousMoveTo(self, newpos):
        pass
    
    def isBusy(self):
        return False
    
raster_with_keysight=KBRasteringControl("raster_with_keysight", KEYSIGHT_AMPLITUDE_VFM_PV, KEYSIGHT_AMPLITUDE_HFM_PV)
raster_with_kentec=KBRasteringControl("raster_with_kentec", HYTEC_AMPLITUDE_VFM_PV, HYTEC_AMPLITUDE_HFM_PV)


