# Functions for setting up intial values on XES spectrometer objects
from gda.jython import InterfaceProvider

def set_initial_crystal_values(xesEnergyScannable, initialRadius=500.0):
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

    radius_scannable = xesEnergyScannable.getXes().getRadiusScannable()
    if radius_scannable.getPosition() == None :
        radius_scannable.moveTo(initialRadius)
    

def setup_dummy_spectrometer(xesEnergyScannable, radiusValue=500.0) :
    """
        Setup initial values for dummy XES spectrometer :
        - Crystal type = Si (if not set),
        - Radius = radiusValue (default = 500), 
        - Crystal cuts to 1, all crystals allowed to move
        - Fast motor speeds
        - Initial Bragg angle = 0.5*(mintheta + maxTheta)
        
    """
    print("Setting up XESEnergyScannable %s ..."%(xesEnergyScannable.getName()))
    if xesEnergyScannable.getMaterial().getPosition() == None :
        xesEnergyScannable.getMaterial().moveTo("Si")

    defSpeed = 10000.0
    spectrometerScannable = xesEnergyScannable.getXes()
    
    # Set the speed of all the scannables
    for scn in spectrometerScannable.getScannables() :
        if isinstance(scn, gda.device.IScannableMotor) :
            scn.setSpeed(defSpeed)
            scn.setPosition(0.0)
    
    # Set some positions so Bragg calculation can work correctly
    spectrometerScannable.getRadiusScannable().moveTo(radiusValue)
    
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
        
    mid_theta = (spectrometerScannable.getMinTheta() + spectrometerScannable.getMaxTheta() ) *0.5
    print "Moving mid Beagg angle ("+str(mid_theta)+" degrees)"
    spectrometerScannable.moveTo(mid_theta)
    
    print("Finished")
    
def move_to_lower_limit(scn_motor, diff=1.0) :
    lower_limit = scn_motor.getLowerMotorLimit()+diff
    print("Moving {} to lower limit ({})".format(scn_motor.getName(), lower_limit))
    scn_motor.moveTo(lower_limit)
    print("Finished moving")

def move_to_upper_limit(scn_motor, diff=1.0) :
    upper_limit = scn_motor.getUpperMotorLimit()-diff
    print("Moving {} to lower limit ({})".format(scn_motor.getName(), upper_limit))
    scn_motor.moveTo(upper_limit)
    print("Finished moving")

def set_current_position(scn_motor, position) :
    print("Setting position of {} to {}".format(scn_motor.getName(), position))
    scn_motor.setPosition(float(position))
    print("Current value of Epics user offset = {}".format(scn_motor.getUserOffset()))


def setup_for_testing() :
    
    # Move x to upper limit (Rowland circle radius, 50cm)
    for scn in [minus1_x, centre_x, plus1_x ] :
        move_to_upper_limit(scn)
        set_current_position(scn, 500.0)
        print("")  
    
    # Set lower limit of y to 40mm (to allow moves for 75 < Bragg < 82 degrees)
    for scn in [minus1_y, centre_y, plus1_y ] :
        move_to_lower_limit(scn)
        set_current_position(scn, 65)
        print("")
    
    # Assume det y is already at a good position,
    set_current_position(xes_det_y, 130)
    print("")
    
    for scn in spectrometer_all_scannables.getGroupMembers() :
        if isinstance(scn, gda.device.IScannableMotor) :
            scn.setDemandPositionTolerance(0.001)
            

def show_spectrometer_positions(bragg_angle) :
    map_values = XESBraggJohann.getSpectrometerPositions(bragg_angle)
    print("Calculated spectrometer positions for {} = {} degrees : ".format(XESBraggJohann.getName(), bragg_angle))
    for scn in map_values.keys() :
        print("\t{} : {}".format(scn.getName(), map_values[scn]))
    
def show_spectrometer_offsets() :
    map_values = xes_motor_offset_store.getEpicsOffsets()
    print("Spectrometer motor Epics offset values :")
    for scn in map_values.keys() :
        print("\t{} : {}".format(scn.getName(), map_values[scn]))
        
def set_tolerances(tol = 0.001) :
    print("Setting demand move tolerance to {}".format(tol))
    for scn in spectrometer_all_scannables.getGroupMembers() :
        if isinstance(scn, gda.device.IScannableMotor) :
            scn.setDemandPositionTolerance(tol)
            
            

medipix_camera_control = Finder.find("medipix_camera_control")
def set_medipix_roi(start_x, start_y, size_x, size_y) :
    medipix_camera_control.setRoi(start_x, start_y, size_x, size_y)
    
def get_medipix_roi() :
    return medipix_camera_control.getRoi()


from gda.device.scannable import CombinedAxisCalculator, MotorOffsetStore
xy_combined_calculator = CombinedAxisCalculator() 
xy_combined_calculator.setOrigin(5,4)
xy_combined_calculator.setAxisAngle(-14.43)

from uk.ac.gda.core.virtualaxis import CombinedManipulator
xes_detector_mover = CombinedManipulator()
xes_detector_mover.setName("xes_detector_mover")
xes_detector_mover.setScannables([xes_det_x, xes_det_y])
xes_detector_mover.setCalculator(xy_combined_calculator)
xes_detector_mover.configure()

xes_motor_offset_store = MotorOffsetStore()
xes_motor_offset_store.setName("xes_motor_offset_store")
xes_motor_offset_store.setXesEnergyScannable(XESEnergyJohann)

dummy_x = DummyScannable("dummy_x")
dummy_y = DummyScannable("dummy_y")
dummy_xy = [dummy_x, dummy_y]
xes_detector_xy = [xes_det_x, xes_det_y]

def get_data_dir() :
    # return "/scratch/gda/9.32/gda_data_non_live/2023/0-0/"
    # return "/dls/i18/data/2023/cm33872-5/"
    return InterfaceProvider.getPathConstructor().createFromDefaultProperty()+"/"

def save_motor_offsets(subdir, name) :
    datadir=get_data_dir()
    fullpath=datadir+subdir
    print("Saving motor offsets to %s/%s.xml"%(fullpath, name))
    xes_motor_offset_store.saveOffsets(fullpath, name)
    
def load_motor_offsets(subdir, name) :
    datadir=get_data_dir()
    fullpath=datadir+subdir
    print("Loading motor offsets from %s/%s.xml"%(fullpath, name))
    xes_motor_offset_store.loadOffsets(fullpath, name)
    
def setup_axis_calculator(axis_calculator) : 
    pitch = -1.0*xes_det_pitch.getPosition()
    det_x = xes_det_x.getPosition()
    det_y = xes_det_y.getPosition()
    print("Setting up axis calculator to match current detector orientation (x = %.4f, y = %.4f, pitch = %.4f)"%(det_x, det_y, pitch))
    
    axis_calculator.setAxisAngle(pitch)
    axis_calculator.setOrigin(det_x, det_y)

def set_xmap_use_tfg() :
    xmapMca.setTfg(counterTimer01.getTimer())

def set_xmap_live_time(time_sec) :
    # clear the Tfg object, so that busy status is determined only by the detector
    # xmapMca.setTfg(None)

    # Set the real preset mode to 'real time' : 
    CAClient.put("BL18I-EA-DET-07:PresetMode", 1)
    # Set the required 'preset real time' :
    CAClient.put("BL18I-EA-DET-07:PresetReal", time_sec)
