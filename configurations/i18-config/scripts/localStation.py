import sys
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from i18_exafs import setupExperiment
from exafsscripts.exafs.xas_scans import xas, xanes, qexafs
from exafsscripts.vortex import vortexConfig
from exafsscripts.vortex.vortexConfig import vortex
from exafsscripts.xspress import xspressConfig
from exafsscripts.xspress.xspressConfig import xspress
from gda.device.scannable import TopupScannable
from gda.device.scannable import BeamMonitorWithFeedbackSwitchScannable
from gda.device.scannable import DetectorFillingMonitorScannable
from gda.device.scannable import BeamMonitorScannableForLineRepeat
from gda.data.fileregistrar import IcatXMLCreator
from cid_photodiode import CidPhotoDiode
from microfocus import map, raster_map, raster_map_return_write

print "Initialization Started";

gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

execfile(gdaConfigDir + "scripts/I18Scans/XspressReadScannable.py")

print "setting scans"
setupExperiment.rootnamespace = globals()
map.rootnamespace = globals()
raster_map.rootnamespace = globals()
rootnamespace = globals()

alias("map")
alias("xas")
alias("xanes")
alias("vortex")
alias("xspress")
alias("qexafs")
alias("map")
alias("raster_map")
alias("raster_map_return_write")

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

    execfile(gdaConfigDir + "scripts/I18Scans/StruckV2F.py")
    execfile("/dls_sw/i18/scripts/focus/SesoMethod/Setup_KBMotors_IDT_Mechanical.py")


print "creating scannable 'test' which will be used to represent energy during commissionning"
print ""
test = DummyScannable("test")

gdaRoot = LocalProperties.get("gda.root")
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

execfile(gdaConfigDir + "scripts/I18Scans/BeamMonitorClass.py")
execfile(gdaConfigDir + "scripts/I18Scans/I18TransmissionMapV2FClass.py")
execfile(gdaConfigDir + "scripts/I18Scans/I18TransmissionExafsV2F.py")

execfile(gdaConfigDir + "scripts/I18Scans/I18ExafsScanV2FClass.py")

execfile(gdaConfigDir + "scripts/I18Scans/vortex/I18VortexExafsScanV2FClass.py")
execfile(gdaConfigDir + "scripts/I18Scans/I18StepMapV2FClass.py")
execfile(gdaConfigDir + "scripts/I18Scans/vortex/I18VortexStepMapV2FClass.py")
execfile(gdaConfigDir + "scripts/I18Scans/I18TrajectoryScan2.py")
execfile(gdaConfigDir + "scripts/I18Scans/vortex/vortex_dtc_params2.py")
execfile(gdaConfigDir + "scripts/I18Scans/vortex/I18VortexUtilities.py")
execfile(gdaConfigDir + "scripts/I18Scans/read_xspress_counts.py")

execfile(gdaConfigDir + "scripts/edxd_calibrator.py")

print "Loading i18 custom script controls..."
execfile(gdaConfigDir + "scripts/i18_scans.py")
print "Loading Stage Offset routines..."
execfile(gdaConfigDir + "scripts/sampleStageTilt.py")

global mapRunning
mapRunning = 0

cid = CidPhotoDiode('cid', 'BL18I-DI-PHDGN-08')
cid.setExtraNames(['CID_Rminusdiode', 'CID_Rplusdiode', 'CID_Lminusdiode', 'CID_Lplusdiode']) 
cid.setOutputFormat(['%4.10f', '%4.10f', '%4.10f', '%4.10f'])

execfile(gdaConfigDir + "scripts/scans/correctTrajInterface.py"); 
raster_xspress.setInputNames([])
raster_xmap.setInputNames([])

print "Initialization Complete";