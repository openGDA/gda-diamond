'''
A metadata scannable used to obtain the gap of insertion device used to generate X-ray in beamline I06.

Created on Sep 1, 2021

@author: fy65
'''
from gda.device.scannable import  ScannableMotionUnitsBase
from i06shared.scannables.sourceModes import SourceMode

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
        if mode == SourceMode.SOURCE_MODES[0]:
            return float(self.iddgap.getPosition())
        elif mode == SourceMode.SOURCE_MODES[1]:
            return float(self.idugap.getPosition())
        elif mode == SourceMode.SOURCE_MODES[2]:
            return float(self.iddgap.getPosition())
        elif mode == SourceMode.SOURCE_MODES[3]:
            return float(self.iddgap.getPosition())
        else:
            return "source mode is %s, cannot determine ID gap!" % mode
    
    def asynchronousMoveTo(self):
        print("%s is a Read-Only scannable used for metadata." % self.getName())
    
    def isBusy(self):
        return False
    
    