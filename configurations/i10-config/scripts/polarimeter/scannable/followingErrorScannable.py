"""
Scannable Motor with Following Error scannable for use with GDA at Diamond
Light Source
"""

from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class FollowingErrorScannable(ScannableMotionBase):
    
    def __init__(self, name, scannable, base_pv):
        self.name = name
        self.scannable = scannable
        self.base_pv = base_pv
        
        self.inputNames = [name]
        self.extraNames = ['max']
        self.outputFormat = ['%f', '%f']
        
    def __repr__(self):
        return "FollowingErrorScannable(%r, %r, %r)" % (self.name,
            self.scannable.name, self.base_pv)
    
    def __str__(self):
        return "followingError=%s, maxFollowingError=%s" % self.getPosition()

    def configure(self):
        self.feError = CAClient(self.base_pv + ":FERROR")
        self.feErrorMax = CAClient(self.base_pv + ":FERRORMAX")
        self.feMaxReset = CAClient(self.base_pv + ":FEMAXRESET.PROC")
        self.reconfigure()

    def reconfigure(self):        
        if not self.feError.isConfigured():
            self.feError.configure()
        if not self.feErrorMax.isConfigured():
            self.feErrorMax.configure()
        if not self.feMaxReset.isConfigured():
            self.feMaxReset.configure()

    def asynchronousMoveTo(self, position):
        return
    
    def atLevelMoveStart(self):
        self.feMaxReset.caput(1)
        return

    def atScanStart(self):
        self.setLevel(self.scannable.getLevel())
        self.feMaxReset.caput(1)
        self.reconfigure()

    def getPosition(self):
        return (float(self.feError.caget()), float(self.feErrorMax.caget()))

    def isBusy(self):
        return self.scannable.isBusy()