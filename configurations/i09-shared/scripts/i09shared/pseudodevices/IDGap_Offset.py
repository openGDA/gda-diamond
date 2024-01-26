'''
Created on 9 Dec 2019

@author: fy65
'''
from time import sleep
from gda.device.scannable import ScannableMotionBase
from gda.device import MotorStatus

class IDGapOffset(ScannableMotionBase):
    '''
    A virtual scannable to hold ID gap offset to be applied to detune energy.
    '''
    
    def __init__(self, name, gap_offset=0.0):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.id_offset=gap_offset
        self._is_busy = False;
        
    def getPosition(self):
        return self.id_offset
    
    def asynchronousMoveTo(self, newpos):
        self.notifyIObservers(self, MotorStatus.BUSY);
        self._is_busy = True
        self.id_offset=float(newpos)
        self._is_busy = False
        self.notifyIObservers(self, MotorStatus.READY);
        
    def isBusy(self):
        return self._is_busy
    
    def waitWhileBusy(self):
        while self.isBusy():
            sleep(0.1)