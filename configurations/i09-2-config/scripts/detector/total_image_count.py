'''
Created on Jan 18, 2023

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
import time

PV_ROOT = "BL09K-EA-D-01:"
ENABLE_CALLBACK = "Stats5:EnableCallbacks"
COMPUTE_STATISTICS = "Stats5:ComputeStatistics"
TOTAL_RBV = "Stats5:Total_RBV"
CAM_ACQUIRE = "cam1:Acquire"
CAM_ACQUIRE_TIME = "cam1:AcquireTime_RBV"
FIRST_BUSY_CHECKING_DELAY = 0.5

class IntegratedSpectrum(ScannableMotionBase):
    '''
    classdocs
    '''


    def __init__(self, name, pv_root):
        '''
        Constructor  
        '''
        self.setName(name)
        self.setInputNames([name])
        self.pv_root = pv_root
        self.totalCli = CAClient(pv_root + TOTAL_RBV)
        self.enableCli = CAClient(pv_root + ENABLE_CALLBACK)
        self.statCli = CAClient(pv_root + COMPUTE_STATISTICS)
        self.acquireCli = CAClient(pv_root + CAM_ACQUIRE)
        self.acquireTimeCli = CAClient(pv_root + CAM_ACQUIRE_TIME)
        self.totalCli.configure()
        self.enableCli.configure()
        self.statCli.configure()
        self.acquireCli.configure()
        self.acquireTimeCli.configure()
        self.enable = None
        self.statistics = None
        
    def atScanStart(self):
        self.enable = self.enableCli.caget()
        self.statistics = self.statCli.caget()
        self.enableCli.caput(1)
        self.statCli.caput(1)
        self.firstTime = True
        self.startTime = time.time()
        
    def atScanEnd(self):
        if self.enable:
            self.enableCli.caput(0)
        if self.statistics:
            self.statCli.caput(0)
        self.firstTime = False
        
    def rawGetPosition(self):
        return float(self.totalCli.caget())
    
    def rawAsynchronousMoveTo(self, new_pos):
        raise Exception("%s: is Read-Only scannable" % self.getName())
    
    def isBusy(self):
        if (time.time() - self.startTime) < float(self.acquireTimeCli.caget()):
            return True
        if int(self.acquireCli.caget()) == 1:
            return True
        return False
    
    def stop(self):
        self.atScanEnd()
    
    def atCommandFailure(self):
        self.stop()
        