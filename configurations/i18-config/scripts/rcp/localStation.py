#localStation.py
#For beamline specific initialisation code.
#
print "===================================================================";
print "Performing beamline specific initialisation code (i18). using localStation_rcp"
print
import sys

import java
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable

# Get the locatation of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.jython.gdaScriptDir")
gdaScriptDir  = gdaScriptDir + "/"
# Get the location of the USERS script directory
userScriptDir = LocalProperties.get("gda.jython.userScriptDir")
userScriptDir  = userScriptDir + "/"

gdaRoot = LocalProperties.get("gda.root")
gdaMicroFocus = gdaRoot+ "/uk.ac.gda.client.microfocus/"
print gdaMicroFocus +  "scripts/"
sys.path.append(gdaMicroFocus +  "scripts/")
print "setting up mapscan"
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
execfile(gdaScriptDir + "i18_scans.py")

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

# to act as the energy during dev
print "creating scannable 'test' which will be used to represent energy during commissionning"
print ""
test = DummyScannable("test")
print "===================================================================";
print

