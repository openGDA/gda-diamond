print("\nRunning 'spectrometer-setup.py")

# Functions for setting up intial values on XES spectrometer objects
from gda.device.scannable import ScannableUtils
def set_initial_crystal_values(xesEnergyScannable):
    """ 
        Set initial values of allowedToMove scannables for XES spectrometer crystals
    """
    for scn in xesEnergyScannable.getXes().getCrystalsAllowedToMove().getGroupMembers() :
        if scn.getPosition() == None :
            print "Setting initial value of {0} to true".format(scn.getName())
            scn.moveTo("true")
    crystalCuts = [xesEnergyScannable.getCut1(), xesEnergyScannable.getCut2(), xesEnergyScannable.getCut3()]
    for scn in crystalCuts :
        if scn.getPosition() == None :
            print "Setting initial value of {0} to 1".format(scn.getName())
            scn.moveTo(1)

    
    # Check the radius is set to something sensible (but don't wipe out any previously restored value!)
    radiusTooSmall = 500.0
    defaultRadius = 1000.0;
    radiusScannable = xesEnergyScannable.getXes().getRadiusScannable()
    currentValue = ScannableUtils.objectToArray(lower_radius.getPosition())[0]
    if currentValue < radiusTooSmall :
        radiusScannable.moveTo(defaultRadius)
    
def setAnalyserMoveTolerances(xesEnergyScannable, tolerances, numRetries = 1):
    print("Setting up motors for %s : tolerances = %s, retries = %d"%(xesEnergyScannable.getName(), str(tolerances), numRetries))
    for analyser in xesEnergyScannable.getXes().getCrystalsList() :
            motors = analyser.getGroupMembers()
            for count in range(len(motors)) :
                if len(tolerances)>count :
                    mot = motors.get(count)
                    # print("  %s \t: %.4f, %d"%(mot.getName(), tolerances[count], numRetries))
                    mot.setTolerance(tolerances[count])
                    mot.setNumberTries(numRetries)
    
from gda.device.motor import EpicsMotor
from gda.device.motor.EpicsMotor import MissedTargetLevel

def setMotorMoveMissedTargetAction(xesEnergyScannable, missedTargetLevel):
    print("Setting up motors for %s : missed target = %s"%(xesEnergyScannable.getName(), str(missedTargetLevel)))
    allScannables = xesEnergyScannable.getXes().getScannables()
    for scn in allScannables :
        if isinstance(scn, gda.device.IScannableMotor) and isinstance(scn.getMotor(), EpicsMotor) :
            #print("%s"%(scn.getName()))
            mot = scn.getMotor()
            mot.setMissedTargetLevel(missedTargetLevel)
        
def setup_dummy_spectrometer(xesEnergyScannable) :
    """
        Setup initial values for dummy XES spectrometer :
        - Crystal type = Si (if not set),
        - Radius = 1000, 
        - Crystal cuts to 1, all crystals allowed to move
        - Fast motor speeds
        - Initial energy = 2000eV
        
    """
    print("Setting up XESEnergyScannable %s ..."%(xesEnergyScannable.getName()))
    if xesEnergyScannable.getMaterial().getPosition() == None :
        xesEnergyScannable.getMaterial().moveTo("Si")

    defSpeed = 10000.0
    radiusValue = 1000.0
    spectrometerScannable = xesEnergyScannable.getXes()
    
    # Set the trajector size so a large detector move doesn't take too long
    spectrometerScannable.setTrajectoryStepSize(2.0)
    
    # Set the speed of all the scannables
    for scn in spectrometerScannable.getScannables() :
        if isinstance(scn, gda.device.IScannableMotor) :
            scn.setSpeed(defSpeed)

    # Set some positions so Bragg calculation can work correctly
    spectrometerScannable.getRadiusScannable().moveTo(radiusValue)
    spectrometerScannable.getDetYScannable().moveTo(475.0)

    # Set the crystal cuts
    print("Setting crystal cut values to 1")
    xesEnergyScannable.getCut1().moveTo(1)
    xesEnergyScannable.getCut2().moveTo(1)
    xesEnergyScannable.getCut3().moveTo(1)
    
    # Set crystals allowed to move to True (if the scannables are present)
    allowedToMoveGrp = spectrometerScannable.getCrystalsAllowedToMove()
    if allowedToMoveGrp != None :
        print("Setting 'allowed to move' flag to 'true'")
        for allowedToMove in allowedToMoveGrp.getGroupMembers() :
            allowedToMove.moveTo("true")
        
    print "Moving to 2000 eV"
    xesEnergyScannable.moveTo(2000)
    
    print("Finished")
    
    
# Set the demand value precisions in XES bragg objects
XESBraggUpper.setAnalyserDemandPrecision([0.0, 0.0, 0.0035, 0.0])
XESBraggLower.setAnalyserDemandPrecision([0.0, 0.0, 0.0035, 0.0])

# Set the GDA tolerance and number of retries on each ScannableMotor
setAnalyserMoveTolerances(XESEnergyLower, [0.005, 0.005, 0.005, 0.005], 3)
setAnalyserMoveTolerances(XESEnergyUpper, [0.005, 0.005, 0.005, 0.005], 3)

setMotorMoveMissedTargetAction(XESEnergyLower, MissedTargetLevel.IGNORE)
setMotorMoveMissedTargetAction(XESEnergyUpper, MissedTargetLevel.IGNORE)

if LocalProperties.isDummyModeEnabled() :
    setup_dummy_spectrometer(XESEnergyUpper)
    setup_dummy_spectrometer(XESEnergyLower)