from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caput, caget
from time import sleep

TIMETOSLEEP=2

class SleeperWhileScan(ScannableMotionBase):
    # constructor
    def __init__(self, name, timeToSleep=TIMETOSLEEP,verbose=False):
        self.setName(name) 
        self.timeToSleep = timeToSleep
        self.verbose = verbose

    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.timeToSleep

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        return

    # Returns the status of this Scannable
    def rawIsBusy(self):
        return
        
    def atPointStart(self):
        if self.verbose:
            print "Sleeper beginning to sleep for %s sec(s)" %(self.timeToSleep)
        sleep(self.timeToSleep)
        
    def atPointEnd(self):
        if self.verbose:
            print "Sleeper finished sleeping for %s sec(s)" %(self.timeToSleep)
        pass
    
    def stop(self):
        pass