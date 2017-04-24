'''
Scannable to offset ID harmonic at current energy of the X-ray beam.

Created on 21 Apr 2017

@author: fy65
'''
from gda.device.scannable import ScannableBase

class HarmonicOffset(ScannableBase):
    '''
    offset current energy harmonic.
    '''


    def __init__(self, name, energy):
        '''
        Constructor - delegate to energy to handle harmonic offset.
        '''
        self.setName(name)
        self.energy=energy
        
    def getPosition(self):
        return self.energy.getOffhar()
    
    def asynchronousMoveTo(self, value):
        self.energy.setOffhar(value)
                
    def isBusy(self):
        return self.energy.isHaroffBusy()      
                
           
        