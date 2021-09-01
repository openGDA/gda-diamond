'''
a metadata svcannable used to obtain the taper of the insertion device used to generate X-ray beam in I10

Created on Sep 1, 2021

@author: fy65
'''
from gda.device.scannable import  ScannableMotionUnitsBase
from calibrations.xraysource import X_RAY_SOURCE_MODES

class TaperScannable(ScannableMotionUnitsBase):
    '''
    a scannable describe the taper property of the insertion device that generate X-ray beam
    '''


    def __init__(self, name, smode, unit, formatstring, iddtaper=None, idutaper=None):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setUserUnits(unit)
        self.setOutputFormat([formatstring])
        self.smode = smode
        self.iddtaper = iddtaper
        self.idutaper = idutaper
    
    def getPosition(self):
        mode = str(self.smode.getPosition())
        if mode == X_RAY_SOURCE_MODES[0]:
            if self.iddtaper:
                return float(self.iddtaper.getPosition())
            return 0.000
        elif mode == X_RAY_SOURCE_MODES[1]:
            if self.idutaper:
                return float(self.idutaper.getPosition())
            return 0.000
        else:
            return "source mode is %s, cannot determine taper!" % mode
    
    def asynchronousMoveTo(self):
        print("%s is a Read-Only scannable used for metadata." % self.getName())
    
    def isBusy(self):
        return False
    
