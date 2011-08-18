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

# Get the locatation of the GDA beamline script directory
gdaRoot = LocalProperties.get("gda.root")
gdaScriptDir = gdaRoot +"/uk.ac.gda.core/scripts/gdascripts"
gdaScriptDir  = gdaScriptDir + "/"
# Get the location of the USERS script directory
userScriptDir = LocalProperties.get("gda.jython.userScriptDir")
userScriptDir  = userScriptDir + "/"

gdaMicroFocus = gdaRoot+ "/uk.ac.gda.client.microfocus/"
print gdaMicroFocus +  "scripts/"
sys.path.append(gdaMicroFocus +  "scripts/")
print "setting up mapscan"
execfile (gdaRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/rastermap.py")
execfile (gdaRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/map.py")
execfile(gdaRoot+ "/uk.ac.gda.client.microfocus/scripts/microfocus/microfocus_elements.py")

alias("map")
print "Setting XSPRESS2 Collection mode"
xs=finder.find("xspress2system")
#xs.setReadoutMode(0)

#MicroFocusSampleX.setOutputFormat(["%.4f"])
#MicroFocusSampleY.setOutputFormat(["%.4f"])

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
from exafsscripts.exafs import xas_scans
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

print "Create topup , detector and beam monitors to pause and resume scans"
from gda.device.scannable import TopupScannable
topupMonitor = TopupScannable()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(5)
topupMonitor.setWaittime(1)
topupMonitor.setTimeout(60)
topupMonitor.configure()
#add_default topupMonitor
from gda.device.scannable import BeamMonitorWithFeedbackSwitchScannable
beam = BeamMonitorWithFeedbackSwitchScannable('FE18I-RS-ABSB-02:STA',['BL18I-OP-DCM-01:FPMTR:FFB.FBON','BL18I-OP-DCM-01:FRMTR:FFB.FBON'])
beam.setName("beam")
beam.setTimeout(7200)
beam.setWaittime(60)
beam.configure()
#add_default beamdown
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

#gdaRoot = gdaRoot + "/uk.ac.gda.core/"
#print gdaRoot
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"

#execfile(gdaConfigDir + "scripts/I18Scans/BeamMonitorClass.py")
#execfile(gdaScriptDir + "pd/scaler8512_pds.py")
##execfile(gdaScriptDir + "pd/epics_pds.py");
#execfile(gdaScriptDir + "pd/time_pds.py");
#execfile(gdaScriptDir + "utils.py");
#execfile(gdaScriptDir + "constants.py");
#execfile(gdaConfigDir + "scripts/chgDataDir.py");
#execfile(gdaConfigDir + "scripts/microscope_limits.py")
# struck ion chambers
#execfile(gdaConfigDir + "scripts/I18Scans/StruckV2F.py")

#Set up the 8512 scaler card
print "Setting up 8512 scalars...";
#execfile(gdaScriptDir + "scaler8512.py");

# KB mirror motors
#execfile("/dls_sw/i18/scripts/focus/SesoMethod/Setup_KBMotors_IDT_Mechanical.py")

##vortex xmap configuration script
#execfile(gdaConfigDir + "scripts/edxd_calibrator.py")


# to act as the energy during dev
print "creating scannable 'test' which will be used to represent energy during commissionning"
print ""
test = DummyScannable("test")
print "===================================================================";
print

