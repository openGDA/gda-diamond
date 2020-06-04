from gda.device.scannable import ScannableMotionBase
import subprocess
from gdascripts.utils import *

class ScriptRunner(ScannableMotionBase):
    # constructor
    def __init__(self, name, script_location):
        self.setName(name) 
        self.scriptlocation = script_location
        self.setInputNames([])
        self.setExtraNames([])
        self.setOutputFormat([])

    # returns the value this scannable represents
    def rawGetPosition(self):
        return

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        return

    # Returns the status of this Scannable
    def rawIsBusy(self):
         return
        
    def atScanEnd(self):
        print "Running the Script %s at the end of the scan" % self.scriptlocation
        listprint(subprocess.Popen([self.scriptlocation], stdout=subprocess.PIPE).communicate())
        
    def stop(self):
        print "Running the Script %s at an aborted scan" % self.scriptlocation
        listprint(subprocess.Popen([self.scriptlocation], stdout=subprocess.PIPE).communicate())
        
    