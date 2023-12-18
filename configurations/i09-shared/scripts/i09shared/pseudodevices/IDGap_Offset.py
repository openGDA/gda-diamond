'''
Created on 9 Dec 2019

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase

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
        
    def getPosition(self):
        return self.id_offset
    
    def asynchronousMoveTo(self, newpos):
        self.id_offset=float(newpos)
        
    def isBusy(self):
        return False
    
igap_offset=IDGapOffset("igap_offset")
jgap_offset=IDGapOffset("jgap_offset")