from uk.ac.gda.server.exafs.scan.preparers import I18BeamlinePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18DetectorPreparer
from uk.ac.gda.server.exafs.scan.preparers import I18SamplePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18OutputPreparer
from uk.ac.gda.server.exafs.scan import XasScanFactory
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

print("Initialisation started...\n");

live_mode = LocalProperties.get("gda.mode") == 'live'

test = DummyScannable("test")

topupMonitor = TopupChecker()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(2.0)
topupMonitor.setWaittime(1.0)
topupMonitor.setTimeout(600.0)
topupMonitor.setMachineModeMonitor(beam_state) # @UndefinedVariable
topupMonitor.setScannableToBeMonitored(topup_start_countdown_complete) # @UndefinedVariable
topupMonitor.setLevel(999) # so this is the last thing to be called before data is collected, to save time for motors to move
topupMonitor.configure()

beamMonitor = BeamMonitor()
beamMonitor.setName("beamMonitor")
beamMonitor.setShutterPVs(["FE18I-RS-ABSB-01:STA"])
beamMonitor.setMachineModeMonitor(beam_state) # @UndefinedVariable
beamMonitor.configure()

detectorFillingMonitor = DetectorFillingMonitorScannable()
detectorFillingMonitor.setName("detectorFillingMonitor")
detectorFillingMonitor.setStartTime(9)
detectorFillingMonitor.setDuration(25.0)

detectorFillingMonitor.configure()

add_default(topupMonitor)
add_default(beamMonitor)
# don't add detectorFillingMonitor as a default

# Watchdogs
from gdascripts.watchdogs.watchdogs import enableWatchdogs, disableWatchdogs, listWatchdogs, topup_watchdog, beam_available_watchdog
alias("enableWatchdogs")
alias("disableWatchdogs")
alias("listWatchdogs")
alias("topup_watchdog")
alias("beam_available_watchdog")

from gdascripts.malcolm.malcolm import reset_malcolm_after_scan

topup_watchdog.setEnabled(True)
beam_available_watchdog.setEnabled(True)

rcpController =                Finder.find("RCPController")
XASLoggingScriptController =   Finder.find("XASLoggingScriptController")
ExafsScriptObserver =          Finder.find("ExafsScriptObserver")
auto_mDeg_idGap_mm_converter = Finder.find("auto_mDeg_idGap_mm_converter_Si111")
loggingcontroller =            Finder.find("XASLoggingScriptController")
datawriterconfig =             Finder.find("datawriterconfig")
if Finder.find("datawriterconfig").getHeader() != None:
    original_header = Finder.find("datawriterconfig").getHeader()[:]
elementListScriptController = Finder.find("elementListScriptController")

sensitivities = [I0_stanford_sensitivity, It_stanford_sensitivity] # @UndefinedVariable
sensitivity_units = [I0_stanford_sensitivity_units, It_stanford_sensitivity_units] # @UndefinedVariable
detectorPreparer = I18DetectorPreparer(sensitivities, sensitivity_units, counterTimer01, xspress3, None, raster_xspress3,None) # @UndefinedVariable

samplePreparer   = I18SamplePreparer() # @UndefinedVariable
outputPreparer   = I18OutputPreparer(datawriterconfig, Finder.find("metashop"))
beamlinePreparer = I18BeamlinePreparer(topupMonitor, beamMonitor, detectorFillingMonitor, energy, energy_nogap, auto_mDeg_idGap_mm_converter) # @UndefinedVariable

if live_mode and (beam_state() == 'User' or beam_state() == 'BL Startup' or beam_state() == 'Special'): # @UndefinedVariable
    energy_scannable_for_scans = energy # @UndefinedVariable
else:
    energy_scannable_for_scans = energy_nogap # @UndefinedVariable

# simulation
if not live_mode:
    energy(7000) # @UndefinedVariable
    energy_nogap(7000) # @UndefinedVariable

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
xas = theFactory.createEnergyScan();
xanes = xas

theFactory.setQexafsDetectorPreparer(detectorPreparer);
theFactory.setQexafsEnergyScannableForConstantVelocityScan(None); # @UndefinedVariable
theFactory.setQexafsNXDetectorList([None]) # @UndefinedVariable
# qexafs = theFactory.createQexafsConstantVelocityScan()

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

vararg_alias("xas")
vararg_alias("xanes")
vararg_alias("qexafs")
vararg_alias("map")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

selectStage = StageSelector(map)
alias("selectStage")
selectStage(1)

# In order to perform AcquireRequests with Xspress3 we must initialise the plugin array:
from gdaserver import Xspress3A
from gdascripts.detectors.initialise_detector import initialise_detector
if live_mode:
    initialise_detector("Xspress3", Xspress3A.getAdBase().getBasePVName(), Xspress3A.getNdArray().getBasePVName(), "Software")
else:
    initialise_detector("Xspress3", Xspress3A.getAdBase().getBasePVName(), Xspress3A.getNdArray().getBasePVName(), "Internal", "Single")

from mapping_scan_commands import mscan, grid, detector, mstep, rect
from org.eclipse.scanning.api.points.models import AxialStepModel

def set_energy_scannable(scannable):
    global xas
    xas.setEnergyScannable(scannable)
    
set_energy_scannable(energy)

from diffraction_calibration_appender import DiffractionAppenderManager
excalibur_metadata = DiffractionAppenderManager("excalibur_calibration_appender", "excalibur_mask_appender")

print("\n...initialisation complete!")

useful_info = """
****************************************
Useful commands:

Select energy scannable for scans:
 set_energy_scannable(energy_nogap_lut) # one of energy, energy_nogap, energy_lut, energy_nogap_lut

Disable/enable all watchdogs:
 disableWatchdogs()/enableWatchdogs()

Disable/enable a single watchdog e.g. topup:
 topup_watchdog.setEnabled(False)/(True)

Specify calibration and mask files for Excalibur:
 excalibur_metadata.set_calibration_file(...)
 excalibur_metadata.set_mask_file(...)
****************************************
"""

print(useful_info)
