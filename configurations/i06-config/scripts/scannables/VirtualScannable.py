'''
Created on 7 Sept 2023

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from scannables.m4m5finepitches import m4fpitch, m5fpitch
from gdascripts.utils import caget
from pickle import FALSE

def calculate_x_and_y_from_current_m5_m4_positions_and_leem_rot(v5, v4):
    import math
    from i06shared import installation
    # get LEEM rotation angle from device
    if installation.isDummy():
        leem_rotation_angle = -139.0
    if installation.isLive():
        try:
            leem_rotation_angle = float(caget("BL06I-EA-LEEM-01:IMAGE:ROT:RBV"))
        except:
            print("Failed to get LEEM rotation angle from 'BL06I-EA-LEEM-01:IMAGE:ROT:RBV'")
            raise
        
    beam_rotation = (-leem_rotation_angle + 87)*math.pi/180.0
    s = math.sin(beam_rotation)
    c = math.cos(beam_rotation)
    #calculate the beam position in micron
    x_current = 920.0*c*v5 - 500.0*s*v4
    y_current = -920.0*s*v5 - 500.0*c*v4
    
    return x_current, y_current, s, c

class VirtualScannable(ScannableMotionBase):
    '''
    a virtual scannable that moves 2 other actual scannables for a given value, on completion it returns the demand value.
    '''

    def __init__(self, name, func, scannable1 = m5fpitch, scannable2 = m4fpitch):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.func = func
        self.scannable1 = scannable1
        self.scannable2 = scannable2
        self.demand_position = 0.0
        self._busy = False
        
    def getPosition(self):
        return self.demand_position

    def asynchronousMoveTo(self, new_pos):
        try:
            self._busy = True
            self.demand_position = float(new_pos)
            v5 = float(self.scannable1.getPosition())
            v4 = float(self.scannable2.getPosition())
            
            x_current, y_current, s, c = calculate_x_and_y_from_current_m5_m4_positions_and_leem_rot(v5, v4)
            
            V5, V4 = self.func(float(new_pos), x_current, y_current, s, c)
            
            self.scannable1.asynchronousMoveTo(V5)
            self.scannable2.asynchronousMoveTo(V4)
        except:
            print("'%s' Failed to move to %f" % (self.getName(), self.demand_position))
            raise
        finally:
            self._busy = False
            
    def isBusy(self):
        return self._busy or self.scannable1.isBusy() or self.scannable2.isBusy(

)
        