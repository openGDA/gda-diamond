from uk.ac.gda.server.exafs.scan.preparers import I18BeamlinePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18DetectorPreparer
from uk.ac.gda.server.exafs.scan.preparers import I18SamplePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18OutputPreparer
from uk.ac.gda.server.exafs.scan import XasScanFactory
from uk.ac.gda.client.microfocus.scan import MapSelector, MapFactory

from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from gda.device.scannable import TopupChecker
from gda.device.scannable import I18BeamMonitor
from gda.device.scannable import DetectorFillingMonitorScannable
from gda.factory import Finder
from stageSelector import StageSelector
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.jython.commands.ScannableCommands import add_default

print "Initialization Started";

live_mode = (LocalProperties.get("gda.mode") == 'live')

finder = Finder.getInstance()

test = DummyScannable("test")

print "Creating topup , beam, detector-filling, trajectory monitors to pause and resume scans"
topupMonitor = TopupChecker()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(2.0)
topupMonitor.setWaittime(1.0)
topupMonitor.setTimeout(600.0)
topupMonitor.setMachineModeMonitor(machineModeMonitor) # @UndefinedVariable
topupMonitor.setScannableToBeMonitored(machineTopupMonitor) # @UndefinedVariable
topupMonitor.setLevel(999) # so this is the last thing to be called before data is collected, to save time for motors to move
topupMonitor.configure()

beamMonitor = I18BeamMonitor(energy) # @UndefinedVariable
beamMonitor.setName("beamMonitor")
beamMonitor.setMachineModeMonitor(machineModeMonitor) # @UndefinedVariable
beamMonitor.configure()

detectorFillingMonitor = DetectorFillingMonitorScannable()
detectorFillingMonitor.setName("detectorFillingMonitor")
detectorFillingMonitor.setStartTime(9)
detectorFillingMonitor.setDuration(25.0)

detectorFillingMonitor.configure()

add_default(topupMonitor)
add_default(beamMonitor)
# don't add detectorFillingMonitor as a default

rcpController =                finder.find("RCPController")
XASLoggingScriptController =   finder.find("XASLoggingScriptController")
commandQueueProcessor =        finder.find("commandQueueProcessor")
ExafsScriptObserver =          finder.find("ExafsScriptObserver")
auto_mDeg_idGap_mm_converter = finder.find("auto_mDeg_idGap_mm_converter")
loggingcontroller =            finder.find("XASLoggingScriptController")
datawriterconfig =             finder.find("datawriterconfig")
if finder.find("datawriterconfig").getHeader() != None:
    original_header =              finder.find("datawriterconfig").getHeader()[:]
elementListScriptController =  finder.find("elementListScriptController")

gains = [i0_keithley_gain, it_keithley_gain] # @UndefinedVariable
detectorPreparer = I18DetectorPreparer(gains, counterTimer01, xspress2system, xspress3, raster_counterTimer01, raster_xspress, QexafsFFI0, raster_xspress3,raster_FFI0_xspress3, buffered_cid, None) # @UndefinedVariable

samplePreparer   = I18SamplePreparer(rcpController, D7A, D7B, kb_vfm_x) # @UndefinedVariable
samplePreparer.setStage1(sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z) # @UndefinedVariable
samplePreparer.setStage3(table_x, table_y, table_z) # @UndefinedVariable
samplePreparer.setStage(1)
outputPreparer   = I18OutputPreparer(datawriterconfig,Finder.getInstance().find("metashop"))
beamlinePreparer = I18BeamlinePreparer(topupMonitor, beamMonitor, detectorFillingMonitor, energy, energy_nogap, auto_mDeg_idGap_mm_converter) # @UndefinedVariable

if live_mode  and (machineModeMonitor() == 'User' or machineModeMonitor() == 'BL Startup' or machineModeMonitor() == 'Special'): # @UndefinedVariable
    energy_scannable_for_scans = energy # @UndefinedVariable
    beamlinePreparer.setUseWithGapEnergy()
else:
    energy_scannable_for_scans = energy_nogap # @UndefinedVariable
    beamlinePreparer.setUseNoGapEnergy()

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
theFactory.setDatawriterconfig(datawriterconfig);
theFactory.setEnergyScannable(energy_scannable_for_scans);
theFactory.setMetashop(finder.find("metashop"));
theFactory.setIncludeSampleNameInNexusName(True);
theFactory.setScanName("energyScan")
xas = theFactory.createEnergyScan();
xanes = xas

theFactory.setQexafsDetectorPreparer(detectorPreparer);
theFactory.setQexafsEnergyScannableForConstantVelocityScan(zebraBraggEnergy); # @UndefinedVariable
theFactory.setQexafsNXDetectorList([qexafsCounterTimer01,qexafsXspress3,qexafsXspress3FFI0]) # @UndefinedVariable
qexafs = theFactory.createQexafsConstantVelocityScan()

traj1PositionReader = finder.find("traj1PositionReader")
traj3PositionReader = finder.find("traj3PositionReader")

mapFactory = MapFactory();
mapFactory.setBeamlinePreparer(beamlinePreparer);
mapFactory.setDetectorPreparer(detectorPreparer);
mapFactory.setSamplePreparer(samplePreparer);
mapFactory.setOutputPreparer(outputPreparer);
mapFactory.setLoggingScriptController(XASLoggingScriptController);
mapFactory.setDatawriterconfig(datawriterconfig);
mapFactory.setEnergyWithGapScannable(energy); # @UndefinedVariable
mapFactory.setEnergyNoGapScannable(energy_nogap); # @UndefinedVariable
mapFactory.setMetashop(Finder.getInstance().find("metashop"));
mapFactory.setIncludeSampleNameInNexusName(True);
mapFactory.setCounterTimer(counterTimer01); # @UndefinedVariable
mapFactory.setxScan(sc_MicroFocusSampleX); # @UndefinedVariable
mapFactory.setyScan(sc_MicroFocusSampleY); # @UndefinedVariable
mapFactory.setzScan(sc_sample_z); # @UndefinedVariable
mapFactory.setElementListScriptController(elementListScriptController);
mapFactory.setRasterMapDetectorPreparer(detectorPreparer);
mapFactory.setTrajectoryMotor(traj1ContiniousX); # @UndefinedVariable # use the MapSelector object to switch to the large stage (stage 3)
mapFactory.setPositionReader(traj1PositionReader); # use the MapSelector object to switch to the large stage (stage 3)
mapFactory.setScanName("step map")

non_raster_map = mapFactory.createStepMap()
raster_map = mapFactory.createRasterMap()
faster_raster_map = mapFactory.createFasterRasterMap();

map = MapSelector(beamlinePreparer, non_raster_map, raster_map, faster_raster_map, traj1ContiniousX, traj3ContiniousX, traj1PositionReader, traj3PositionReader, raster_counterTimer01) # @UndefinedVariable @ReservedAssignment
map.setStage1X(sc_MicroFocusSampleX) # @UndefinedVariable
map.setStage1Y(sc_MicroFocusSampleY) # @UndefinedVariable
map.setStage1Z(sc_sample_z) # @UndefinedVariable
map.setStage3X(table_x) # @UndefinedVariable
map.setStage3Y(table_y) # @UndefinedVariable
map.setStage3Z(table_z) # @UndefinedVariable

map.setStage(1)

if live_mode and (machineModeMonitor() == 'User' or machineModeMonitor() == 'BL Startup' or machineModeMonitor() == 'Special'): # @UndefinedVariable
    map.enableUseIDGap()
else:
    map.disableUseIDGap()

vararg_alias("xas")
vararg_alias("xanes")
vararg_alias("qexafs")
vararg_alias("map")
vararg_alias("raster_map")
vararg_alias("raster_map_return_write")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

selectStage = StageSelector(samplePreparer,map)
alias("selectStage")
selectStage(1)

from gda.scan import EpicsTrajectoryScanController
EpicsTrajectoryScanController.setMAXIMUM_ELEMENT_NUMBER(100000)

print "Initialization Complete";

print "****************************************"
print ""
print "Useful commands:"
print ""
print "To switch to faster raster (two-way rastering):"
print " map.enableFasterRaster()"
print "and to switch back:"
print " map.disableFasterRaster()"
print ""
print "To switch to use table 3 (large stage) for rastering:"
print " selectStage(3)"
print "To switch back to table 1 (small stage) for rastering:"
print " selectStage(1)"
print ""
print "To disable/enable use of the ID Gap:"
print " map.disableUseIDGap()"
print " map.enableUseIDGap()"
print ""
print "To disable/enable output of real positions in raster maps:"
print " map.disableRealPositions()"
print " map.enableRealPositions()"
print ""
print "To change the y axis used in maps to fine theta (but could be any motor) using stage1 (for tomography measurements):"
print " map.setStage1Y(sc_sample_thetafine)"
print " map.setStage(1)"
print "****************************************"
