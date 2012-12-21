from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from exafsscripts.vortex.vortexConfig import vortex
from exafsscripts.xspress.xspressConfig import xspress
from gda.device.scannable import TopupScannable
from gda.device.scannable import BeamMonitorWithFeedbackSwitchScannable
from gda.device.scannable import DetectorFillingMonitorScannable
from gda.device.scannable import BeamMonitorScannableForLineRepeat
from gda.data.fileregistrar import IcatXMLCreator
from cid_photodiode import CidPhotoDiode

from microfocus.map_select import MapSelect
from microfocus.map import Map
from microfocus.raster_map import RasterMap
from microfocus.raster_map_return_write import RasterMapReturnWrite

from gda.factory import Finder
from exafsscripts.exafs.i18_detector_preparer import I18DetectorPreparer
from exafsscripts.exafs.i18_sample_preparer import I18SamplePreparer
from exafsscripts.exafs.output_preparer import OutputPreparer
from exafsscripts.exafs.i18ScanScripts import I18XasScan
from exafsscripts.exafs.qexafs_scan import QexafsScan
from gda.data import PathConstructor

from microfocus.microfocus_elements import getXY,plotSpectrum,displayMap

from uk.ac.gda.client.microfocus.scan.datawriter import MicroFocusWriterExtender

print "Initialization Started";

finder = Finder.getInstance()

gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"


xmldir = PathConstructor.createFromDefaultProperty() + "/xml/"

non_raster_map = Map(D7A, D7B, counterTimer01, xmldir)
raster_map = RasterMap(D7A, D7B, counterTimer01, trajectoryX, raster_counterTimer01, raster_xmap, realX, xmldir, raster_xspress)
raster_map_return_write = RasterMapReturnWrite(D7A, D7B, counterTimer01, trajectoryX, raster_counterTimer01, raster_xmap, realX, HTScaler, HTXmapMca, xmldir)


# switch between raster_map and raster_map_return_write
map = MapSelect(non_raster_map, raster_map, xmldir)

if (LocalProperties.get("gda.mode") == 'live'):
    print "Create topup , detector and beam monitors to pause and resume scans"
    topupMonitor = TopupScannable()
    topupMonitor.setName("topupMonitor")
    topupMonitor.setTolerance(1.0)
    topupMonitor.setWaittime(1)
    topupMonitor.setTimeout(600)
    #topupMonitor.setTopupPV("SR-CS-FILL-01:COUNTDOWN")
    topupMonitor.setScannableToBeMonitored(epicsTopupMonitor)
    topupMonitor.configure()

    #beam = BeamMonitorWithFeedbackSwitchScannable('FE18I-RS-ABSB-02:STA',['BL18I-OP-DCM-01:FPMTR:FFB.FBON'],['BL18I-OP-DCM-01:FRMTR:FFB.FBON'])
    beam = BeamMonitorWithFeedbackSwitchScannable('FE18I-RS-ABSB-02:STA', [''])
    beam.setName("beam")
    beam.setTimeout(7200)
    beam.setWaittime(60)
    beam.configure()

    detectorFillingMonitor = DetectorFillingMonitorScannable()
    detectorFillingMonitor.setName("detectorFillingMonitor")
    detectorFillingMonitor.setTimeout(7200)
    detectorFillingMonitor.setStartTime(9)
    detectorFillingMonitor.setDuration(25.0)
    detectorFillingMonitor.configure()

    trajBeamMonitor = BeamMonitorScannableForLineRepeat(beam)
    trajBeamMonitor.setName("trajBeamMonitor")
    trajBeamMonitor.setTolerance(5)
    trajBeamMonitor.setWaittime(1)
    trajBeamMonitor.setTimeout(7200)
    trajBeamMonitor.configure()
    trajBeamMonitor.setLevel(1)

    add_default topupMonitor
    add_default trajBeamMonitor

    archiver = IcatXMLCreator()
    archiver.setDirectory("/dls/bl-misc/dropfiles2/icat/dropZone/i18/i18_")

detectorPreparer = I18DetectorPreparer()
rcpController = finder.find("RCPController")
samplePreparer = I18SamplePreparer(rcpController, sc_MicroFocusSampleX, sc_MicroFocusSampleY, sc_sample_z, D7A, D7B)
outputPreparer = OutputPreparer()

loggingcontroller = Finder.getInstance().find("XASLoggingScriptController")

xas = I18XasScan(loggingcontroller,detectorPreparer, samplePreparer, outputPreparer, None)
if (LocalProperties.get("gda.mode") == 'live'):
    xas.addMonitors(topupMonitor, beam, detectorFillingMonitor, trajBeamMonitor)
else:
    xas.addMonitors(None, None, None, None)

qexafs = QexafsScan(loggingcontroller,detectorPreparer, samplePreparer, outputPreparer, qexafs_energy, qexafs_counterTimer01)
xanes = xas

alias("xas")
alias("xanes")
alias("vortex")
alias("xspress")
alias("qexafs")
alias("map")
alias("raster_map")
alias("raster_map_return_write")

test = DummyScannable("test")

gdaRoot = LocalProperties.get("gda.root")
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

global mapRunning
mapRunning = 0

cid = CidPhotoDiode('cid', 'BL18I-DI-PHDGN-08')
cid.setExtraNames(['CID_Rminusdiode', 'CID_Rplusdiode', 'CID_Lminusdiode', 'CID_Lplusdiode']) 
cid.setOutputFormat(['%4.10f', '%4.10f', '%4.10f', '%4.10f'])

raster_xspress.setInputNames([])
raster_xmap.setInputNames([])

print "Initialization Complete";