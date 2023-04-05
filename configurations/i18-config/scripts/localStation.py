from uk.ac.gda.server.exafs.scan.preparers import I18BeamlinePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18DetectorPreparer
from uk.ac.gda.server.exafs.scan.preparers import I18SamplePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18OutputPreparer
from uk.ac.gda.server.exafs.scan import XasScanFactory, XesScanFactory
from uk.ac.gda.client.microfocus.scan import MapSelector, MapFactory

from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from gda.device.scannable import TopupChecker
from gda.device.scannable import BeamMonitor
from gda.device.scannable import DetectorFillingMonitorScannable
from gda.factory import Finder
from stageSelector import StageSelector
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.jython.commands.ScannableCommands import add_default

from mapping_scan_commands import static

from mapping_scan_commands import mscan, grid, detector, mstep, rect
from org.eclipse.scanning.api.points.models import AxialStepModel
from gdascripts.watchdogs.watchdogs import enableWatchdogs, disableWatchdogs, listWatchdogs, topup_watchdog, beam_available_watchdog, set_watchdog_enabled, is_watchdog_enabled
from gdascripts.malcolm.malcolm import reset_malcolm_after_scan
from diffraction_calibration_appender import DiffractionAppenderManager

from gdaserver import Xspress3A
from gdascripts.detectors.initialise_detector import initialise_detector

def xes_dummy_prep(det_y_pos=475.0, xtal_x_pos=1000.0, radius_length=1000.0, det_y_speed=10000, xtal_x_speed=10000, scn_speed=10000):
    if material() == None:
        material('Si')
    det_y.getMotor().setSpeed(det_y_speed)
    xtal_x.getMotor().setSpeed(xtal_x_speed)
    
    # Set positions of some scannables to reasonable positions so that XESBragg calculation has a chance of working
    for scn in spectrometer_all_scannables.getGroupMembers():
        if str(scn.getName())!='radius':
            scn.getMotor().setSpeed(scn_speed)
    
    for crys in crystalsAllowedToMove.getGroupMembers():
        crys.moveTo("true")
    
    pos det_y det_y_pos
    pos xtal_x xtal_x_pos
    pos radius radius_length
    
    for cut in [cut1, cut2, cut3]:
        cut.moveTo(1)
    print("All Moves Complete")

def setup_monitors():
    global topupMonitor
    topupMonitor = TopupChecker()
    topupMonitor.setName("topupMonitor")
    topupMonitor.setTolerance(2.0)
    topupMonitor.setWaittime(1.0)
    topupMonitor.setTimeout(600.0)
    topupMonitor.setMachineModeMonitor(beam_state) # @UndefinedVariable
    topupMonitor.setScannableToBeMonitored(topup_start_countdown_complete) # @UndefinedVariable
    topupMonitor.setLevel(999) # so this is the last thing to be called before data is collected, to save time for motors to move
    topupMonitor.configure()
    
    global beamMonitor
    beamMonitor = BeamMonitor()
    beamMonitor.setName("beamMonitor")
    beamMonitor.setShutterPVs(["FE18I-RS-ABSB-01:STA"])
    beamMonitor.setMachineModeMonitor(beam_state) # @UndefinedVariable
    beamMonitor.configure()
    
    global detectorFillingMonitor
    detectorFillingMonitor = DetectorFillingMonitorScannable()
    detectorFillingMonitor.setName("detectorFillingMonitor")
    detectorFillingMonitor.setStartTime(9)
    detectorFillingMonitor.setDuration(25.0)
    
    detectorFillingMonitor.configure()
    
    add_default(topupMonitor)
    add_default(beamMonitor)
    # don't add detectorFillingMonitor as a default

def setup_watchdogs():
    topup_watchdog.setEnabled(True)
    beam_available_watchdog.setEnabled(True)

def setup_factories():
    theFactory = XasScanFactory();
    theFactory.setBeamlinePreparer(beamlinePreparer);
    theFactory.setDetectorPreparer(detectorPreparer);
    theFactory.setSamplePreparer(samplePreparer);
    theFactory.setOutputPreparer(outputPreparer);
    theFactory.setLoggingScriptController(XASLoggingScriptController);
    theFactory.setEnergyScannable(energy_scannable_for_scans);
    theFactory.setMetashop(Finder.find("metashop"));
    theFactory.setIncludeSampleNameInNexusName(True);
    theFactory.setScanName("energyScan")
    
    
    global xas
    xas = theFactory.createEnergyScan();
    xanes = xas
    
    theFactory.setQexafsDetectorPreparer(detectorPreparer);
    theFactory.setQexafsEnergyScannableForConstantVelocityScan(zebraBraggEnergy); # @UndefinedVariable
    theFactory.setQexafsNXDetectorList([qexafsXspress3FFI0]) # @UndefinedVariable
    qexafs = theFactory.createQexafsConstantVelocityScan()
    
    mapFactory = MapFactory();
    mapFactory.setBeamlinePreparer(beamlinePreparer);
    mapFactory.setDetectorPreparer(detectorPreparer);
    mapFactory.setSamplePreparer(samplePreparer);
    mapFactory.setOutputPreparer(outputPreparer);
    mapFactory.setLoggingScriptController(XASLoggingScriptController);
    mapFactory.setEnergyWithGapScannable(energy); # @UndefinedVariable
    mapFactory.setEnergyNoGapScannable(energy_nogap); # @UndefinedVariable
    mapFactory.setMetashop(Finder.find("metashop"));
    mapFactory.setIncludeSampleNameInNexusName(True);
    mapFactory.setCounterTimer(counterTimer01); # @UndefinedVariable
    mapFactory.setxScan(t1x); # @UndefinedVariable
    mapFactory.setyScan(t1y); # @UndefinedVariable
    mapFactory.setzScan(t1z); # @UndefinedVariable
    mapFactory.setElementListScriptController(elementListScriptController);
    mapFactory.setScanName("step map")

    non_raster_map = mapFactory.createStepMap()
    
    map = MapSelector(beamlinePreparer, non_raster_map) # @UndefinedVariable @ReservedAssignment
    map.setStage1X(t1x) # @UndefinedVariable
    map.setStage1Y(t1y) # @UndefinedVariable
    map.setStage1Z(t1z) # @UndefinedVariable
    map.setStage3X(t3x) # @UndefinedVariable
    map.setStage3Y(t3y) # @UndefinedVariable
    map.setStage3Z(t3z) # @UndefinedVariable
    
    map.setStage(1)
    
    if live_mode and (beam_state() == 'User' or beam_state() == 'BL Startup' or beam_state() == 'Special'): # @UndefinedVariable
        map.enableUseIDGap()
    else:
        map.disableUseIDGap()

    selectStage = StageSelector(map)
    alias("selectStage")
    selectStage(1)

def setup_aliases():
    # Watchdogs
    alias("enableWatchdogs")
    alias("disableWatchdogs")
    alias("listWatchdogs")
    # mapping
    vararg_alias("xas")
    vararg_alias("xanes")
    vararg_alias("qexafs")
    vararg_alias("map")
    alias("meta_add")
    alias("meta_ll")
    alias("meta_ls")
    alias("meta_rm")

def fix_snapshot():
    # In order to perform AcquireRequests with Xspress3 we must initialise the plugin array:
    if live_mode:
        initialise_detector("Xspress3", Xspress3A.getAdBase().getBasePVName(), Xspress3A.getNdArray().getBasePVName(), "Software")
    else:
        initialise_detector("Xspress3", Xspress3A.getAdBase().getBasePVName(), Xspress3A.getNdArray().getBasePVName(), "Internal", "Single")
        
def set_energy_scannable(scannable):
    global xas
    xas.setEnergyScannable(scannable)

def print_useful_info():
    useful_info = """
    ****************************************
    Useful commands:
    
    Select energy scannable for scans:
     set_energy_scannable(energy_nogap_lut) # one of energy, energy_nogap, energy_lut, energy_nogap_lut
    
    Disable/enable all watchdogs:
     disableWatchdogs()/enableWatchdogs()
    
    List the watchdogs:
      listWatchdogs
    
    Disable/enable a single watchdog e.g. topup:
     topup_watchdog.setEnabled(False)/(True)
    
    Specify calibration and mask files for Excalibur:
     excalibur_metadata.set_calibration_file(...)
     excalibur_metadata.set_mask_file(...)
     
    To fix snapshots after detector IOC restart:
     fix_snapshot()
    ****************************************
    """
    print(useful_info)

def setup():
    print("Initialisation started...\n");

    global live_mode
    live_mode = LocalProperties.get("gda.mode") == 'live'
    
    test = DummyScannable("test")
    
    setup_monitors()
    setup_watchdogs()
    
    global XASLoggingScriptController
    global elementListScriptController
    rcpController =                Finder.find("RCPController")
    XASLoggingScriptController =   Finder.find("XASLoggingScriptController")
    ExafsScriptObserver =          Finder.find("ExafsScriptObserver")
    auto_mDeg_idGap_mm_converter = Finder.find("auto_mDeg_idGap_mm_converter_Si111")
    loggingcontroller =            Finder.find("XASLoggingScriptController")
    datawriterconfig =             Finder.find("datawriterconfig")
    if Finder.find("datawriterconfig").getHeader() != None:
        original_header = Finder.find("datawriterconfig").getHeader()[:]
    elementListScriptController = Finder.find("elementListScriptController")
    
    global detectorPreparer
    sensitivities = [I0_stanford_sensitivity, It_stanford_sensitivity] # @UndefinedVariable
    sensitivity_units = [I0_stanford_sensitivity_units, It_stanford_sensitivity_units] # @UndefinedVariable
    detectorPreparer = I18DetectorPreparer(sensitivities, sensitivity_units, counterTimer01, xspress3, raster_counterTimer01, raster_xspress3, raster_FFI0_xspress3) # @UndefinedVariable
    
    global beamlinePreparer
    global samplePreparer
    global outputPreparer
    samplePreparer   = I18SamplePreparer() # @UndefinedVariable
    outputPreparer   = I18OutputPreparer(datawriterconfig, Finder.find("metashop"))
    beamlinePreparer = I18BeamlinePreparer(topupMonitor, beamMonitor, detectorFillingMonitor, energy, energy_nogap, auto_mDeg_idGap_mm_converter) # @UndefinedVariable
    
    global energy_scannable_for_scans
    if live_mode and (beam_state() == 'User' or beam_state() == 'BL Startup' or beam_state() == 'Special'): # @UndefinedVariable
        energy_scannable_for_scans = energy # @UndefinedVariable
    else:
        energy_scannable_for_scans = energy_nogap # @UndefinedVariable
    
    # simulation
    if not live_mode:
        energy(7000) # @UndefinedVariable
        energy_nogap(7000) # @UndefinedVariable
    
    setup_factories()
    setup_aliases()
    fix_snapshot()
    set_energy_scannable(energy_scannable_for_scans)
    excalibur_metadata = DiffractionAppenderManager("excalibur_calibration_appender", "excalibur_mask_appender")
    print("\n...initialisation complete!")
    print_useful_info()
    
    
    #  Make the spectrometer setup functions available
    run "spectrometer-setup.py"
    if LocalProperties.isDummyModeEnabled() :
        setup_dummy_spectrometer(XESEnergy)
    set_initial_crystal_values(XESEnergy)
    
    run "tfgSetup.py"
    tfg=TFG()

setup()
