from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
from gda.scan import ContinuousScanWithSleep
from __builtin__ import False, True
from uk.ac.gda.server.exafs.epics.device.scannable import QexafsTestingScannable
from gda.device import IScannableMotor
from gda.device.scannable import TwoDScanPlotter
import math
from gda.device.detector import BufferedScannablePositions 
import time

print "Running 'continuous_scans.py"


class ContinuousMotorScannable(QexafsTestingScannable) :
    
    def __init__(self, bufferedScaler):
        self.bufferedScaler = bufferedScaler
        self.pulseDelayMs = 0.0
        self.scannable_positions_detector=None
        
    def atScanLineStart(self):
        # set the tfg to use internal triggered frames (each inner loop of the scan)
        self.bufferedScaler.setUseExternalTriggers(False)
        
    def atScanStart(self):
        # this ensures that tfg is only configured during call to setContinuousMode(True).
        # Need to call startTfg method to actually start it.
        self.bufferedScaler.setManualStart(True)
    
    def performContinuousMove(self):
        # Positions detector will already have been started by call to setContinuousMode(True), so need to stop it here
        if self.scannable_positions_detector is not None :
            print("Making sure positions detector has been stopped")
            self.scannable_positions_detector.atScanEnd()
            
        # start the motor move
        print("Moving %s"%(self.getName()))
        super(ContinuousMotorScannable,self).performContinuousMove()
        
        # sleep for the delay time
        if self.pulseDelayMs> 0 :
            print("Waiting for %f ms before starting tfg"%(self.pulseDelayMs))
            time.sleep(self.pulseDelayMs)
        
        #start the tfg
        print("Starting Tfg")
        self.bufferedScaler.startTfg(False)
        
        # Start the positions detector
        if self.scannable_positions_detector is not None :
            print("Starting the positions detector")
            self.scannable_positions_detector.atScanStart()
        
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

def createContinuousScan(scnMotor, start, end, step, time_per_point, dets=None, bidirectional=False, rampDistance=0, pulseDelayMs=0, **kwargs) :
    """
        Create continuous scan using 'step scan'-like parameter 
        i.e. between start and end positions, with num points and total time computed automatically.
        
            scnMotor - scannable motor object. Position of this motor is also recorded during the scan
            start, end - start and end positions for the scan
            step - distance between start and end of each readout
            time_per_point - duration of each readout
            dets = list of detectors to use for the scan
    """
    num_points=abs( int((end-start)/step) )
    total_time=num_points*time_per_point
    
    continuous_scannable = scnMotor
    ## Create continuously scannable object from the scannable motor
    if not isinstance(scnMotor, ContinuouslyScannable) :
        continuous_scannable = createContinuousScannable(scnMotor, pulseDelayMs=pulseDelayMs, rampDistance=rampDistance)
    
    cs=getCscanUnsyncronized(continuous_scannable, start, end, num_points, total_time, dets, bidirectional=bidirectional, **kwargs)
    cs.setBiDirectional(bidirectional)

    #add non continuous variable to get encoder values for motor position instead of values calculated by GDA according to speed
    #cs.getAllScannables().add(scnMotor)

    return cs

def createContinuousScannable(scn, name=None, pulseDelayMs=0, rampDistance=0):
    """
        Create a new continuous scannable object (QexafsTestingScannable) for use in ContinuousScans.
        Output format, current speed are taken from the supplied scannable. Speed to use when
        moving to runup position is 0.5*max speed of the motor.
        
        Parameters :
            scn  -  a scannable. This should be a scannable motor - provides the underlying motor object for the new scannable.
            name - name to use for the new scannable (optional). If not set new name is 'qexafs_'.scn.getName()

            pulseDelay = delay between motor move and Tfg start (milli-seconds)
            rampDistance = distance beyond start, end scan positions to move for initial and final positions.
    """

    if isinstance(scn, IScannableMotor) == False :
        print("Cannot create new 'Continuous scannable' - object is not a scannable motor")
        return
        
    if name == None :
        name = "qexafs_"+scn.getName()
    
    newScannable = ContinuousMotorScannable(qexafs_counterTimer01)
    newScannable.setDelegateScannable(scn)
    newScannable.setName(name)
    newScannable.setOutputFormat(scn.getOutputFormat())
    
    motor = scn.getMotor()
    maxSpeed = motor.getMaxSpeed()
    # newScannable.setSpeed(motor.getSpeed())
    newScannable.setMaxMotorSpeed(maxSpeed*0.5)
    
    newScannable.pulseDelayMs = pulseDelayMs
    newScannable.setRampDistance(rampDistance)
    
    newScannable.configure()
    
    scannable_positions_detector = createScannableDetector(newScannable)
    
    newScannable.scannable_positions_detector = scannable_positions_detector
    
    return newScannable

def createScannableDetector(scn) :
    scn_det = BufferedScannablePositions()
    scn_det.setScannable(scn)
    scn_det.setName(scn.getName()+"_det")
    return scn_det

"""
No zebra used for synchronization. Motor move and tfg start at same time 
"""
def getCscanUnsyncronized(continuous_axis, start, stop, readouts, time, extraDetectors=None, extraScannables=None, bidirectional=False, timeBetweenStarts=0.0) :
    detectors=[]

    if extraDetectors != None :
        detectors.extend(extraDetectors)
    
    # Get the detector to be used for recording the scannable position during scan
    scn_detector = None
    if isinstance(continuous_axis, BufferedScannablePositions) :
        scn_detector = continuous_axis.scannable_positions_detector
    # Create default detector to record positions
    if scn_detector is None : 
        scn_detector = createScannableDetector(continuous_axis)
        
    detectors.append(scn_detector)
    
    # add counterTimer01
    detectors.append(qexafs_counterTimer01)
    
    cs=ContinuousScanWithSleep(continuous_axis, start, stop, readouts, time, detectors)
    
    # set the bidirectional flag
    cs.setBiDirectional(bidirectional)
    
    # set the time between starts
    cs.setTimeBetweenStarts(timeBetweenStarts)
    
    # Add any extra scannables (to record the position for each point in the scan)
    if extraScannables != None :
        for scn in extraScannables : 
            cs.getAllScannables().add(scn)
    return cs 

def runCscanUnsyncronized(continuous_axis, start, stop, readouts, time, extraDetectors=None ) :
    cs = getCscanUnsyncronized(continuous_axis, start, stop, readouts, time, extraDetectors)
    cs.runScan()


print "Run continuous scan : runCscanUnsyncronized(axis, start, stop, num_readouts, total_time )"
print "Create continuous scan object : getCscanUnsyncronized(axis, start, stop, num_readouts, total_time )"
print "Run a 2d scan using continuous scan over sam2x for inner axis : "
print "   cs = getCscanUnsyncronized(qexafs_sam2x, 100, 150, 100, 10)"
print "   scan sam2y 50 100 1.0 cs"
