print "Adding continuous scan commands for ionchambers and xspress3 "
print "\t run_continuous_scan(totalTime, timePerReadout) \n\t run_continuous_xspress3_scan(totalTime, timePerReadout) "

def run_continuous_scan(totalTime, timePerReadout) :
    numReadouts = int(totalTime/timePerReadout)
    ionchambers.setUseInternalTriggeredFrames(True)
    cvscan qexafs_energy 0 totalTime numReadouts totalTime ionchambers

def run_continuous_xspress3_scan(totalTime, timePerReadout) :
    numReadouts = int(totalTime/timePerReadout)
    ionchambers.setUseInternalTriggeredFrames(True)
    cvscan qexafs_energy 0 totalTime numReadouts totalTime buffered_xspress3 ionchambers
    
    

print "Adding continuous scan commands for Ede detectors "
print "\t runEdeScan(numSpectra, accumulationTime, numAccumulations, detector=xh)"
print "\t createEdeScanParams(numSpectra, accumulationTime, numAccumulations)"
print "\t createEdeScanParamsFrameTime(numSpectra, accumulationTime, timePerSpectrum, detector=xh)"
print "\t runEdeScanWithMotorMove(edeParams, motor, startPos, endPos, motorSpeed=0, delay=0.0, detector=xh)"


from uk.ac.gda.exafs.ui.data import TimingGroup, EdeScanParameters


def createEdeScanParamsFrameTime(numSpectra, accumulationTime, timePerSpectrum, detector=xh):
    """
    Same as createEdeScanParams except number of accumulations is determined automatically
    from the detector, to get the requested time per spectrum.
    Parameters : 
        numSpectra - total number of spectra to collect
        accumulation time - time per accumulation (sec)
        timePerSpectrum - time for each spectrum
        detector - detector to use for determine number of accumulations (xh or frelon, default=xh)
    """
    numAccumulations = detector.getNumberScansInFrame(timePerSpectrum, accumulationTime, numSpectra)
    print("Time per spectrum : %f \nAccumulation time : %f \nNum spectra : %d \n --> num accumulations = %d"%(timePerSpectrum, accumulationTime, numSpectra, numAccumulations))
    return createEdeScanParams(numSpectra, accumulationTime, numAccumulations)


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

def runEdeScan(numSpectra, accumulationTime, numAccumulations, detector=xh):
    """
    Run an Ede scan object used for setting up EdeScans.
    Parameters : 
        numSpectra - total number of spectra to collect
        accumulation time - time per accumulation (sec)
        numAccumulations - accumulations per spectrum
        detector - detector to use (default = xh)
    """
    params = createEdeScanParams(numSpectra, accumulationTime, numAccumulations)
    createEdeScan(params, detector).runScan()

from gda.scan import EdeScan
from gda.scan.ede.position import EdeScanMotorPositions
from org.dawnsci.ede import EdePositionType, EdeScanType


def createEdeScan(edeParams, detector=xh):
    """
    Return new EdeScan object from EdeScanParameters object.
    The motor positions for the scan are set to be empty, scan type is Light I0
    params - EdeScanParameters object
    detector - detector to use (default = xh)
    """
    # Set scan types to 'Light It' so that fast data writing is used for the Nexus file writing
    motorPositions = EdeScanMotorPositions(EdePositionType.INBEAM, None)
    edeScan = EdeScan(edeParams, motorPositions, EdeScanType.LIGHT, detector, 0, dummy_shutter, None)
    return edeScan


def runEdeScanWithMotorMove(edeParams, motorToMove, startPos, endPos, motorSpeed=0, delay=0.0, detector=xh) :
    """
        Run an Ede scan at the same time as moving a motorToMove. The motorToMove is moved asynchronously
        between startPos and endPos using specified motorToMove speed.
        
        edeParams - EdeScanParameters object
        motorToMove - motorToMove to be moved
        startPos, endPos - start and end positions for the motorToMove move
        motorSpeed = speed of the motorToMove (optional, set if > 0)
        delay - how long to wait after starting the motorToMove move to endPos to start the EdeScan (optional, set if > 0)
    """
    print("Creating Ede scan object")
    edeScan = createEdeScan(edeParams)
    edeScan.addScannableToMonitorDuringScan(motorToMove)

    origSpeed = motorToMove.getSpeed()
    
    print("Moving %s to start position : %f"%(motorToMove.getName(), startPos))
    motorToMove.moveTo(startPos)
    
    if motorSpeed > 0 :
        print("Setting motor speed to : %f"%(motorSpeed))
        motorToMove.setSpeed(motorSpeed)
    
    print("Starting asynchronous move to : %f "%(endPos))
    motorToMove.asynchronousMoveTo(endPos)
    
    if delay > 0 :
        print("Waiting %f secs before starting collection"%(delay))
        sleep(delay)
    
    try : 
        print("Starting Ede scan")
        edeScan.runScan()
    finally :  
        print("Stopping motor at end of scan")
        motorToMove.stop()
        sleep(0.5)
        
        print("Restoring original motor speed (%f)"%(origSpeed))
        motorToMove.setSpeed(origSpeed)
