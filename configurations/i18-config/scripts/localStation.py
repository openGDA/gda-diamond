#@PydevCodeAnalysisIgnore

from uk.ac.gda.server.exafs.scan.preparers import I18BeamlinePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18DetectorPreparer
from uk.ac.gda.server.exafs.scan.preparers import I18SamplePreparer
from uk.ac.gda.server.exafs.scan.preparers import I18OutputPreparer
from uk.ac.gda.server.exafs.scan import XasScan, QexafsScan
from uk.ac.gda.client.microfocus.scan import MapScan, MapSelector

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
# from microfocus.map_select import MapSelect
# from microfocus.map import Map
# from microfocus.raster_map import RasterMap
# from microfocus.raster_map_return_write import RasterMapReturnWrite
from cid_photodiode import CidPhotoDiode
from gdascripts.metadata.metadata_commands import meta_add,meta_ll,meta_ls,meta_rm
from gda.data.scan.datawriter import NexusDataWriter

from microfocus.microfocus_elements import getXY,plotSpectrum,displayMap
from edxd_calibrator import refinement #script refinement that is used to calibrate the vortex about once a year
from sampleStageTilt import *
from pd_setPvAndWaitForCallbackWithSeparateReadback import SetPvAndWaitForCallbackWithSeparateReadback2

print "Initialization Started";

finder = Finder.getInstance()

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

gains = [i0_keithley_gain, it_keithley_gain]

detectorPreparer = I18DetectorPreparer(gains, counterTimer01, xspress2system, xmapMca, qexafs_counterTimer01, qexafs_xspress, QexafsFFI0, qexafs_xmap)
samplePreparer = I18SamplePreparer(rcpController, sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, D7A, D7B, kb_vfm_x)
outputPreparer = I18OutputPreparer(datawriterconfig,Finder.getInstance().find("metashop"))

if (LocalProperties.get("gda.mode") == 'live')  and (machineModeMonitor() == 'User' or machineModeMonitor() == 'BL Startup' or machineModeMonitor() == 'Special'):
    energy_scannable_for_scans = energy
else:
    energy_scannable_for_scans = energy_nogap
    topupMonitor = None
    beamMonitor = None
    detectorFillingMonitor = None
    trajBeamMonitor = None
beamlinePreparer = I18BeamlinePreparer(topupMonitor, beamMonitor, detectorFillingMonitor, trajBeamMonitor, energy_scannable_for_scans, auto_mDeg_idGap_mm_converter)
xas = XasScan(beamlinePreparer, detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, XASLoggingScriptController, datawriterconfig, original_header, energy_scannable_for_scans, Finder.getInstance().find("metashop"), True)
non_raster_map = MapScan(beamlinePreparer, detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, XASLoggingScriptController, datawriterconfig, original_header, energy_scannable_for_scans, Finder.getInstance().find("metashop"), True, counterTimer01, sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z)
xanes = xas
qexafs = QexafsScan(beamlinePreparer, detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, XASLoggingScriptController, datawriterconfig, original_header, qexafs_energy, Finder.getInstance().find("metashop"), True)


# if (LocalProperties.get("gda.mode") == 'live'):
#     non_raster_map =                           Map(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, sc_MicroFocusSampleX, sc_MicroFocusSampleY)
#     raster_map =                         RasterMap(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, traj1ContiniousX, traj3ContiniousX, raster_counterTimer01, raster_xmap, traj1PositionReader, traj3PositionReader, raster_xspress, buffered_cid, trajBeamMonitor)
#     raster_map_return_write = RasterMapReturnWrite(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, raster_xmap, traj1tfg, traj1xmap,traj3tfg, traj3xmap, traj1SampleX, traj3SampleX, raster_xspress, traj1PositionReader, traj3PositionReader, trajBeamMonitor)
# else:
#     non_raster_map =                           Map(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, sc_MicroFocusSampleX, sc_MicroFocusSampleY)
#     raster_map =                         RasterMap(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, traj1ContiniousX, traj3ContiniousX, raster_counterTimer01, raster_xmap, None, None, raster_xspress, None, None)
#     raster_map_return_write = RasterMapReturnWrite(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, raster_xmap, traj1tfg, traj1xmap,traj3tfg, traj3xmap, traj1SampleX, traj3SampleX, raster_xspress, None, None, None)
    

# give object references to energy and table motors, now do not need the finder or to edit XML
# non_raster_map.setEnergyScannables(energy,energy_nogap)
# non_raster_map.setStageScannables(sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, table_x, table_y, table_z)
# raster_map.setEnergyScannables(energy,energy_nogap)
# raster_map.setStageScannables(sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, table_x, table_y, table_z)
# raster_map_return_write.setEnergyScannables(energy,energy_nogap)
# raster_map_return_write.setStageScannables(sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, table_x, table_y, table_z)
# samplePreparer.setStageScannables(sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, table_x, table_y, table_z)


# map = MapSelect(non_raster_map, raster_map, raster_map_return_write, samplePreparer)
# 
# non_raster_map = Map(beamlinePreparer, detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, XASLoggingScriptController, datawriterconfig, original_header, energy, True, Finder.getInstance().find("metashop"), counterTimer01, sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z)


#non_raster_map = Map(beamlinePreparer, detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, XASLoggingScriptController, datawriterconfig, original_header, energy, True, Finder.getInstance().find("metashop"), counterTimer01, sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z)

# # while traj stage 3 hardware is switched off
# raster_map =                         RasterMap(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, traj1ContiniousX, traj3ContiniousX, raster_counterTimer01, raster_xmap, traj1PositionReader, traj3PositionReader, raster_xspress, buffered_cid, trajBeamMonitor)
# raster_map_return_write = RasterMapReturnWrite(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, raster_xmap, traj1tfg, traj1xmap,traj3tfg, traj3xmap, traj1SampleX, traj3SampleX, raster_xspress, traj1PositionReader, traj3PositionReader, trajBeamMonitor)
# raster_map =                         RasterMap(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, traj1ContiniousX, None, raster_counterTimer01, raster_xmap, traj1PositionReader, None, raster_xspress, buffered_cid)
# raster_map_return_write = RasterMapReturnWrite(xspressConfig, vortexConfig, D7A, D7B, counterTimer01, rcpController, ExafsScriptObserver, outputPreparer, detectorPreparer, raster_xmap, traj1tfg, traj1xmap,None, None, traj1SampleX, None, raster_xspress, traj1PositionReader, None)

# map = MapSelect(non_raster_map, raster_map, raster_map_return_write)
map = MapSelector(non_raster_map, None, None)

if (LocalProperties.get("gda.mode") == 'live'):
    detectorPreparer.addMonitors(topupMonitor, beamMonitor, detectorFillingMonitor)
else:
    detectorPreparer.addMonitors(None, None, None)

vararg_alias("xas")
vararg_alias("xanes")
vararg_alias("qexafs")
vararg_alias("map")
# alias("raster_map")
# alias("raster_map_return_write")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

test = DummyScannable("test")

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
