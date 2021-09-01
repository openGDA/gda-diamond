'''
A metadata scannable used to obtain the gap of insertion device used to generate X-ray in beamline I10.

Created on Sep 1, 2021

@author: fy65
'''
from gda.device.scannable import  ScannableMotionUnitsBase
from calibrations.xraysource import X_RAY_SOURCE_MODES

class GapScannable(ScannableMotionUnitsBase):
    '''
    return the ID gap used for generating X-ray
    '''

    def __init__(self, name, smode, iddgap, idugap, unit, formatstring):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setUserUnits(unit)
        self.setOutputFormat([formatstring])
        self.smode = smode
        self.iddgap = iddgap
        self.idugap = idugap
    
    def getPosition(self):
        mode = str(self.smode.getPosition())
        if mode == X_RAY_SOURCE_MODES[0]:
            return float(self.iddgap.getPosition())
        elif mode == X_RAY_SOURCE_MODES[1]:
            return float(self.idugap.getPosition())
        else:
            return "source mode is %s, cannot determine ID gap!" % mode
    
    def asynchronousMoveTo(self):
        print("%s is a Read-Only scannable used for metadata." % self.getName())
    
    def isBusy(self):
        return False
    
    