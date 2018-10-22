'''
Created on 20 Oct 2017

@author: fy65
'''
from gda.device.scannable import ScannableMotor
import time
from gdascripts.utils import caput

class FollowingErrorHandlerScannable(ScannableMotor):
    '''
    A wrapper Scannable Motor that handles motor's following error by EPICS kill action 
    when following error occurs and the point time over the set time to wait value 
    (must be exceed exposure time of the detector).
    '''


    def __init__(self, name, pv,timetowiat):
        '''
        Constructor
        @param name: name of this object
        @param pv: the motor KILL.PROC PV
        @param timetowait: Time to wait before poke the KILL action.   
        '''
        self.setName(name)
        self.setInputNames([name])
        self.pv=pv
        self.timeelapsed=0.0
        self.timeToWait=timetowiat
        self.start=0.0
        
    def rawAsynchronousMoveTo(self, newpos):
        '''record the start time of the move before calling to move.
        '''
        self.start=time.time()
        super(FollowingErrorHandlerScannable, self).rawAsynchronousMoveTo(newpos)
        
    def isBusy(self):
        '''check timing if exceeded the set time to wait, issue kill call to EPICS record before return False,
        otherwise call the actual scannale motor's isBusy()
        '''
        self.timeelapsed=time.time()-self.start
        if self.timeelapsed > self.timeToWait:
            caput(self.pv, 1)
            return False
        else:
            super(FollowingErrorHandlerScannable, self).isBusy()
            
    def setTimeToWait(self, t):
        self.timeToWait=t
    
    def getTimeToWait(self):
        return self.timeToWait
    
anaRotation=FollowingErrorHandlerScannable("anaRotation", "ME02P-MO-ANA-01:ROT:KILL.PROC", 10.0)
anaRotation.setMotor(AnaRotation.getMotor())  # @UndefinedVariable
anaRotation.setProtectionLevel(0)
anaRotation.setInitialUserUnits("Deg")
anaRotation.setHardwareUnitString("Deg")
