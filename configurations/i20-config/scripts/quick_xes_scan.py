print("\nRunning quick_xes_scans.py")

from org.eclipse.scanning.sequencer import ScanRequestBuilder
from mapping_scan_commands import submit
from org.eclipse.scanning.api.points.models import StaticModel, AxialStepModel, CompoundModel
from uk.ac.diamond.osgi.services import ServiceProvider
from org.eclipse.scanning.command.Services import getRunnableDeviceService
from uk.ac.gda.api.io import PathConstructor
from gda.device.scannable import PVScannable

from os import name

XesMotorOffsetsLower = Finder.find("XesMotorOffsetsLower")
XesMotorOffsetsUpper = Finder.find("XesMotorOffsetsUpper")

# Path to script to show axis setup Edm screen :
# /dls_sw/work/R3.14.12.7/support/BL20I-BUILDER/iocs/BL20I-MO-IOC-37/bin/linux-x86_64/stBL20I-MO-IOC-37-gui &

# axis_detector_map_malcolm = {XESEnergyLower : ("xes_02_xtal_lo_pitch", "BL20I-ML-SCAN-01"),  XESEnergyUpper : ("xes_01_xtal_up_pitch", "BL20I-ML-SCAN-01")}

axis_detector_map_malcolm = {XESEnergyBoth : ("xes_01_xtal_all_pitch", "BL20I-ML-SCAN-02"), XESEnergyLower : ("xes_02_xtal_lo_pitch", "BL20I-ML-SCAN-01"),  XESEnergyUpper : ("xes_01_xtal_up_pitch", "BL20I-ML-SCAN-01")}

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
    pitch_start, pitch_end, pitch_step = calculate_pitch_for_scan(xes_energy_scn, energy_start, energy_end, energy_step)
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

class HardwarePreparer() :
    
    def reset_medipix(self) :
        print("Setting Medipix trigger mode to internal, PositionMode to 0 and XML layout path to default")
        
        # PV name - value pairs to be set on each medipix
        posMode = ":HDF5:PositionMode", 0
        triggerMode = ":CAM:TriggerMode", 0
        layout = ":HDF5:XMLFileName", ""
        value_pairs = [posMode, triggerMode, layout]
        
        # Generate Medipix basePV names from ADBase on medipix ADDetector objects
        detectors = [medipix1_addetector, medipix2_addetector]
        base_pvs = [det.getAdBase().getBasePVName().replace(":CAM:","") for det in detectors]
    
        for basename in base_pvs :
            for value_pair in value_pairs :
                pv_name = basename+value_pair[0]
                pv_value = value_pair[1]
                # eet appropriate caput method to use - in case dealing with a string
                caput_pv_value = CAClient.putStringAsWaveform if isinstance(pv_value, str) else CAClient.put
                print("Caput %s %s"%(pv_name, str(pv_value)))
                caput_pv_value(pv_name, pv_value)

    def setup_panda_offsets(self, debug=False) :
        motor_order = ["C", "P1", "P2", "P3", "M1", "M2", "M3"]
        spec_pitch_pv_base = "BL20I-EA-XES-0%d:XTAL:%s:PITCH"
        panda_posbus_pv_pattern = "BL20I-EA-PANDA-0%d:DRV:POSBUS%d:SETPOS"
        
        # Generate PV names for the pitch positions (upper row, then lower row - in same order as motor_order list)
        pitch_pvs=[]
        for row in 1, 2 :
            pitch_pvs.extend(spec_pitch_pv_base%(row, xtl) for xtl in motor_order)
            
        ## Generate pv names that correspond to panda position capture for each motor (same order of motors as in pitch_pvs list)
        posbus_pvs = []
        for panda_idx in 1, 2, 3, 4 :
            max_val = 3 if panda_idx%2==0 else 4 
            for pos_idx in range(max_val) :
                posbus_pvs.append( panda_posbus_pv_pattern%(panda_idx, pos_idx))
                if debug :
                    print(panda_idx, pos_idx)
        
        # Compute the new posbus value for each pitch motor and apply to Panda 
        mres_value = float(CAClient.get(pitch_pvs[0]+".MRES"))
        print("Setting panda offset values using pitch readback (mres = %.4g)"%(mres_value))
        
        if LocalProperties.isDummyModeEnabled() :
            print("Skipping - dummy mode enabled")
            return
        
        for rbv_pv, posbus_pv in zip(pitch_pvs, posbus_pvs) :
            readback = float(CAClient.get(rbv_pv+".RBV"))
            #  Compute new posbus value : absolute value of readback/mres
            new_posbus_val = math.fabs(readback/mres_value)
            if debug : 
                print("%s = %.4f , setting %s = %d"%(rbv_pv, readback, posbus_pv, new_posbus_val))
            CAClient.put(posbus_pv, new_posbus_val)

class XesAxisControl : 
    def __init__(self) :
        self.create_axis_control_scannables()

    def create_axis_control_scannables(self) :
        self.upper_enable = PVScannable("qxes_upper_enable", "BL20I-EA-XES-01:CS3:UP:ENA")
        self.lower_enable = PVScannable("qxes_lower_enable", "BL20I-EA-XES-02:CS3:LO:ENA")
        self.lower_gain =   PVScannable("qxes_lower_gain",   "BL20I-EA-XES-02:CS3:LO:GAIN")
        self.lower_offset = PVScannable("qxes_lower_offset", "BL20I-EA-XES-02:CS3:LO:OFFSET")
        
        scannables = [self.upper_enable, self.lower_enable, self.lower_gain, self.lower_offset]
        for scn in scannables : 
            scn.configure()

    def calculate_gain_offset(self, start_energy_upper, end_energy_upper, start_energy_lower, end_energy_lower) :
        """
            Calculate the malcolm scan pitch 'offset' and 'gain' from upper and lower row start
            and end energies so that : pitch_lower = pitch_upper*gain + offset
            
            Return : gain, offset
        """
        upper_pitches = calculate_pitch_for_scan(XESEnergyUpper, start_energy_upper, end_energy_upper, 1.0)
        lower_pitches = calculate_pitch_for_scan(XESEnergyLower, start_energy_lower, end_energy_lower, 1.0)
        gain = (lower_pitches[0] - lower_pitches[1])/(upper_pitches[0] - upper_pitches[1])
        offset = lower_pitches[0] - upper_pitches[0]*gain
        return gain, offset
    
    def prepare_gain_offset(self, row1_start, row1_end, row2_start, row2_end) :
        gain, offset = self.calculate_gain_offset(row1_start, row1_end, row2_start, row2_end)
        print("Enabling both spectrometer rows and setting gain and offset to : %.4g, %.4g"%(gain, offset))
        
        if LocalProperties.isDummyModeEnabled() :
            print("Skipping - dummy mode enabled")
            return

        self.lower_gain.moveTo(gain)
        self.lower_offset.moveTo(offset)
        
    def convert_bool(self, istrue):
        return 1 if istrue else 0 
    
    def enable_upper(self, enable):
        self.upper_enable.moveTo(self.convert_bool(enable))
    
    def enable_lower(self, enable) :
        self.lower_enable.moveTo(self.convert_bool(enable))

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
    

def prepare_pitch_offsets(xes_energy_scn, xes_energy) :
    
    # move to initial energy
    print("Moving %s to energy %.4f"%(xes_energy_scn.getName(), xes_energy))
    xes_energy_scn.moveTo(xes_energy)
    sleep(2)
    print("Finished move")

    #calculate the pitch for given energy
    pitch_value = calculate_pitch(xes_energy_scn, xes_energy)
    
    print("Setting pitch of all analysers to %.4f :"%(pitch_value))
    
    # set current pitch value of each analyser to match central analyser
    pitch_motors = [cryst.getPitchMotor() for cryst in xes_energy_scn.getXes().getCrystalsList()]
    for pitch_mot in pitch_motors :
        print("\t%s = %.4f"%(pitch_mot.getName(), pitch_value))
        pitch_mot.setPosition(pitch_value)

def calculate_pitch(xes_energy_scn, energy) :
    # Get positions of all motors in spectrometer for given energy
    position = xes_energy_scn.getPositionsMap(energy)
    # motors for central analyser
    central_analyser = getAnalyserCrystal(xes_energy_scn, 0)
    # return the pitch value
    return position[central_analyser.getPitchMotor().getName()]

def calculate_pitch_for_scan(xes_energy_scn, start_energy, end_energy, step_energy):
    if isinstance(xes_energy_scn, ScannableGroup) :
        print("Using pitch values using first scannable in %s group"%(xes_energy_scn.getName()))
        xes_energy_scn = xes_energy_scn.getGroupMembers()[0]
    print("Calculating pitch using %s"%(xes_energy_scn.getName()))
    
    start_pitch = calculate_pitch(xes_energy_scn, start_energy)
    end_pitch = calculate_pitch(xes_energy_scn, end_energy)

    # Calculate the pitch step size
    grad = (end_pitch - start_pitch)/(end_energy - start_energy)
    step_pitch = math.fabs(step_energy*grad)
    if end_pitch < start_pitch :
        step_pitch *= -1.0
    
    print("Energy : start = %.3f, end = %.3f, step = %.4f"%(start_energy, end_energy, step_energy))
    print("Pitch  : start = %.4f, end = %.4f, step = %.5f"%(start_pitch, end_pitch, step_pitch))

    return start_pitch, end_pitch, step_pitch

def run_test_both() :
    restore_tmp_offsets(XESEnergyUpper)
    restore_tmp_offsets(XESEnergyLower)
    sleep(1)

    prepare_pitch_offsets(XESEnergyUpper, 8270)
    prepare_pitch_offsets(XESEnergyLower, 8270)
    
    xes_axis_control.prepare_gain_offset(8270, 8290, 8270, 8290)
    
    run_qxes_scan_energy(XESEnergyBoth, 8270, 8290, 0.5, 0.5, 5)

    restore_tmp_offsets(XESEnergyUpper)
    restore_tmp_offsets(XESEnergyLower)

    reset_medipix()
    
def run_test_upper() :
    restore_tmp_offsets(XESEnergyUpper)
    sleep(1)
    # prepare_pitch_offsets(XESEnergyUpper, 6404)
    # run_qxes_scan_energy(XESEnergyUpper, 6400, 6410, 0.25, 0.5, 5)
    prepare_pitch_offsets(XESEnergyUpper, 8264)
    run_qxes_scan_energy(XESEnergyUpper, 8264, 8268, 0.25, 0.5, 5)

    restore_tmp_offsets(XESEnergyUpper)
    reset_medipix()

def run_test_lower() :
    restore_tmp_offsets(XESEnergyLower)
    sleep(1)
    prepare_pitch_offsets(XESEnergyLower, 8264)
    run_qxes_scan_energy(XESEnergyLower, 8264, 8268, 0.25, 1.0, 5, outer_scannable=pos_time_scn)
    #run_qxes_scan_energy(XESEnergyLower, 8264, 8268, 0.25, 0.5)
    restore_tmp_offsets(XESEnergyLower)
    reset_medipix()


def test_qxes() :
    start = -7.7
    end = -7.4
    step_size = 0.01
    exp_time = 0.1
    run_qxes_scan(XESEnergyLower, start, end, step_size, exp_time, use_malcolm = True, continuous_scan = True)


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

from gda.device.scannable import DummyScannable, TimeScannable
repetition_number_scn = DummyScannable("repetition_number_scn")
repetition_number_scn.configure()

pos_time_scn = PositionTimeScannable()
pos_time_scn.setup("pos_time_scn")
pos_time_scn.setScannableToMove(repetition_number_scn)
pos_time_scn.setUseUtcTime(True)


def prepare_run_qxes_scan(scannable_name, energy_start, energy_end, energy_step_size, integration_time, 
                          row2_energy_start=None, row2_energy_step_size=None,
                          is_alternating=False, num_reps=1, mono_energy=None, use_malcolm=True) :
    
    xes_energy_scannable = Finder.find(scannable_name) 
    if xes_energy_scannable is None : 
        raise ValueError("Scannable called "+scannable_name+" was not found")
    

    xes_scannables = xes_energy_scannable,
    xes_energies = energy_start,

    if xes_energy_scannable == XESEnergyBoth : 
        
        # Validate the params
        warnings = ""
        if row2_energy_start is None :
            row2_energy_start = energy_start
            warnings += "Row 2 start energy value has not been given. Using start energy from row 1 ("+str(energy_start)+")\n"
        if row2_energy_step_size is None :
            row2_energy_step_size = energy_step_size
            warnings += "nRow 2 energy step size value has not been given. Using step size from row 1 ("+str(energy_step_size)+")\n"
            
        if len(warnings) > 0 :
            print(warnings)

        xes_scannables = XESEnergyUpper, XESEnergyLower
        xes_energies = energy_start, row2_energy_start

    print("Running Qxes scan using : "+str(xes_scannables))
    print("Time per point : %.2f sec"%(integration_time))
    print("Row 1 energy start, stop, step : %.4g, %.4g, %.4g\n"%(energy_start, energy_end, energy_step_size))
    if row2_energy_start is not None : 
        print("Row 2 energy start, step : %.4g, %.4g\n"%(row2_energy_start, row2_energy_step_size))

    if mono_energy is not None : 
        print("Moving mono to %.4g eV"%(mono_energy))
        bragg1WithOffset.moveTo(mono_energy)

    # Save the current pitch offsets, set new offsets so that pitch values are all the same for start energy
    for scn, energy in zip(xes_scannables, xes_energies) :
        restore_tmp_offsets(scn)
        sleep(1)
        prepare_pitch_offsets(scn, energy)
    
    # Set the 'gain' and 'offset' parameters for row2 based on row1
    if xes_energy_scannable == XESEnergyBoth : 
        # Calculate row2 end energy from number of row1 steps and row2 step size.
        num_steps = int( (energy_end-energy_start)/energy_step_size)
        row2_energy_end = row2_energy_start + row2_energy_step_size*abs(num_steps)
        xes_axis_control.prepare_gain_offset(energy_start, energy_end, row2_energy_start, row2_energy_end)
        xes_axis_control.enable_lower(True)
        xes_axis_control.enable_upper(True)
    else :
        xes_axis_control.prepare_gain_offset(energy_start, energy_end, energy_start, energy_end)
        xes_axis_control.enable_lower(xes_energy_scannable == XESEnergyLower)
        xes_axis_control.enable_upper(xes_energy_scannable == XESEnergyUpper)
        
    print("Upper row enable : "+str(xes_axis_control.upper_enable.getPosition()))
    print("Lower row enable : "+str(xes_axis_control.lower_enable.getPosition()))

    if bragg1WithOffset.isBusy() :
        print("Waiting for mono to finish moving before starting scan")
        bragg1WithOffset.waitWhileBusy()
    
    xes_hardare_preparer.setup_panda_offsets()
    
    run_qxes_scan_energy(XESEnergyBoth, energy_start, energy_end, energy_step_size, integration_time, num_reps, 
                         outer_scannable=pos_time_scn, is_alternating=is_alternating, use_malcolm=use_malcolm)

    for scn in xes_scannables :
        restore_tmp_offsets(scn)
    
    reset_medipix()


# clear the subdirectory, so data is written in top level of visit.
set_subdirectory()

xes_hardare_preparer = HardwarePreparer()
xes_axis_control = XesAxisControl()

reset_medipix = xes_hardare_preparer.reset_medipix
reset_medipix()

