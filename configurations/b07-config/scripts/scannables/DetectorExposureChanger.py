'''
Created on 8 Jan 2020

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class DetectorExposureScannable(ScannableMotionBase):
    '''
    a scannable to change exposure time of a given detector PV at each scan data point during scan process
    '''


    def __init__(self, name, pv):
        '''
        create a scannable for specified PV
        '''
        self.setName(name)
        self.setInputNames(['exposure'])
        self.pv = pv
        self.cli=CAClient(pv)
        self._busy=False
        
    def atScanStart(self):
        if not self.cli.isConfigured():
            self.cli.configure()
            
    def atScanEnd(self):
        if self.cli.isConfigured():
            self.cli.clearup()
            
    def asynchronousMoveTo(self, new_pos):
        try:
            if not self.cli.isConfigured():
                self.cli.configure()
            self._busy=True
            self.cli.caput(float(new_pos))
        except:
            raise 
        finally:
            self._busy=False
        
    def getPosition(self):
        return float(self.cli.caget())
    
    def isBusy(self):
        return self._busy;
            