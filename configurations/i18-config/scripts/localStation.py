#@PydevCodeAnalysisIgnore
from gda.configuration.properties import LocalProperties
from gda.data import PathConstructor
from gda.data.fileregistrar import IcatXMLCreator
from gda.device.monitor import DummyMonitor
from gda.device.scannable import DummyScannable
from gda.device.scannable import TopupChecker
from gda.device.scannable import I18BeamMonitor
from gda.device.scannable import DetectorFillingMonitorScannable
from gda.device.scannable import LineRepeatingBeamMonitor
from gda.factory import Finder
from uk.ac.gda.client.microfocus.scan.datawriter import MicroFocusWriterExtender
from microfocus.map_select import MapSelect
from microfocus.map import Map
from microfocus.raster_map import RasterMap
from microfocus.raster_map_return_write import RasterMapReturnWrite
from cid_photodiode import CidPhotoDiode
from exafsscripts.exafs.i18DetectorPreparer import I18DetectorPreparer
from exafsscripts.exafs.i18SamplePreparer import I18SamplePreparer
from exafsscripts.exafs.i18OutputPreparer import I18OutputPreparer
from exafsscripts.exafs.xas_scan import XasScan
from exafsscripts.exafs.qexafs_scan import QexafsScan
from exafsscripts.exafs.config_fluoresence_detectors import XspressConfig, VortexConfig, Xspress3Config
from gdascripts.metadata.metadata_commands import meta_add,meta_ll,meta_ls,meta_rm
from gda.data.scan.datawriter import NexusDataWriter

from microfocus.microfocus_elements import getXY,plotSpectrum,displayMap
from edxd_calibrator import refinement #script refinement that is used to calibrate the vortex about once a year
from sampleStageTilt import *
from pd_setPvAndWaitForCallbackWithSeparateReadback import SetPvAndWaitForCallbackWithSeparateReadback2

print "Initialization Started";

finder = Finder.getInstance()

test = DummyScannable("test")


if (LocalProperties.get("gda.mode") == 'live'):
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
    traj1ContiniousX.setBeamMonitor(beamMonitor) # this will test the beam state just before a traj map move
    traj1ContiniousX.setTopupMonitor(topupMonitor) # this will test the beam state just before a traj map move
    traj3ContiniousX.setBeamMonitor(beamMonitor)
    traj3ContiniousX.setTopupMonitor(topupMonitor)
    
    detectorFillingMonitor = DetectorFillingMonitorScannable()
    detectorFillingMonitor.setName("detectorFillingMonitor")
    detectorFillingMonitor.setStartTime(9)
    detectorFillingMonitor.setDuration(25.0)
    detectorFillingMonitor.configure()

    trajBeamMonitor = LineRepeatingBeamMonitor(beamMonitor)
    trajBeamMonitor.setName("trajBeamMonitor")
    trajBeamMonitor.configure()
    trajBeamMonitor.setMachineModeMonitor(machineModeMonitor)
    trajBeamMonitor.setLevel(1)
    
    add_default topupMonitor
    add_default beamMonitor
    #add_default trajBeamMonitor
    # don't add detectorFillingMonitor as a default

    archiver = IcatXMLCreator()
    archiver.setDirectory("/dls/bl-misc/dropfiles2/icat/dropZone/i18/i18_")

else:
    traj1xmap = finder.find("traj1xmap")
    traj3xmap = finder.find("traj3xmap")

rcpController =                finder.find("RCPController")
XASLoggingScriptController =   finder.find("XASLoggingScriptController")
commandQueueProcessor =        finder.find("commandQueueProcessor")
ExafsScriptObserver =          finder.find("ExafsScriptObserver")
auto_mDeg_idGap_mm_converter = finder.find("auto_mDeg_idGap_mm_converter")
loggingcontroller =            finder.find("XASLoggingScriptController")
datawriterconfig =             finder.find("datawriterconfig")
original_header =              finder.find("datawriterconfig").getHeader()[:]

xspressConfig = XspressConfig(xspress2system, ExafsScriptObserver)
# vortexConfig =  VortexConfig(xmapMca, ExafsScriptObserver)
vortexConfig =  VortexConfig(None, ExafsScriptObserver)
xspress3Config = Xspress3Config(xspress3, ExafsScriptObserver)

detectorPreparer = I18DetectorPreparer(xspressConfig, vortexConfig, xspress3Config, I0_keithley, It_keithley, cmos_for_maps)
samplePreparer =   I18SamplePreparer(rcpController, D7A, D7B, kb_vfm_x)
outputPreparer =   I18OutputPreparer(datawriterconfig)


# user mode on the live beamline, use energy
if (LocalProperties.get("gda.mode") == 'live')  and (machineModeMonitor() == 'User' or machineModeMonitor() == 'BL Startup' or machineModeMonitor() == 'Special'):
    xas = XasScan(detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, ExafsScriptObserver, XASLoggingScriptController, datawriterconfig, original_header, energy, counterTimer01, False, False, auto_mDeg_idGap_mm_converter)
# else use energy_nogap
else :
     xas = XasScan(detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, ExafsScriptObserver, XASLoggingScriptController, datawriterconfig, original_header, energy_nogap, counterTimer01, False, False, auto_mDeg_idGap_mm_converter)

if (LocalProperties.get("gda.mode") == 'live'):
    non_raster_map =                           Map(xspressConfig, vortexConfig, D7A, D7B, kb_vfm_x, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, sc_MicroFocusSampleX, sc_MicroFocusSampleY)
    raster_map =                         RasterMap(xspressConfig, vortexConfig, D7A, D7B, kb_vfm_x, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, traj1ContiniousX, traj3ContiniousX, raster_counterTimer01, None, traj1PositionReader, traj3PositionReader, raster_xspress, qexafs_xspress3, buffered_cid, trajBeamMonitor)
    raster_map_return_write = RasterMapReturnWrite(xspressConfig, vortexConfig, D7A, D7B, kb_vfm_x, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, traj_xspress3, traj1tfg, None, traj3tfg, None, traj1SampleX, traj3SampleX, traj1PositionReader, traj3PositionReader, trajBeamMonitor)
else:
    non_raster_map =                           Map(xspressConfig, vortexConfig, D7A, D7B, kb_vfm_x, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, sc_MicroFocusSampleX, sc_MicroFocusSampleY)
    raster_map =                         RasterMap(xspressConfig, vortexConfig, D7A, D7B, kb_vfm_x, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, traj1ContiniousX, traj3ContiniousX, raster_counterTimer01, None, None, None, raster_xspress, qexafs_xspress3, None, None)
    raster_map_return_write = RasterMapReturnWrite(xspressConfig, vortexConfig, D7A, D7B, kb_vfm_x, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, traj_xspress3, traj1tfg, None, traj3tfg, None, traj1SampleX, traj3SampleX, None, None, None)
    

# give object references to energy and table motors, now do not need the finder or to edit XML

non_raster_map.setEnergyScannables(energy,energy_nogap)
non_raster_map.setStageScannables(sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, table_x, table_y, table_z)
non_raster_map.setCmos(cmos_for_maps)
raster_map.setEnergyScannables(energy,energy_nogap)
raster_map.setStageScannables(sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, table_x, table_y, table_z)
raster_map.setCmos(cmos_for_maps)
raster_map_return_write.setEnergyScannables(energy,energy_nogap)
raster_map_return_write.setStageScannables(sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, table_x, table_y, table_z)
samplePreparer.setStageScannables(sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, table_x, table_y, table_z)

map = MapSelect(non_raster_map, raster_map, raster_map_return_write, samplePreparer)


if (LocalProperties.get("gda.mode") == 'live'):
    detectorPreparer.addMonitors(topupMonitor, beamMonitor, detectorFillingMonitor)
else:
    detectorPreparer.addMonitors(None, None, None)

qexafs = QexafsScan(detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, ExafsScriptObserver, XASLoggingScriptController, datawriterconfig, original_header, qexafs_energy, qexafs_counterTimer01)
xanes = xas


alias("xas")
alias("xanes")
alias("qexafs")
alias("map")
alias("raster_map")
alias("raster_map_return_write")
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
