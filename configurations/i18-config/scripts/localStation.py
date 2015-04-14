from uk.ac.gda.server.exafs.scan.preparers import I18BeamlinePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18DetectorPreparer
from uk.ac.gda.server.exafs.scan.preparers import I18SamplePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18OutputPreparer
from uk.ac.gda.server.exafs.scan import EnergyScan, QexafsScan, XasScanFactory
from uk.ac.gda.client.microfocus.scan import StepMap, MapSelector, RasterMap, FasterRasterMap, MapFactory

from gda.configuration.properties import LocalProperties
#from gda.data import PathConstructor
#from gda.data.fileregistrar import IcatXMLCreator
from gda.device.monitor import DummyMonitor
from gda.device.scannable import DummyScannable
from gda.device.scannable import TopupChecker
from gda.device.scannable import I18BeamMonitor
from gda.device.scannable import DetectorFillingMonitorScannable
from gda.factory import Finder
#from uk.ac.gda.client.microfocus.scan.datawriter import MicroFocusWriterExtender
#from cid_photodiode import CidPhotoDiode
from gdascripts.metadata.metadata_commands import meta_add,meta_ll,meta_ls,meta_rm
#from gda.data.scan.datawriter import NexusDataWriter

#from microfocus.microfocus_elements import getXY,plotSpectrum,displayMap
#from edxd_calibrator import refinement #script refinement that is used to calibrate the vortex about once a year
#from sampleStageTilt import *
#from pd_setPvAndWaitForCallbackWithSeparateReadback import SetPvAndWaitForCallbackWithSeparateReadback2

print "Initialization Started";

finder = Finder.getInstance()

test = DummyScannable("test")


# if (LocalProperties.get("gda.mode") == 'live'):
print "Create topup , beam, detector-filling, trajectory monitors to pause and resume scans"
topupMonitor = TopupChecker()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(1.0)
topupMonitor.setWaittime(1)
topupMonitor.setTimeout(600)
topupMonitor.setMachineModeMonitor(machineModeMonitor)
topupMonitor.setScannableToBeMonitored(machineTopupMonitor)
topupMonitor.setLevel(999) # so this is the last thing to be called before data is collected, to save time for motors to move
topupMonitor.configure()

beamMonitor = I18BeamMonitor(energy)
beamMonitor.setName("beamMonitor")
beamMonitor.setMachineModeMonitor(machineModeMonitor)
beamMonitor.configure()
# traj1ContiniousX.setBeamMonitor(beamMonitor) # this will test the beam state just before a traj map move
# traj1ContiniousX.setTopupMonitor(topupMonitor) # this will test the beam state just before a traj map move
# traj3ContiniousX.setBeamMonitor(beamMonitor)
# traj3ContiniousX.setTopupMonitor(topupMonitor)

detectorFillingMonitor = DetectorFillingMonitorScannable()
detectorFillingMonitor.setName("detectorFillingMonitor")
detectorFillingMonitor.setStartTime(9)
detectorFillingMonitor.setDuration(25.0)
detectorFillingMonitor.configure()

add_default topupMonitor
add_default beamMonitor

#     archiver = IcatXMLCreator()
#     archiver.setDirectory("/dls/bl-misc/dropfiles2/icat/dropZone/i18/i18_")

# else:
#     traj1xmap = finder.find("traj1xmap")
#     traj3xmap = finder.find("traj3xmap")
#     
#     topupMonitor = DummyMonitor()
#     topupMonitor.setName("topupMonitor")
#     beamMonitor = DummyMonitor()
#     beamMonitor.setName("beamMonitor")
#     detectorFillingMonitor = DummyMonitor()
#     detectorFillingMonitor.setName("detectorFillingMonitor")
#     trajBeamMonitor = DummyMonitor()
#     trajBeamMonitor.setName("trajBeamMonitor")


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

gains = [i0_keithley_gain, it_keithley_gain]
detectorPreparer = I18DetectorPreparer(gains, counterTimer01, xspress2system, xspress3, raster_counterTimer01, raster_xspress, QexafsFFI0, raster_xspress3,raster_FFI0_xspress3, buffered_cid, None)
samplePreparer   = I18SamplePreparer(rcpController, sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, D7A, D7B, kb_vfm_x)
outputPreparer   = I18OutputPreparer(datawriterconfig,Finder.getInstance().find("metashop"))
beamlinePreparer = I18BeamlinePreparer(topupMonitor, beamMonitor, detectorFillingMonitor, energy, energy_nogap, auto_mDeg_idGap_mm_converter)

if (LocalProperties.get("gda.mode") == 'live')  and (machineModeMonitor() == 'User' or machineModeMonitor() == 'BL Startup' or machineModeMonitor() == 'Special'):
    energy_scannable_for_scans = energy
    beamlinePreparer.setUseWithGapEnergy()
else:
    energy_scannable_for_scans = energy_nogap
    beamlinePreparer.setUseNoGapEnergy()
    
# while testing in low-alpha only
energy_scannable_for_scans = energy_nogap
    
# simulation
if (LocalProperties.get("gda.mode") == 'dummy'):
    energy(7000)
    energy_nogap(7000)
    

theFactory = XasScanFactory();
theFactory.setBeamlinePreparer(beamlinePreparer);
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setDatawriterconfig(datawriterconfig);
theFactory.setEnergyScannable(energy_scannable_for_scans);
theFactory.setMetashop(Finder.getInstance().find("metashop"));
theFactory.setIncludeSampleNameInNexusName(True);
theFactory.setQexafsDetectorPreparer(detectorPreparer);
theFactory.setQexafsEnergyScannable(qexafs_energy);
theFactory.setScanName("energyScan")

xas = theFactory.createEnergyScan();
xanes = xas
qexafs = theFactory.createQexafsScan()


if (LocalProperties.get("gda.mode") != 'live'):
    traj1PositionReader = None
    traj3PositionReader = None

mapFactory = MapFactory();
mapFactory.setBeamlinePreparer(beamlinePreparer);
mapFactory.setDetectorPreparer(detectorPreparer);
mapFactory.setSamplePreparer(samplePreparer);
mapFactory.setOutputPreparer(outputPreparer);
mapFactory.setLoggingScriptController(XASLoggingScriptController);
mapFactory.setDatawriterconfig(datawriterconfig);
mapFactory.setEnergyWithGapScannable(energy);
mapFactory.setEnergyNoGapScannable(energy_nogap);
mapFactory.setMetashop(Finder.getInstance().find("metashop"));
mapFactory.setIncludeSampleNameInNexusName(True);
mapFactory.setCounterTimer(counterTimer01);
mapFactory.setxScan(sc_MicroFocusSampleX);
mapFactory.setyScan(sc_MicroFocusSampleY);
mapFactory.setzScan(sc_sample_z);
mapFactory.setElementListScriptController(elementListScriptController);
mapFactory.setRasterMapDetectorPreparer(detectorPreparer);
mapFactory.setTrajectoryMotor(traj1ContiniousX); # use the MapSelector object to switch to the large stage (stage 3)
mapFactory.setPositionReader(finder.find("traj1PositionReader")); # use the MapSelector object to switch to the large stage (stage 3)
mapFactory.setScanName("step map")


non_raster_map = mapFactory.createStepMap()
raster_map = mapFactory.createRasterMap()
faster_raster_map = mapFactory.createFasterRasterMap();

map = MapSelector(beamlinePreparer, non_raster_map, raster_map, faster_raster_map, traj1ContiniousX, traj3ContiniousX, traj1PositionReader, traj3PositionReader, raster_counterTimer01)
map.setStage1X(sc_MicroFocusSampleX)
map.setStage1Y(sc_MicroFocusSampleY)
map.setStage1Z(sc_sample_z)
map.setStage3X(table_x)
map.setStage3Y(table_y)
map.setStage3Z(table_z)

map.setStage(1)

if (LocalProperties.get("gda.mode") == 'live')  and (machineModeMonitor() == 'User' or machineModeMonitor() == 'BL Startup' or machineModeMonitor() == 'Special'):
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


if (LocalProperties.get("gda.mode") == 'live'):
    photonccd.setOutputFolderRoot("x:/data/2014/sp9943-1/xrd/")

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
print " map.setStage(3)"
print "To switch back to table 1 (small stage) for rastering:"
print " map.setStage(1)"
print ""
print "To disable/enable use of the ID Gap:"
print " map.disableUseIDGap()"
print " map.enableUseIDGap()"
print ""
print "To disable/enable output of real positions in raster maps:"
print " map.disableRealPositions()"
print " map.enableRealPositions()"
print ""
print "To change the y axis used in maps to fine theta (but could be any motor):"
print " non_raster_map.stage1_y = sc_sample_thetafine"
print " raster_map.stage1_y = sc_sample_thetafine"
print " raster_map_return_write.stage1_y = sc_sample_thetafine"
print " map.setStage(1)"
print "****************************************"


from gda.scan import EpicsTrajectoryScanController
EpicsTrajectoryScanController.setMAXIMUM_ELEMENT_NUMBER(2000)
