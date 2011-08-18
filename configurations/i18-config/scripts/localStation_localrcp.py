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
#microfocusScanWriter="Empty"
# Get the locatation of the GDA beamline script directory
gdaScriptDir = str(LocalProperties.get("gda.jython.gdaScriptDir"))
gdaScriptDir  = gdaScriptDir + "/"
# Get the location of the USERS script directory
userScriptDir = str(LocalProperties.get("gda.jython.userScriptDir"))
userScriptDir  = userScriptDir + "/"
gdaRoot = str(LocalProperties.get("gda.root"))
gdaMicroFocus = gdaRoot+ "/uk.ac.gda.client.microfocus/"
print gdaMicroFocus +  "scripts/"
sys.path.append(gdaMicroFocus +  "scripts/")
print "setting up mapscan"
execfile (gdaRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/rastermap.py")
execfile (gdaRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/map.py")
execfile(gdaRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/microfocus_elements.py")

alias("map")
#gdaRoot = gdaRoot + "/uk.ac.gda.core/"
#print gdaRoot
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

execfile(gdaConfigDir + "scripts/scans/DummySlaveCounterTimer.py")
execfile(gdaConfigDir + "scripts/scans/DummyExafsScanClass.py")

#Set up the 8512 scaler card
print "Setting up 8512 scalars...";
#execfile(gdaScriptDir + "scaler8512.py");


print "Setting XSPRESS2 Collection mode"
xs=finder.find("xspress2system")
#xs.setReadoutMode(0)

sc_MicroFocusSampleX.setOutputFormat(["%.4f"])
sc_MicroFocusSampleY.setOutputFormat(["%.4f"])

print "Loading i18 custom script controls..."
#execfile(gdaScriptDir + "i18_scans.py")

print "Loading Stage Offset routines..."
#execfile(gdaScriptDir + "sampleStageTilt.py")

#print "Loading Shutter Control"
#execfile(gdaScriptDir + "shutter.py")
#sampleShutter=ShutterClass('shutter', 'BL18I-EA-SHTR-01:CON')

print "Setting up DCM/Undulator (Lookup) motions..."
#execfile(gdaConfigDir + "scripts/dcm_undulator_lookup.py")

#comboDCM=DcmUndulatorLookupScriptClass('comboDCM')

#print "Loading Detector Utilities..."
#execfile(gdaScriptDir + "detectorUtils.py")

#ct1=finder.find("counterTimer01")
#ct2=finder.find("counterTimer02")
#tfg=finder.find("tfg")

print "setting scans"
from exafsscripts.exafs import setupBeamline
setupBeamline.rootnamespace = globals()
from exafsscripts.exafs.xas_scans import xas, xanes, estimateXas, estimateXanes

#old
#from exafsscripts.exafs import exafsScan
#from exafsscripts.exafs.exafsScan import xas, xanes, estimateXas, estimateXanes


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
# Get the locatation of the GDA beamline script directory
#gdaScriptDir = LocalProperties.get("gda.jython.gdaScriptDir")
#gdaScriptDir  = gdaScriptDir + "/"
# Get the location of the USERS script directory
#userScriptDir = LocalProperties.get("gda.jython.userScriptDir")
#userScriptDir  = userScriptDir + "/"
gdaRoot = LocalProperties.get("gda.root")
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"
#gdaDevScriptDir = LocalProperties.get("gda.jython.gdaDevScriptDir") + "/";
#gdaConfigDir=gdaRoot+"/"
#gdaDevScriptDir=""
gdaScriptDir=""
#########################################################################
###File Archiving
#######################################################################
from gda.data.fileregistrar import IcatXMLCreator
archiver= IcatXMLCreator()
archiver.setDirectory("/dls/bl-misc/dropfiles/icat/dropZone/i18/i18_")
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

from gdascripts.pd import scaler8512_pds, epics_pds, time_pds
from gdascripts import utils, constants
#execfile(gdaDevScriptDir + "pd/scaler8512_pds.py")
#execfile(gdaDevScriptDir + "pd/epics_pds.py");
#execfile(gdaDevScriptDir + "pd/time_pds.py");
#execfile(gdaDevScriptDir + "utils.py");
#execfile(gdaDevScriptDir + "constants.py");
execfile(gdaConfigDir + "scripts/chgDataDir.py");
#execfile(gdaConfigDir + "scripts/microscope_limits.py")
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
xs.setReadoutMode(0)
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
execfile(gdaScriptDir + "i18_scans.py")
print "Loading Stage Offset routines..."
execfile(gdaScriptDir + "sampleStageTilt.py")
##########################################################################

#########################################################################
###counterTimer Setup
#################################################################################
# temp fix to setup the TFG scaler output format until config in Spring
##commented ad DAServer is switched off 10/06/10
#counterTimer01.setOutputFormat(['%5.2g','%5.2g', '%5.2g'])
#counterTimer01.setTFGv2(1)
#counterTimer01.setTimeChannelRequired(0)
#########################################################################

#########################################################################
####Xmap setup
#########################################################################
#xmapMca.setEventProcessingTimes([1.1029752060937018e-007, 1.1407794527246737e-007, 1.1465765791909203e-007, 1.0675602460939456e-007])
##########################################################################
###global mapRunning variable
##########################################################################
global mapRunning
mapRunning =0
print "===================================================================";
print

