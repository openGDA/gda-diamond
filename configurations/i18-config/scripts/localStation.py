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
from gda.jython.commands.ScannableCommands import add_default, remove_default

from mapping_scan_commands import static

from mapping_scan_commands import mscan, grid, detector, mstep, rect
from org.eclipse.scanning.api.points.models import AxialStepModel
from gdascripts.watchdogs.watchdogs import watchdogService, enableWatchdogs, disableWatchdogs, listWatchdogs, topup_watchdog, beam_available_watchdog, set_watchdog_enabled, is_watchdog_enabled
from gdascripts.malcolm.malcolm import reset_malcolm_after_scan
from diffraction_calibration_appender import DiffractionAppenderManager

from gdascripts.detectors.initialise_detector import initialise_detector
from gdascripts.metadata.metadata_commands import meta_add, meta_ll, meta_ls, meta_rm, meta_clear_alldynamical
from gdascripts.scan.gdascans import Rscan

def run_script(script_name):
    print("--- Running '"+script_name+"' ---")
    run(script_name)
    print("")
    
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

def setup_watchdogs():
    topup_watchdog.setEnabled(True)
    beam_available_watchdog.setEnabled(True)

def noBeamMode(noBeam):
    if noBeam:
        disableWatchdogs()
        remove_default(topupMonitor)
        remove_default(beamMonitor)
    else:
        enableWatchdogs()
        add_default(topupMonitor)
        add_default(beamMonitor)
    print "topup_watchdog Enabled: "+str(topup_watchdog.enabled)
    print "beam_available_watchdog Enabled: "+str(beam_available_watchdog.enabled)
    

def setup_factories():
    # creates qexafs_energy scannable
    run_script("qexafs_scans.py")

    theFactory = XasScanFactory();
    theFactory.setBeamlinePreparer(beamlinePreparer);
    theFactory.setDetectorPreparer(detectorPreparer);
    theFactory.setSamplePreparer(samplePreparer);
    theFactory.setOutputPreparer(outputPreparer);
    theFactory.setLoggingScriptController(XASLoggingScriptController);
    theFactory.setEnergyScannable(energy_scannable_for_scans);
    theFactory.setMetashop(Finder.find("metashop"));
    theFactory.setIncludeSampleNameInNexusName(True);
    
    
    global xas
    xas = theFactory.createEnergyScan();
    xanes = xas
    
    theFactory.setQexafsDetectorPreparer(detectorPreparer);
    theFactory.setQexafsEnergyScannable(qexafs_energy); # @UndefinedVariable
    global qexafs
    qexafs = theFactory.createQexafsScan()
    
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

    non_raster_map = mapFactory.createStepMap()
    
    map = MapSelector(beamlinePreparer, non_raster_map) # @UndefinedVariable @ReservedAssignment
    map.setStage1X(t1x) # @UndefinedVariable
    map.setStage1Y(t1y) # @UndefinedVariable
    map.setStage1Z(t1z) # @UndefinedVariable
    map.setStage3X(t3x) # @UndefinedVariable
    map.setStage3Y(t3y) # @UndefinedVariable
    map.setStage3Z(t3z) # @UndefinedVariable
    
    map.setStage(1)
    
    if live_mode and beam_available() :
        map.enableUseIDGap()
    else:
        map.disableUseIDGap()

    selectStage = StageSelector(map)
    alias("selectStage")
    selectStage(1)

def beam_available() :
    return beam_state() == 'User' or beam_state() == 'BL Startup' or beam_state() == 'Special'

def setup_aliases():
    # Watchdogs
    alias("enableWatchdogs")
    alias("disableWatchdogs")
    alias("listWatchdogs")
    alias("noBeamMode")
    # mapping
    vararg_alias("xas")
    vararg_alias("xanes")
    vararg_alias("qexafs")
    vararg_alias("map")
    alias("meta_add")
    alias("meta_ll")
    alias("meta_ls")
    alias("meta_rm")
    alias("meta_clear_alldynamical")
    
    # add 'rscan' (relative scan) command :
    global rscan
    rscan = Rscan()
    alias(rscan)

def set_energy_scannable(scannable):
    global xas
    xas.setEnergyScannable(scannable)

def print_useful_info():
    useful_info = """
    ****************************************
    Useful commands:
    
    Select energy scannable for XML (xas, xanes) scans:
     set_energy_scannable(energy_nogap_lut) # one of energy, energy_nogap, energy_lut, energy_nogap_lut
    
    Disable/enable all watchdogs:
     disableWatchdogs()/enableWatchdogs()
    
    List the watchdogs:
      listWatchdogs
    
    Disable/enable a single watchdog e.g. topup:
     topup_watchdog.setEnabled(False)/(True)
     
    Disable/enable all watchdogs and monitors that require beam (topup_watchdog, beam_available_watchdog, topupMonitor, beamMonitor):
     noBeamMode(True)/noBeamMode(False)
    
    Specify calibration and mask files for Excalibur:
     excalibur_metadata.set_calibration_file(...)
     excalibur_metadata.set_mask_file(...)
     
    Reload lookup table values from disk :
     reload_lookup_tables()

    Scannables to control Goniometer (BL18I-MO-TABLE-03:PITCH)
     xps_pitch - move using angle
     xps_energy_conv - move using energy (ev) (lookup table in lookuptables/gonio_lookup_table.txt)
     
    Energy scannables that also move Gonionmeter :
     energy_gonio, energy_nogap_gonio
     
    Change energy conversion scannables between Si311 and Si111 :
     setup_for_Si333() , setup_for_Si111()

    ****************************************
    """
    print(useful_info)

def set_energy_output_format() :
    out_format="%.4f"
    print("Setting output format of energy scannables to : "+out_format)
    dets = [energy_Si111, energy_Si311, energy_nogap_Si111, energy_nogap_Si311]
    for d in dets :
        d.setOutputFormat([out_format])

def setup():
    print("Initialisation started...\n");

    global live_mode
    live_mode = LocalProperties.get("gda.mode") == 'live'
    global test
    test = DummyScannable("test")
    
    setup_monitors()
    setup_watchdogs()
    if not live_mode or not beam_available() :
        print("Machine mode = "+beam_state.getPosition()+" - setting up watchdogs and monitors for 'no beam mode'")
        noBeamMode(True) 

    # Temporarily disable topup watchdog (for Excalibur experiment)
    print("Disabling topup watchdog")
    topup_watchdog.setEnabled(False)

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
    detectorPreparer = I18DetectorPreparer(sensitivities, sensitivity_units, counterTimer01, raster_counterTimer01) # @UndefinedVariable
    detectorPreparer.addQexafsDetectors("Xspress3Odin", [qexafs_counterTimer01, qexafs_xspress3Odin, qexafs_FFI0_xspress3Odin])
        
    global beamlinePreparer
    global samplePreparer
    global outputPreparer
    samplePreparer   = I18SamplePreparer() # @UndefinedVariable
    outputPreparer   = I18OutputPreparer(datawriterconfig, Finder.find("metashop"))
    beamlinePreparer = I18BeamlinePreparer(topupMonitor, beamMonitor, detectorFillingMonitor, energy, energy_nogap, auto_mDeg_idGap_mm_converter) # @UndefinedVariable
    
    global energy_scannable_for_scans
    if live_mode and beam_available() :
        energy_scannable_for_scans = energy # @UndefinedVariable
    else:
        energy_scannable_for_scans = energy_nogap # @UndefinedVariable
    set_energy_output_format()
    
    # simulation
    if not live_mode:
        energy(7000) # @UndefinedVariable
        energy_nogap(7000) # @UndefinedVariable
    
    setup_factories()
    setup_aliases()
    set_energy_scannable(energy_scannable_for_scans)
    excalibur_metadata = DiffractionAppenderManager("excalibur_calibration_appender", "excalibur_mask_appender")

    #  Make the spectrometer setup functions available
    run_script("spectrometer-setup.py")
    if XESEnergyJohann is not None :
        if LocalProperties.isDummyModeEnabled() :
            setup_dummy_spectrometer(XESEnergyJohann)
        set_initial_crystal_values(XESEnergyJohann)
    
    run_script("tfgSetup.py")
    
    tfg=TFG()
    
    run_script("sleep_scannable.py")
    
    # Setup xspress3 Odin live mode
    if not LocalProperties.isDummyModeEnabled() : 
        qexafs_xspress3Odin.setUseSwmrFileReading(True)

    run_script("detector_setup.py")
   
    run_script("convert_to_Si333.py")
    
    print("\n...initialisation complete!")
    print_useful_info()

print "Reconnect daserver command : reconnect_daserver() "
def reconnect_daserver() :
    daServer = counterTimer01.getScaler().getDaServer()
    print "Trying to reconnect to DAServer..."
    daServer.reconnect()
    counterTimer01.configure()
    print "Ignore this error (it's 'normal'...)"
    counterTimer01.getScaler().clear()

from gda.data.metadata import GDAMetadataProvider
def set_subdirectory(subdir=None):
    metadata=GDAMetadataProvider.getInstance()
    if subdir is None : 
        subdir = ""
    print("Setting data subdirectory to : {}".format(subdir))
    metadata.setMetadataValue("subdirectory", subdir)


def pwd():
    return InterfaceProvider.getPathConstructor().createFromDefaultProperty()

def reload_lookup_tables() :
    print("Reloading lookup tables : ")
    lut_objects = Finder.getFindablesOfType(gda.util.converters.LookupTableConverterHolder)
    for conv_name, converter in lut_objects.items() :
        print("\t"+conv_name)
        converter.reloadConverter()

def update_t1theta_lut(newpath) :
    print("Updating path to t1theta lookup table : "+newpath)
    t1theta_ev_deg_converter = t1theta_energy_conv.getConvertor()
    t1theta_ev_deg_converter.setColumnDataFileName(newpath)
    t1theta_ev_deg_converter.reloadConverter()
    
setup()
