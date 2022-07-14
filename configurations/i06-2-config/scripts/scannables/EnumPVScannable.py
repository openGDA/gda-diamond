'''
Created on 23 Jul 2019

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep

class EnumPVScannable(ScannableMotionBase):
    '''
    support get and set a multiple values Enum PV. There is no wait or check on set a value to the PV.
    Once instantiated the object must be configured first before use
    '''


    def __init__(self, name, pv):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.pvcli=CAClient(pv)
        self.availablePositions=[]
        self.pvcli.configure()
        sleep(1)
        self.availablePositions=self.pvcli.cagetLabels()

    
    def getPosition(self):
        return self.pvcli.caget()
    
    def asynchronousMoveTo(self, newpos):
        if newpos in self.availablePositions:
            self.pvcli.caput(self.availablePositions.index(newpos))
        else:
            raise Exception("Requested mode %s is not available in list %s" %(newpos, self.availablePositions))
        
    def isBusy(self):
        return False
    
    def toFormattedString(self):
        return "%s: %s" % (self.getName(), self.getPosition())
    
    def __del__(self):
        self.pvcli.clearup()