#@PydevCodeAnalysisIgnore

from uk.ac.gda.server.exafs.scan.preparers import I18BeamlinePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18DetectorPreparer
from uk.ac.gda.server.exafs.scan.preparers import I18SamplePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18OutputPreparer
from uk.ac.gda.server.exafs.scan import EnergyScan, QexafsScan, XasScanFactory
from uk.ac.gda.client.microfocus.scan import StepMap, MapSelector, RasterMap, FasterRasterMap, MapFactory

from gda.configuration.properties import LocalProperties
from gda.data import PathConstructor
from gda.data.fileregistrar import IcatXMLCreator
from gda.device.monitor import DummyMonitor
from gda.device.scannable import DummyScannable
from gda.device.scannable import TopupChecker
from gda.device.scannable import I18BeamMonitor
from gda.device.scannable import DetectorFillingMonitorScannable
from gda.device.scannable import I18LineRepeatingBeamMonitor
from gda.factory import Finder
from uk.ac.gda.client.microfocus.scan.datawriter import MicroFocusWriterExtender
from cid_photodiode import CidPhotoDiode
from gdascripts.metadata.metadata_commands import meta_add,meta_ll,meta_ls,meta_rm
from gda.data.scan.datawriter import NexusDataWriter

from microfocus.microfocus_elements import getXY,plotSpectrum,displayMap
from edxd_calibrator import refinement #script refinement that is used to calibrate the vortex about once a year
from sampleStageTilt import *
from pd_setPvAndWaitForCallbackWithSeparateReadback import SetPvAndWaitForCallbackWithSeparateReadback2

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

trajBeamMonitor = I18LineRepeatingBeamMonitor(energy)
trajBeamMonitor.setName("trajBeamMonitor")
trajBeamMonitor.configure()
trajBeamMonitor.setMachineModeMonitor(machineModeMonitor)
trajBeamMonitor.setLevel(1)

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
original_header =              finder.find("datawriterconfig").getHeader()[:]
elementListScriptController =  finder.find("elementListScriptController")

gains = [i0_keithley_gain, it_keithley_gain]
detectorPreparer = I18DetectorPreparer(gains, counterTimer01, xspress2system, xmapMca, qexafs_counterTimer01, qexafs_xspress, QexafsFFI0, qexafs_xmap, buffered_cid, None)
samplePreparer   = I18SamplePreparer(rcpController, sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, D7A, D7B, kb_vfm_x)
outputPreparer   = I18OutputPreparer(datawriterconfig,Finder.getInstance().find("metashop"))

if (LocalProperties.get("gda.mode") == 'live')  and (machineModeMonitor() == 'User' or machineModeMonitor() == 'BL Startup' or machineModeMonitor() == 'Special'):
    energy_scannable_for_scans = energy
else:
    energy_scannable_for_scans = energy_nogap
    
beamlinePreparer = I18BeamlinePreparer(topupMonitor, beamMonitor, detectorFillingMonitor, energy_scannable_for_scans, auto_mDeg_idGap_mm_converter)

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
qeaxfs = theFactory.createQexafsScan()


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
mapFactory.setEnergyScannable(energy_scannable_for_scans);
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
mapFactory.setTrajectoryBeamMonitor(trajBeamMonitor);
mapFactory.setScanName("step map")


non_raster_map = mapFactory.createStepMap()
raster_map = mapFactory.createRasterMap()
faster_raster_map = mapFactory.createFasterRasterMap();

map = MapSelector(non_raster_map, raster_map, faster_raster_map, traj1ContiniousX, traj3ContiniousX, traj1PositionReader, traj3PositionReader)


if (LocalProperties.get("gda.mode") == 'live'):
    detectorPreparer.addMonitors(topupMonitor, beamMonitor, detectorFillingMonitor)
else:
    detectorPreparer.addMonitors(None, None, None)

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
print "****************************************"
