'''
define energy offset to be applied to detune ID energy

Created on 9 Dec 2019

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase

class EnergyOffset(ScannableMotionBase):
    '''
    A virtual scannable to hold energy offset to be applied to detune ID energy.
    '''

    def __init__(self, name, energy_offset=0.0):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.energy_offset = energy_offset
        
    def getPosition(self):
        return self.energy_offset
    
    def asynchronousMoveTo(self, newpos):
        self.energy_offset=float(newpos)
        
    def isBusy(self):
        return False
    
energy_offset = EnergyOffset("energy_offset")
