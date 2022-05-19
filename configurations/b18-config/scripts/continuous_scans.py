from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
from gda.scan import ContinuousScan
from __builtin__ import False
from uk.ac.gda.server.exafs.epics.device.scannable import QexafsTestingScannable
from gda.device import IScannableMotor
from gda.device.scannable import TwoDScanPlotter

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

twoDPlotter = TwoDScanPlotter()
twoDPlotter.setName("twoDPlotter")
# this should be set to one of the output quantities in the scan (e.g. I0, It, Iref if using counterTimer01 etc)
twoDPlotter.setZ_colName("It")
twoDPlotter.setOpenPlotViewAtScanStart(True)
twoDPlotter.setPlotViewname("2d plot view")

def test_2d_scan() :
    cs = createContinuousScan(sam1rot, 10, 20, 0.1, 0.01, [qexafs_counterTimer01])
    twoDPlotter.setZ_colName("I0")
    twoDPlotter.setXArgs(10, 20,  0.1) # 0.1)
    twoDPlotter.setYArgs(10, 20,  1.0) #1.0)

    scan test 10 20 1.0 cs twoDPlotter

def createContinuousScan(scnMotor, start, end, step, time_per_point, dets=[]) :
    """
        Create continuous scan using 'step scan'-like parameter 
        i.e. between start and end positions, with num points and total time computed automatically.
        
            scnMotor - scannable motor object. Position of this motor is also recorded during the scan
            start, end - start and end positions for the scan
            step - distance between start and end of each readout
            time_per_point - duration of each readout
            dets = list of detectors to use for the scan
    """
    num_points=int((end-start)/step)
    total_time=num_points*time_per_point
    
    ## Create continuously scannable object from the scannable motor
    continuous_scannable = createContinuousScannable(scnMotor)
    
    cs=getCscanUnsyncronized(continuous_scannable, start, end, num_points, total_time, dets)
    
    #add non continuous variable to get encoder values for motor position instead of values calculated by GDA according to speed
    cs.getAllScannables().add(scnMotor)

    return cs

def createContinuousScannable(scn, name=None):
    """
        Create a new continuous scannable object (QexafsTestingScannable) for use in ContinuousScans.
        Output format, current speed are taken from the supplied scannable. Speed to use when
        moving to runup position is 0.5*max speed of the motor.
        
        Parameters :
            scn  -  a scannable. This should be a scannable motor - provides the underlying motor object for the new scannable.
            name - name to use for the new scannable (optional). If not set new name is 'qexafs_'.scn.getName()

    """

    if isinstance(scn, IScannableMotor) == False :
        print("Cannot create new 'Continuous scannable' - object is not a scannable motor")
        return
        
    if name == None :
        name = "qexafs_"+scn.getName()
    
    motor = scn.getMotor()
    newScannable = QexafsTestingScannable()
    newScannable.setMotor(motor)
    newScannable.setName(name)
    newScannable.setOutputFormat(scn.getOutputFormat())
    
    maxSpeed = motor.getMaxSpeed()
    newScannable.setSpeed(motor.getSpeed())
    newScannable.setMaxMotorSpeed(maxSpeed*0.5)
    newScannable.configure()
    return newScannable

"""
No zebra used for synchronization. Motor move and tfg start at same time 
"""
def getCscanUnsyncronized(continuous_axis, start, stop, readouts, time, extraDetectors=None ) :
    detectors=[qexafs_counterTimer01]
    if extraDetectors != None :
        detectors.extend(extraDetectors)
    
    cs=ContinuousScan(continuous_axis, start, stop, readouts, time, detectors)
    # cs.getAllScannables().add(axis) # add hoffset scannable to get the real position at each scan data point (from Epics)
    cs.getAllScannables().add(set_tfg_internal_trigger)
    return cs 

def runCscanUnsyncronized(continuous_axis, start, stop, readouts, time, extraDetectors=None ) :
    cs = getCscanUnsyncronized(continuous_axis, start, stop, readouts, time, extraDetectors)
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