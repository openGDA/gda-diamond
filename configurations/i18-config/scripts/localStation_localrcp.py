#localStation.py
#For beamline specific initialisation code.
#
print "===================================================================";
print "Performing beamline specific initialisation code (i18).";
print
import sys

import java
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
# Get the location of the gda root  directory
gdaRoot = str(LocalProperties.get("gda.root"))
gdaMicroFocus = gdaRoot+ "/uk.ac.gda.client.microfocus/"
print gdaMicroFocus +  "scripts/"
sys.path.append(gdaMicroFocus +  "scripts/")

######################################################################
##RCP map scan and trajectory map scan
######################################################################
print "setting up mapscan"
execfile (gdaRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/rastermap.py")
execfile (gdaRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/map.py")
execfile(gdaRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/microfocus_elements.py")

alias("map")
#########################################################################
##Get config path
#########################################################################
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

execfile(gdaConfigDir + "scripts/scans/DummySlaveCounterTimer.py")
execfile(gdaConfigDir + "scripts/scans/DummyExafsScanClass.py")

##########################################################################
##Swing GUI xspress and Microfocus settings
##########################################################################
print "Setting XSPRESS2 Collection mode"
xs=finder.find("xspress2system")
#xs.setReadoutMode(0)

sc_MicroFocusSampleX.setOutputFormat(["%.4f"])
sc_MicroFocusSampleY.setOutputFormat(["%.4f"])

###########################################################################
##RCP exafs scan settings
###########################################################################
print "setting scans"
from exafsscripts.exafs import setupBeamline
setupBeamline.rootnamespace = globals()
from exafsscripts.exafs.xas_scans import xas, xanes, estimateXas, estimateXanes

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
# to act as the energy during dev
################################################################################
##default monitors
################################################################################
print "Create topup , detector and beam monitors to pause and resume scans"
from gda.device.scannable import TopupScannable
topupMonitor = TopupScannable()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(1.0)
topupMonitor.setWaittime(1)
topupMonitor.setTimeout(60)
topupMonitor.setTopupPV("SR-CS-FILL-01:COUNTDOWN")
topupMonitor.configure()
add_default topupMonitor
from gda.device.scannable import BeamMonitorWithFeedbackSwitchScannable
beam = BeamMonitorWithFeedbackSwitchScannable('FE18I-RS-ABSB-02:STA',['BL18I-OP-DCM-01:FPMTR:FFB.FBON','BL18I-OP-DCM-01:FRMTR:FFB.FBON'])
beam.setName("beam")
beam.setTimeout(7200)
beam.setWaittime(60)
beam.configure()
#add_default beam
from gda.device.scannable import DetectorFillingMonitorScannable
detectorFillingMonitor = DetectorFillingMonitorScannable()
detectorFillingMonitor.setName("detectorFillingMonitor")
detectorFillingMonitor.setTimeout(7200)
detectorFillingMonitor.setStartTime(9)
detectorFillingMonitor.setDuration(38.0)
detectorFillingMonitor.configure()
#add_default detectorFillingMonitor
from gda.device.scannable import BeamMonitorScannableForLineRepeat
trajBeamMonitor = BeamMonitorScannableForLineRepeat(beam)
trajBeamMonitor.setName("trajBeamMonitor")
trajBeamMonitor.setTolerance(5)
trajBeamMonitor.setWaittime(1)
trajBeamMonitor.setTimeout(60)
trajBeamMonitor.configure()
trajBeamMonitor.setLevel(1)
add_default trajBeamMonitor

print "creating scannable 'test' which will be used to represent energy during commissionning"
print ""
test = DummyScannable("test")
print "===================================================================";

###swing gui station script

gdaRoot = LocalProperties.get("gda.root")
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

#########################################################################
###File Archiving
#######################################################################
from gda.data.fileregistrar import IcatXMLCreator
archiver= IcatXMLCreator()
#archiver.setDirectory("/dls/bl-misc/dropfiles/icat/dropZone/i18/i18_")
archiver.setDirectory("/tmp/i18/i18_")
########################################################################

########################################################################
####Scans and other scripts
##########################################################################
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
###############################################################################

###############################################################################
###xspress setup
#########################################################################
print "Setting XSPRESS2 Collection mode"
xs=finder.find("sw_xspress2system")
#xs.setReadoutMode(0)
#########################################################################

##########################################################################
##Sample stage setup
#########################################################################
MicroFocusSampleX.setOutputFormat(["%.4f"])
MicroFocusSampleY.setOutputFormat(["%.4f"])
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
print "===================================================================";
print

