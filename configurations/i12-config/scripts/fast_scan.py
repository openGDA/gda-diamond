from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caput, caget

VELOCITY=20.0
ACCELERATION=0.1

class FastScan(ScannableMotionBase):
    # constructor
    def __init__(self, name):
        self.setName(name) 
        self.setInputNames([])
        self.setExtraNames([])
        self.setOutputFormat([])
        self.numberOfPointsCalled = 0
        self.cachedAcc= caget("BL12I-MO-TAB-02:ST1:THETA.ACCL")
        self.cachedVel= caget("BL12I-MO-TAB-02:ST1:THETA.VELO")
        self.cachedAccAtPointStart=None
        self.cachedVelATPointStart=None

    # returns the value this scannable represents
    def rawGetPosition(self):
        return

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        return

    # Returns the status of this Scannable
    def rawIsBusy(self):
        return
        
        
    def atPointStart(self):
        self.numberOfPointsCalled += 1
        
        if self.numberOfPointsCalled == 2 :           
            print("** Enabling Fast Scanning mode for the theta stage")
            self.cachedAccAtPointStart= caget("BL12I-MO-TAB-02:ST1:THETA.ACCL")
            self.cachedVelATPointStart= caget("BL12I-MO-TAB-02:ST1:THETA.VELO")
            caput("BL12I-MO-TAB-02:ST1:THETA.ACCL", ACCELERATION)
            caput("BL12I-MO-TAB-02:ST1:THETA.VELO", VELOCITY)
            
    def atScanEnd(self):
        print("** Disabling Fast Scanning mode for the theta stage")
        caput("BL12I-MO-TAB-02:ST1:THETA.ACCL", self.cachedAccAtPointStart)
        caput("BL12I-MO-TAB-02:ST1:THETA.VELO", self.cachedVelATPointStart)
        self.cachedAccAtPointStart=None
        self.cachedVelATPointStart=None
        self.numberOfPointsCalled = 0
        
    def stop(self):
        print("** Dissabling Fast Scanning mode for the theta stage due to scan abort")
        if not (self.cachedAccAtPointStart==None or self.cachedVelATPointStart==None):
            caput("BL12I-MO-TAB-02:ST1:THETA.ACCL", self.cachedAccAtPointStart)
            caput("BL12I-MO-TAB-02:ST1:THETA.VELO", self.cachedVelATPointStart)
            self.cachedAccAtPointStart=None
            self.cachedVelATPointStart=None

        self.numberOfPointsCalled = 0
