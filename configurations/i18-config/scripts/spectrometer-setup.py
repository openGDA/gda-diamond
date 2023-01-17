# Functions for setting up intial values on XES spectrometer objects

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

    xesEnergyScannable.getXes().getRadiusScannable().moveTo(1000.)
    

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
    if spectrometerScannable.getSpectrometerX() != None : 
        spectrometerScannable.getSpectrometerX().moveTo(radiusValue)
         
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