from uk.ac.gda.exafs.ui.data import TimingGroup, EdeScanParameters


def createEdeScanParams(numSpectra, accumulationTime, numAccumulations):
    """
    Return an EdeScanParameters object used for setting up EdeScans.
    Parameters : 
        numSpectra - total number of spectra to collect
        accumulation time - time per accumulation (sec)
        numAccumulations - accumulations per spectrum
    """
    newGroup = TimingGroup();
    newGroup.setLabel("group1");
    newGroup.setNumberOfFrames(numSpectra);
    newGroup.setTimePerScan(accumulationTime);
    newGroup.setNumberOfScansPerFrame(numAccumulations);
    newGroup.setTimePerFrame(accumulationTime*numAccumulations);
    newGroup.setDelayBetweenFrames(0);
    return EdeScanParameters.createEdeScanParameters([newGroup]);

from gda.scan import EdeScan
from gda.scan.ede.position import EdeScanMotorPositions
from org.dawnsci.ede import EdePositionType, EdeScanType


def createEdeScan(edeParams):
    """
    Return new EdeScan object from EdeScanParameters object.
    The motor positions for the scan are set to be empty, scan type is Light I0
    params - EdeScanParameters object
    """
    motorPositions = EdeScanMotorPositions(EdePositionType.OUTBEAM, None)
    edeScan = EdeScan(edeParams, motorPositions, EdeScanType.LIGHT, xh, 0, dummy_shutter, None)
    return edeScan


def runEdeScanWithMotorMove(edeParams, motor, startPos, endPos, motorSpeed=0, delay=0.0) :
    """
        Run an Ede scan at the same time as moving a motor. The motor is moved asynchronously
        between startPos and endPos using specified motor speed.
        
        edeParams - EdeScanParameters object
        motor - motor to be moved
        startPos, endPos - start and end positions for the motor move
        motorSpeed = speed of the motor (optional, set if > 0)
        delay - how long to wait after starting the motor move to endPos to start the EdeScan (optional, set if > 0)
    """
    print("Creating Ede scan object")
    edeScan = createEdeScan(edeParams)
    edeScan.addScannableToMonitorDuringScan(motor)

    origSpeed = motor.getSpeed()
    print("Moving motor to start position : %f"%(startPos))
    motor.moveTo(startPos)
    print("Setting speed to %f"%(motorSpeed))
    if motorSpeed > 0 :
        motor.setSpeed(motorSpeed)
    print("Starting asynchronous move to : %f "%(endPos))
    motor.asynchronousMoveTo(endPos)
    
    if delay > 0 :
        print("Waiting %f secs to start collection"%(delay))
        sleep(delay)
    
    print("Starting Ede scan")
    edeScan.runScan()

    motor.setSpeed(origSpeed)
    
