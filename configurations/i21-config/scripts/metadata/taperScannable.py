'''
a metadata scannable used to obtain the taper of the insertion device used to generate X-ray beam in I21

Created on Sep 2, 2021

@author: fy65
'''
from gda.device.scannable import  ScannableMotionUnitsBase

class TaperScannable(ScannableMotionUnitsBase):
    '''
    a scannable describes the taper property of the insertion device that generate X-ray beam
    '''


    def __init__(self, name, unit, formatstring, idtaper=None):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setUserUnits(unit)
        self.setOutputFormat([formatstring])
        self.idtaper = idtaper
    
    def getPosition(self):
        if self.idtaper:
            return float(self.idtaper.getPosition())
        return 0.000
    
    def asynchronousMoveTo(self):
        print("%s is a Read-Only scannable used for metadata." % self.getName())
    
    def isBusy(self):
        return False
    
