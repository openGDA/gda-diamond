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
from i05Shared.dirFileCommands import pwd, lwf, nwf, nfn
from gda.factory import Finder

print "Installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()


from i05Shared.scannableGroupSingleInput import ScannableGroupSingleInput
try:
	print "Configuring rawid_phase combined scannable for rawid_lowerphase and rawid_upperphase"
	rawid_phase = ScannableGroupSingleInput('rawid_phase', [rawid_lowerphase, rawid_upperphase])
	rawid_phase.configure()
	print "rawid_phase combined scannable configured"
except:
	print "rawid_phase configuration FAILED"


print "load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport
from gdascripts.pd.dummy_pds import * #@UnusedWildImport

print "load time utilities for creating timer objects."
from gdascripts.pd.time_pds import * #@UnusedWildImport

from gdascripts import utils

print "Loading Secondary Scannable Group Creator Script... "
print "Usage: scan_creator = ScanCreator(start, stop, step, input_list)"
print "scan_creator.create_group_and_tuples()"

from i05Shared.scan_creator import *
from i05Shared.pathscanTable import pathscanTable
print "-" *20

print "Creating beamline specific devices...";

from i05Shared import metadatatweaks
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
# module location is /dls_sw/ixx/scripts/
from beamline.sampleStage import *

print "Installing archiver client"
from gdascripts.archiver.archiver import archive
alias('archive')
archiver = Finder.find("archiver")

print "Adding ring_current as a default_scannable"
add_default(ring_current)

from plottings.configScanPlot import setYFieldVisibleInScanPlot,getYFieldVisibleInScanPlot,setXFieldInScanPlot,useSeparateYAxes,useSingleYAxis, getXFieldInScanPlot  # @UnusedImport
setXFieldInScanPlot(-1)

from i05Shared.checkBeamlineHealth import *
checkForBeamlineProblems()

from i05Shared.resolutionEstimator import *
estimateResolution()

print "-"*20
from gdaserver import smx, smy, smz, smdefocus
from gdascripts.scannable.sample_positions import SamplePositions
sp = SamplePositions("sp", [smx, smy, smz, smdefocus])
print("Creating sample positioner object sp. Store sample manipulator position components in a dictionary, save them to a file and move sample manipulator to previously saved positions in the dictionary.")
help(sp)

if LocalProperties.get("gda.mode") == "live":  # don't execute in squish tests
		# Run the beamline staff scripts
		print "==================================================================="
		print "Running i05-1 scripts."
		# module location is /dls_sw/ixx/scripts/
		from beamline.masterj import *
		# run "beamline/masterj.py"
		print "==================================================================="
