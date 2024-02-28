# localStation.py
# For beamline specific initialisation code.
#
print "===================================================================";
print "Performing beamline specific initialisation code (i05-1).";
print

print "Importing generic features...";
import java
from gda.configuration.properties import LocalProperties
from gda.device.scannable.scannablegroup import ScannableGroup
from time import sleep, localtime
from gda.jython.commands.GeneralCommands import alias
from gdascripts.pd.time_pds import actualTimeClass
from dirFileCommands import pwd, lwf, nwf, nfn
from gda.factory import Finder

# Get the location of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.config") + "/scripts/"
gdascripts = LocalProperties.get("gda.install.git.loc") + "/gda-core.git/uk.ac.gda.core/scripts/gdascripts/"

print "Installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()

execfile(gdascripts + "/pd/epics_pds.py");
execfile(gdascripts + "/pd/dummy_pds.py");
execfile(gdascripts + "/pd/time_pds.py");

execfile(gdascripts + "/utils.py");

print "Loading Secondary Scannable Group Creator Script... "
print "Usage: scan_creator = ScanCreator(start, stop, step, input_list)"
print "scan_creator.create_group_and_tuples()"
execfile(gdaScriptDir + "scan_creator.py")
print "-" *20

print "Creating beamline specific devices...";

import metadatatweaks
getSubdirectory = metadatatweaks.getSubdirectory
alias("getSubdirectory")
setSubdirectory = metadatatweaks.setSubdirectory
alias("setSubdirectory")
getVisit = metadatatweaks.getVisit
alias("getVisit")
setVisit = metadatatweaks.setVisit
alias("setVisit")
sample_name = metadatatweaks.SampleNameScannable("sample_name", "samplename")

centre_energy = analyser.getCentreEnergyScannable()
centre_energy.setName("centre_energy")
centre_energy.setInputNames(["centre_energy"])

# Add the MCP ROI to the global namespace, must match the name in spring.
mcp_roi = Finder.find('mcp_roi')

import arpes

# Sample stage script for easy and safe movement of the stage to predefined positions
run "beamline/sampleStage.py"

print "Installing archiver client"
from gdascripts.archiver.archiver import archive
alias('archive')
archiver = Finder.find("archiver")

print "Adding ring_current as a default_scannable"
add_default(ring_current)

from plottings.configScanPlot import setYFieldVisibleInScanPlot,getYFieldVisibleInScanPlot,setXFieldInScanPlot,useSeparateYAxes,useSingleYAxis, getXFieldInScanPlot  # @UnusedImport
setXFieldInScanPlot(0)

from i05Shared.checkBeamlineHealth import *
checkForBeamlineProblems()

run "beamline/resolutionEstimator.py"

if LocalProperties.get("gda.mode") == "live":  # don't execute in squish tests
    # Run the beamline staff scripts
    print "==================================================================="
    print "Running i05-1 scripts."
    run "beamline/masterj.py"
    print "==================================================================="
