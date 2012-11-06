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
#########################################################################
###Setting up the necessary paths
##########################################################################
# Get the locatation of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.jython.gdaScriptDir")
gdaScriptDir  = gdaScriptDir + "/"
# Get the location of the USERS script directory
userScriptDir = LocalProperties.get("gda.jython.userScriptDir")
userScriptDir  = userScriptDir + "/"
gdaRoot = LocalProperties.get("gda.root")
gdaConfigDir = LocalProperties.get("gda.config")
gdaConfigDir = gdaConfigDir + "/"
gdaDevScriptDir = LocalProperties.get("gda.jython.gdaDevScriptDir") + "/";
#########################################################################

#########################################################################
###File Archiving
#######################################################################
from gda.data.fileregistrar import IcatXMLCreator
archiver= IcatXMLCreator()
#archiver.setDirectory("/tmp/i18_")
archiver.setDirectory("/dls/bl-misc/dropfiles2/icat/dropZone/i18/i18_")
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

execfile(gdaDevScriptDir + "pd/scaler8512_pds.py")
execfile(gdaDevScriptDir + "pd/epics_pds.py");
execfile(gdaDevScriptDir + "pd/time_pds.py");
execfile(gdaDevScriptDir + "utils.py");
execfile(gdaDevScriptDir + "constants.py");
execfile(gdaScriptDir + "chgDataDir.py");
execfile(gdaConfigDir + "scripts/microscope_limits.py")
# struck ion chambers
execfile(gdaConfigDir + "scripts/I18Scans/StruckV2F.py")

print "Setting up 8512 scalars...";
execfile(gdaScriptDir + "scaler8512.py");
# KB mirror motors
execfile("/dls_sw/i18/scripts/focus/SesoMethod/Setup_KBMotors_IDT_Mechanical.py")

##vortex xmap configuration script
execfile(gdaConfigDir + "scripts/edxd_calibrator.py")

##vortex xmap configuration script
execfile(gdaConfigDir + "scripts/edxd_calibrator.py")
###############################################################################

###############################################################################
###xspress setup
#########################################################################
print "Setting XSPRESS2 Collection mode"
xs=finder.find("xspress2system")
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
counterTimer01.setOutputFormat(['%5.2g','%5.2g', '%5.2g'])
counterTimer01.setTFGv2(1)
counterTimer01.setTimeChannelRequired(0)
#########################################################################

#########################################################################
####Xmap setup
#########################################################################
xmapMca.setEventProcessingTimes([1.1029752060937018e-007, 1.1407794527246737e-007, 1.1465765791909203e-007, 1.0675602460939456e-007])
##########################################################################
###global mapRunning variable
##########################################################################
global mapRunning
mapRunning =0
print "===================================================================";
print

