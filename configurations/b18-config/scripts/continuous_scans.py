from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
from uk.ac.gda.server.exafs.epics.device.scannable import QexafsTestingScannable

print "Running 'continuous_scans.py"

"""
  Scannable that runs a jython command in atScanStart and atScanEnd command.
  Similar to gda.device.scannable.ScriptAdapter, except works with Jython commands.
  Set command to be run in atScanStart, atScanEnd by using setScanStartCommand, setScanEndCommand.
"""
class CommandStringAdapter(ScannableBase):

    def __init__(self, name):
        self.name = name
        self.inputNames = [name]
        self.setOutputFormat({});
        self.setInputNames({});
        self.scanStartCommand = ""
        self.scanEndCommand = ""
        self.scanLineStartCommand = ""

    def runCommand(self, when, commandString) :
        if len(commandString) > 0 :
            InterfaceProvider.getTerminalPrinter().print("Running command for "+when+" : "+commandString)
            InterfaceProvider.getCommandRunner().runsource(commandString)
        
    def atScanStart(self) :
        self.runCommand("atScanStart", self.scanStartCommand)
        
    def atScanLineStart(self) :
        self.runCommand("atScanLineStart", self.scanLineStartCommand)

    def atScanEnd(self) :
        self.runCommand("atScanEnd", self.scanEndCommand)    
        
    def setScanStartCommand(self, command) :
        self.scanStartCommand = command
      
    def setScanLineStartCommand(self, command) :
        self.scanLineStartCommand = command
  
    def getScanStartCommand(self) :
        return self.scanStartCommand
        
    def setScanEndCommand(self, command) :
        self.scanEndCommand = command
  
    def getScanEndCommand(self) :
        return self.scanEndCommand
    
    def isBusy(self):
        return False

    def rawAsynchronousMoveTo(self,new_position):
        pass

    def rawGetPosition(self):
        return None
    

set_tfg_internal_trigger = CommandStringAdapter("set_tfg_internal_trigger")
set_tfg_internal_trigger.configure()
set_tfg_internal_trigger.setScanLineStartCommand("qexafs_counterTimer01.setUseInternalTriggeredFrames(True)") # use software start for Tfg triggers

"""
No zebra used for synchronization. Motor move and tfg start at same time 
"""
def getCscanUnsyncronized(continuous_axis, start, stop, readouts, time ) :
    qexafs_counterTimer01.setUseInternalTriggeredFrames(True) # use software start for Tfg triggers
    cs=ContinuousScan(continuous_axis, start, stop, readouts, time, [qexafs_counterTimer01])
    # cs.getAllScannables().add(axis) # add hoffset scannable to get the real position at each scan data point (from Epics)
    cs.getAllScannables().add(set_tfg_internal_trigger)
    return cs 

def runCscanUnsyncronized(continuous_axis, start, stop, readouts, time ) :
    cs = getCscanUnsyncronized(continuous_axis, start, stop, readouts, time)
    cs.runScan()


print "Run continuous scan : runCscanUnsyncronized(axis, start, stop, num_readouts, total_time )"
print "Create continuous scan object : getCscanUnsyncronized(axis, start, stop, num_readouts, total_time )"
print "Run a 2d scan using continuous scan over sam2x for inner axis : "
print "   cs = getCscanUnsyncronized(qexafs_sam2x, 100, 150, 100, 10)"
print "   scan sam2y 50 100 1.0 cs"

"""
Delete the scannables - do this if you want to run the script again without doing a reset_namespace
"""
def delete_scannables() :
    del set_tfg_internal_trigger