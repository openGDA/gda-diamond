print "===================================================================";
print "Performing beamline specific initialisation code (i18).";
print
import sys

import java
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable

gdaRoot = str(LocalProperties.get("gda.root"))
gdaMicroFocus = gdaRoot+ "/uk.ac.gda.client.microfocus/"
print gdaMicroFocus +  "scripts/"
sys.path.append(gdaMicroFocus +  "scripts/")

print "setting up mapscan"
microfocusRoot = "/dls_sw/i18/software/gda_versions/gda_822ws_git/gda-xas-core.git/"
execfile (microfocusRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/rastermap.py")
execfile (microfocusRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/vortex_rastermap.py")
execfile (microfocusRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/map.py")
execfile(microfocusRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/microfocus_elements.py")

alias("map")

gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

execfile(gdaConfigDir + "scripts/scans/DummySlaveCounterTimer.py")
execfile(gdaConfigDir + "scripts/scans/DummyExafsScanClass.py")

execfile(gdaConfigDir + "scripts/I18Scans/XspressReadScannable.py")

print "Setting XSPRESS2 Collection mode"
xs=finder.find("xspress2system")

sc_MicroFocusSampleX.setOutputFormat(["%.4f"])
sc_MicroFocusSampleY.setOutputFormat(["%.4f"])

print "setting scans"
from i18_exafs import setupExperiment
setupExperiment.rootnamespace = globals()
map.rootnamespace = globals()
rastermap.rootnamespace = globals()
rootnamespace = globals()
from exafsscripts.exafs.xas_scans import xas, xanes, estimateXas, estimateXanes, qexafs

from exafsscripts.vortex import vortexConfig
from exafsscripts.vortex.vortexConfig import vortex

from exafsscripts.xspress import xspressConfig
from exafsscripts.xspress.xspressConfig import xspress

alias("xas")
alias("xanes")
alias("estimateXas")
alias("estimateXanes")
alias("vortex")
alias("xspress")
alias("qexafs")

print "Create topup , detector and beam monitors to pause and resume scans"
from gda.device.scannable import TopupScannable
topupMonitor = TopupScannable()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(1.0)
topupMonitor.setWaittime(1)
topupMonitor.setTimeout(600)
#topupMonitor.setTopupPV("SR-CS-FILL-01:COUNTDOWN")
topupMonitor.setScannableToBeMonitored(epicsTopupMonitor)
topupMonitor.configure()
add_default topupMonitor

from gda.device.scannable import BeamMonitorWithFeedbackSwitchScannable

#beam = BeamMonitorWithFeedbackSwitchScannable('FE18I-RS-ABSB-02:STA',['BL18I-OP-DCM-01:FPMTR:FFB.FBON'],['BL18I-OP-DCM-01:FRMTR:FFB.FBON'])
beam = BeamMonitorWithFeedbackSwitchScannable('FE18I-RS-ABSB-02:STA', [''])
beam.setName("beam")
beam.setTimeout(7200)
beam.setWaittime(60)
beam.configure()

from gda.device.scannable import DetectorFillingMonitorScannable
detectorFillingMonitor = DetectorFillingMonitorScannable()
detectorFillingMonitor.setName("detectorFillingMonitor")
detectorFillingMonitor.setTimeout(7200)
detectorFillingMonitor.setStartTime(9)
detectorFillingMonitor.setDuration(25.0)
detectorFillingMonitor.configure()

from gda.device.scannable import BeamMonitorScannableForLineRepeat
trajBeamMonitor = BeamMonitorScannableForLineRepeat(beam)
trajBeamMonitor.setName("trajBeamMonitor")
trajBeamMonitor.setTolerance(5)
trajBeamMonitor.setWaittime(1)
trajBeamMonitor.setTimeout(7200)
trajBeamMonitor.configure()
trajBeamMonitor.setLevel(1)
add_default trajBeamMonitor

print "creating scannable 'test' which will be used to represent energy during commissionning"
print ""
test = DummyScannable("test")
print "===================================================================";

gdaRoot = LocalProperties.get("gda.root")
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

from gda.data.fileregistrar import IcatXMLCreator
archiver= IcatXMLCreator()
archiver.setDirectory("/dls/bl-misc/dropfiles2/icat/dropZone/i18/i18_")

execfile(gdaConfigDir + "scripts/I18Scans/BeamMonitorClass.py")
# transmission
execfile(gdaConfigDir + "scripts/I18Scans/I18TransmissionMapV2FClass.py")
execfile(gdaConfigDir + "scripts/I18Scans/I18TransmissionExafsV2F.py")
# exafs
execfile(gdaConfigDir + "scripts/I18Scans/I18ExafsScanV2FClass.py")
execfile(gdaConfigDir + "scripts/I18Scans/vortex/I18VortexExafsScanV2FClass.py")
#microfocus step
execfile(gdaConfigDir + "scripts/I18Scans/I18StepMapV2FClass.py")
#execfile(gdaConfigDir + "scripts/I18Scans/I18StepMapV2FClass_noThreads.py")
execfile(gdaConfigDir + "scripts/I18Scans/vortex/I18VortexStepMapV2FClass.py")
#microfocus continuous
execfile(gdaConfigDir + "scripts/I18Scans/I18TrajectoryScan2.py")
#vortex
execfile(gdaConfigDir + "scripts/I18Scans/vortex/vortex_dtc_params2.py")
execfile(gdaConfigDir + "scripts/I18Scans/vortex/I18VortexUtilities.py")
#xspress
execfile(gdaConfigDir + "scripts/I18Scans/read_xspress_counts.py")

from gdascripts.pd.scaler8512_pds import ScalerChannelEpicsPVClass
from gdascripts.pd.epics_pds import SingleEpicsPositionerClass
from gdascripts.pd import time_pds
from gdascripts import utils, constants
from gdascripts.utils import * 
execfile(gdaConfigDir + "scripts/chgDataDir.py");
execfile(gdaConfigDir + "scripts/microscope_limits.py")
# struck ion chambers
execfile(gdaConfigDir + "scripts/I18Scans/StruckV2F.py")

print "Setting up 8512 scalars...";
execfile(gdaConfigDir + "scripts/scaler8512.py");
# KB mirror motors
execfile("/dls_sw/i18/scripts/focus/SesoMethod/Setup_KBMotors_IDT_Mechanical.py")

##vortex xmap configuration script
execfile(gdaConfigDir + "scripts/edxd_calibrator.py")

print "Setting XSPRESS2 Collection mode"
xs=finder.find("sw_xspress2system")

#MicroFocusSampleX.setOutputFormat(["%.4f"])
#MicroFocusSampleY.setOutputFormat(["%.4f"])
#########################################################################

#########################################################################
######Other
#######################################################################
print "Loading i18 custom script controls..."
execfile(gdaConfigDir + "scripts/i18_scans.py")
print "Loading Stage Offset routines..."
execfile(gdaConfigDir + "scripts/sampleStageTilt.py")
##########################################################################


global mapRunning
mapRunning =0

#qbpm settings 
from cid_photodiode import CidPhotoDiode
cid = CidPhotoDiode('cid', 'BL18I-DI-PHDGN-08')
cid.setExtraNames(['CID_Rminusdiode', 'CID_Rplusdiode','CID_Lminusdiode', 'CID_Lplusdiode']) 
cid.setOutputFormat(['%4.10f','%4.10f','%4.10f','%4.10f'])
#cid.setIncludeRange(False) 
#cid.setOutputFormat(['%4.10f','%4.10f','%4.10f','%4.10f','%4.10f','%4.10f','%4.10f']) 

##fix for trajectory scans 
execfile(gdaConfigDir + "scripts/scans/correctTrajInterface.py"); 
raster_xspress.setInputNames([])
raster_xmap.setInputNames([])
print "===================================================================";
print