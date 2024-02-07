"""

"""

from org.eclipse.scanning.sequencer import ScanRequestBuilder
from org.eclipse.scanning.api.points.models import StaticModel, AxialStepModel, CompoundModel
from uk.ac.diamond.osgi.services import ServiceProvider
from mapping_scan_commands import submit, getRunnableDeviceService
from uk.ac.gda.api.io import PathConstructor

from __builtin__ import False, True, None
from os import name

XesMotorOffsetsLower = Finder.find("XesMotorOffsetsLower")
XesMotorOffsetsUpper = Finder.find("XesMotorOffsetsUpper")

axis_detector_map_malcolm = {XESEnergyLower : ("xes_02_xtal_lo_pitch", "BL20I-ML-SCAN-01"),  XESEnergyUpper : ("xes_01_xtal_up_pitch", "BL20I-ML-SCAN-01")}

# axes for doing software malcolm scan (dummy mode).
axis_detector_map_gda = {XESEnergyLower : ("lower_zero_pitch", "medipix2_addetector"),  XESEnergyUpper : ("upper_zero_pitch", "medipix1_addetector")}

motor_offset_store_map = {XESEnergyLower:XesMotorOffsetsLower, XESEnergyUpper:XesMotorOffsetsUpper}

# Submit scan request to queue and block until completion
def run_mapping_scan(scan_request, scan_name="QXES") :
    print("Running scan")
    try :
        submit(scan_request, block=True, name=scan_name)
        print("Run complete")
    except Exception as e:
        print("Exception running scan",e)

def run_qxes_scan_energy(xes_energy_scn, energy_start, energy_end, energy_step, exposure_time=0.1, num_reps=1, outer_scannable=None, use_malcolm = True, continuous_scan = True, is_alternating=True):
    pitch_start, pitch_end, pitch_step = calculate_scan_pitch_for_scan(xes_energy_scn, energy_start, energy_end, energy_step)
    if num_reps > 1 and outer_scannable is not None :
        run_qxes_scan_pitch_reps(xes_energy_scn, pitch_start, pitch_end, pitch_step, exposure_time, num_reps, outer_scannable, use_malcolm, continuous_scan, is_alternating)
    else :
        run_qxes_scan_pitch(xes_energy_scn, pitch_start, pitch_end, pitch_step, exposure_time, use_malcolm, continuous_scan)

def run_qxes_scan_pitch(xes_energy_scn, pitch_start, pitch_end, pitch_step, exposure_time=0.1, use_malcolm = True, continuous_scan = True):
    
    # lookup detector and axis name to use for given XESEnergyScannable object
    axis_det_pair = axis_detector_map_malcolm[xes_energy_scn] if use_malcolm else axis_detector_map_gda[xes_energy_scn]
    axis_name = axis_det_pair[0]
    detector_name = axis_det_pair[1]
    
    print("Running scan using %s with %s detector (exposure time = %.2f sec)"%(axis_name, detector_name, exposure_time))
    print("Scan start, stop, step : %.5f, %.5f, %.5f"%(pitch_start, pitch_end, pitch_step))

    # Get detector runnable device
    detector_device = getRunnableDeviceService().getRunnableDevice(detector_name)
    if detector_device is None :
        raise Exception("Could not find runnable device for detector called "+detector_name)
    
    # Set the exposure time on detector model
    detector_model = detector_device.getModel()
    detector_model.setExposureTime(exposure_time)
    detectors = {detector_model.getName() : detector_model}
    
    # Make step scan style model with single axis
    path_model = AxialStepModel(axis_name, pitch_start, pitch_end, pitch_step)
    path_model.setContinuous(continuous_scan)
    
    # Generate ScanRequest using the builder
    request = ScanRequestBuilder().withPathAndRegion(path_model, None).withDetectors(detectors).build()
    name_for_queue = "Qxes (Malcolm)" if use_malcolm else "Qxes"
    run_mapping_scan(request, scan_name=name_for_queue)

def run_qxes_scan_pitch_reps(xes_energy_scn, pitch_start, pitch_end, pitch_step, exposure_time=0.1, num_reps=2, outer_scannable=None, use_malcolm = True, continuous_scan = True, is_alternating=True):
    
    # lookup detector and axis name to use for given XESEnergyScannable object
    axis_det_pair = axis_detector_map_malcolm[xes_energy_scn] if use_malcolm else axis_detector_map_gda[xes_energy_scn]
    axis_name = axis_det_pair[0]
    detector_name = axis_det_pair[1]
    
    print("Running scan using %s with %s detector (exposure time = %.2f sec)"%(axis_name, detector_name, exposure_time))
    print("Scan start, stop, step : %.5f, %.5f, %.5f"%(pitch_start, pitch_end, pitch_step))
    print("Number of repetitions : %d"%(num_reps))
    
    # Get detector runnable device
    detector_device = getRunnableDeviceService().getRunnableDevice(detector_name)
    if detector_device is None :
        raise Exception("Could not find runnable device for detector called "+detector_name)
    
    # Set the exposure time on detector model
    detector_model = detector_device.getModel()
    detector_model.setExposureTime(exposure_time)
    detectors = {detector_model.getName() : detector_model}
    
    # Create model for outer axis : dummy scannable that just tracks the current repetition number
    path_model_outer = AxialStepModel(outer_scannable.getName(), 0, num_reps-1, 1)
    path_model_outer.setContinuous(False)

    # Model for the inner axis : step scan style model with single axis
    path_model_inner = AxialStepModel(axis_name, pitch_start, pitch_end, pitch_step)
    path_model_inner.setContinuous(continuous_scan)
    path_model_inner.setAlternating(is_alternating)
    
    # Compount model : outer axis is dummy scannable, inner axis is continuous malcolm scan
    path_model = CompoundModel([path_model_outer, path_model_inner])
    
    # Generate ScanRequest using the builder
    request = ScanRequestBuilder().withPathAndRegion(path_model, None).withDetectors(detectors).build()
    name_for_queue = "Qxes (Malcolm)" if use_malcolm else "Qxes"
    run_mapping_scan(request, scan_name=name_for_queue)

def test_qxes() :
    start = -7.7
    end = -7.4
    step_size = 0.01
    exp_time = 0.1
    run_qxes_scan(XESEnergyLower, start, end, step_size, exp_time, use_malcolm = True, continuous_scan = True)

# Return the name of the current data directory (including subdirectory)
def pwd() :
    return InterfaceProvider.getPathConstructor().createFromDefaultProperty()

# Return visit directory (i.e. top level data directory, without subdirectory)
def get_visit_dir() :
    pc = PathConstructor()
    return pc.getVisitDirectory()

# Set subdirectory to use for writing files
def set_subdirectory(dirname=""):
    Finder.find("GDAMetadata").setMetadataValue("subdirectory", dirname)

medipix1_camera_control=Finder.find("medipix1_camera_control")
medipix2_camera_control=Finder.find("medipix2_camera_control")
# Set the medipix ROI directly on the ROI plugin, using CameraControlForLiveStream
def set_medipix_roi(medipix, xstart, ystart, xsize, ysize) :    
    cam_control =  medipix1_camera_control if medipix == medipix1 else medipix2_camera_control
    cam_control.setRoi(xstart, ystart, xsize, ysize)


# Generate path to the directory used to store temporary motor offset file
# i.e. : 'tmp folder in current visit directory
def get_tmp_offset_dir() :
    current_data_dir = get_visit_dir()
    return current_data_dir+"/tmp"


# Save the current set of Epics motor offset values to a temporary file
def save_tmp_offsets(xes_energy_scn) :
    directory=get_tmp_offset_dir()
    filename = "tmp_current_offsets_"+xes_energy_scn.getName()
    print("Saving temporary current offsets to {}/{}.xml".format(directory, filename))
    offsets_object = motor_offset_store_map[xes_energy_scn]
    offsets_object.saveOffsets(directory, filename)
    
# Restore offsets from temporary file
def restore_tmp_offsets(xes_energy_scn) :
    directory=get_tmp_offset_dir()
    filename = "tmp_current_offsets_"+xes_energy_scn.getName()
    print("Restoring temporary offsets from {}/{}.xml".format(directory, filename))
    offsets_object = motor_offset_store_map[xes_energy_scn]
    offsets_object.loadOffsets(directory, filename)
    
def restore_offsets(xes_energy_scn, offset_dir="/dls/i20/data/2023/cm33869-5/xml",  offset_file="lowerOffset_ZnKb_141123") :
    print("Restoring offsets from : {}/{}".format(offset_dir, offset_file))
    offsets_object = motor_offset_store_map[xes_energy_scn]
    offsets_object.loadOffsets(offset_dir, offset_file)
    
def prepare_for_scan(xes_energy_scn, start_energy) :
    #calculate the pitch start, end, step size for given energy parameters
    pitch_vals = calculate_scan_pitch_for_scan(xes_energy_scn, start_energy, start_energy+1, 1.0)
    
    # move to initial energy
    print("Moving %s to energy %.4f"%(xes_energy_scn.getName(), start_energy))
    xes_energy_scn.moveTo(start_energy)
    sleep(2)
    print("Finished move")
    # set current pitch value of each analyser to match central analyser
    set_analyser_pitch_offsets(xes_energy_scn, pitch_vals[0])
    return pitch_vals

def calculate_scan_pitch_for_scan(xes_energy_scn, start_energy, end_energy, step_energy):
    
    # calculate the start and energy spectrometer positions for the start and end energies
    start_positions = xes_energy_scn.getPositionsMap(start_energy)
    end_positions = xes_energy_scn.getPositionsMap(end_energy)
    
    # get the pitch start and end pitch value for the central analayser
    central_analyser = getAnalyserCrystal(xes_energy_scn, 0)
    central_pitch_name = central_analyser.getPitchMotor().getName()
    start_pitch = start_positions[central_pitch_name]
    end_pitch = end_positions[central_pitch_name]

    # Calculate the pitch step size
    grad = (end_pitch - start_pitch)/(end_energy - start_energy)
    step_pitch = math.fabs(step_energy*grad)
    if end_pitch < start_pitch :
        step_pitch *= -1.0
    
    print("Energy : start = %.3f, end = %.3f, step = %.4f"%(start_energy, end_energy, step_energy))
    print("Pitch  : start = %.4f, end = %.4f, step = %.5f"%(start_pitch, end_pitch, step_pitch))

    return start_pitch, end_pitch, step_pitch

def set_analyser_pitch_offsets(xes_energy_scn, pitch_value) :
    print("Setting pitch of all analysers to %.4f :"%(pitch_value))
    ### store the offsets first!
    for pitch_mot in get_pitch_motors(xes_energy_scn) :
        print("\t%s = %.4f"%(pitch_mot.getName(), pitch_value))
        pitch_mot.setPosition(pitch_value)
        
def get_pitch_motors(xes_energy_scn):
    pitch_motors = []
    for cryst in xes_energy_scn.getXes().getCrystalsList() :
        pitch_motors.append(cryst.getPitchMotor())
    return pitch_motors

# restore_offsets(XESEnergyLower, offset_file="lowerOffset_ZnKb_141123")
# save_tmp_offsets(XESEnergyLower)
# prepare_for_scan(XESEnergyLower, 2000)
# run_qxes_scan_energy(XESEnergyLower, 2000, 2010, 0.5, 0.
# restore_tmp_offsets(XESEnergyLower)

def run_test_upper() :
    restore_tmp_offsets(XESEnergyUpper)
    sleep(1)
    prepare_for_scan(XESEnergyUpper, 6404)
    run_qxes_scan_energy(XESEnergyUpper, 6400, 6410, 0.25, 0.5, 5)
    restore_tmp_offsets(XESEnergyUpper)
    reset_medipix()

def run_test_lower() :
    restore_tmp_offsets(XESEnergyLower)
    sleep(1)
    prepare_for_scan(XESEnergyLower, 7058)
    run_qxes_scan_energy(XESEnergyLower, 7055, 7065, 0.25, 0.5, 5, outer_scannable=pos_time_scn)
    restore_tmp_offsets(XESEnergyLower)
    reset_medipix()

def reset_medipix() :
    print("Setting Medipix trigger mode to internal and setting PositionMode to 0")
    posMode = ":HDF5:PositionMode", 0
    triggerMode = ":CAM:TriggerMode", 0
    medipix1_pv="BL20I-EA-DET-05"
    medipix2_pv="BL20I-EA-DET-07"
    for basename in medipix1_pv, medipix2_pv :
        CAClient.put(basename+posMode[0], posMode[1])
        CAClient.put(basename+triggerMode[0], triggerMode[1])

from gda.device.scannable import DummyScannable, TimeScannable
repetition_number_scn = DummyScannable("repetition_number_scn")
repetition_number_scn.configure()


class PositionTimeScannable(ScannableBase) :
    
    def setup(self, name) :
        self.setName(name)
        self.setInputNames([name])
        self.scn_to_move = None
        self.time_scn = TimeScannable("time_scn")
        self.move_sleep_time_sec = 0.0
        
    def setScannableToMove(self, scn):
        self.scn_to_move = scn
        
    def getOutputFormat(self) :
        return self.scn_to_move.getOutputFormat() + self.time_scn.getOutputFormat()
    
    def getExtraNames(self) :
        return [self.time_scn.getName()]
    
    def setUseUtcTime(self, tf) :
        self.time_scn.setUseUtcMillis(tf)
    
    def rawAsynchronousMoveTo(self, position):
        # print("Sleeping for %s sec"%(self.move_sleep_time_sec))
        sleep(self.move_sleep_time_sec)
        # print("Moving %s to %s"%(self.getName(), str(position)))
        self.scn_to_move.rawAsynchronousMoveTo(position)
    
    def isBusy(self) :
        return self.scn_to_move.isBusy()
    
    def getPosition(self):
        return [self.scn_to_move.getPosition(), self.time_scn.getPosition()]



pos_time_scn = PositionTimeScannable()
pos_time_scn.setup("pos_time_scn")
pos_time_scn.setScannableToMove(repetition_number_scn)
pos_time_scn.setUseUtcTime(True)


"""
Energy scan params : start, end, step size, time per point, 
Move spectrometer analysers into position for given energy
Store the current values of the Epics offsets (for pitch motors)
Take pitch of central analyser, set the current position of p1, p2, p3, m1, m2, m3 to match it (use setPosition() method on scannable)

Use : XESEnergyLower.getPositionsMap(energy) to compute positions for start, end energies
Get pitch motors from : getAnalyserCrystal(xesEnergyScn, crystalIndex) and analyserCrystal.getPitchMotor()
"""

"""
Testing 10/1/2024
XESEnergyLower :
    8030.27 eV
    offsets saved to tmp/tmp_current_offsets_XESEnergyLower.xml


"""

