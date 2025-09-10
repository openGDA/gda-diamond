# localStation.py
# For beamline specific initialisation code.
#
print "="*100
print "Performing beamline initialisation code (i05-1).";

from i05Shared.localStation import * #@UnusedWildImport

print "-"*100
print "Creating beamline specific devices...";
print ("")

print("-"*100)
print "Installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
print("")

print("-"*100)
print(" Setting up sample_name ")
sample_name = metadatatweaks.SampleNameScannable("sample_name", "samplename")
print("")

print "-"*100
print "Adding archiver to a global namespace"
archiver = Finder.find("archiver")
print "Adding mcp_roi to global namespace";
mcp_roi = Finder.find('mcp_roi')
print ("")

print "-"*100
print "Setting up centre_energy scannable";
centre_energy = analyser.getCentreEnergyScannable()
centre_energy.setName("centre_energy")
centre_energy.setInputNames(["centre_energy"])
print("")

print "-"*100
print "Adding ring_current as a default_scannable"
add_default(ring_current)
print("")

print "-"*100
print "Importing plotting configurations"
from plottings.configScanPlot import setYFieldVisibleInScanPlot,getYFieldVisibleInScanPlot,setXFieldInScanPlot,useSeparateYAxes,useSingleYAxis, getXFieldInScanPlot  # @UnusedImport
setXFieldInScanPlot(-1)
print("")

print "-"*100
print "Load checkBeamlineHealth function and run it"
from i05Shared.checkBeamlineHealth import * #@UnusedWildImport
checkForBeamlineProblems()
print("")

print "-"*100
print("Loading resolutionEstimator")
from i05Shared.resolutionEstimator import * #@UnusedWildImport
try:
	estimateResolution(100)
except:
	print "Failed to estimate beamline/analyser resolution"
print("")

print "-"*100
from gdaserver import smx, smy, smz, smdefocus
from gdascripts.scannable.sample_positions import SamplePositions
sp = SamplePositions("sp", [smx, smy, smz, smdefocus])
print("Creating sample positioner object sp. Store sample manipulator position components in a dictionary, save them to a file and move sample manipulator to previously saved positions in the dictionary.")
help(sp)

print("="*100)

if LocalProperties.get("gda.mode") == "live":  # don't execute in squish tests
		# Run the beamline staff scripts
		print "Running i05-1 LOCAL scripts."
		# Sample stage script for easy and safe movement of the stage to predefined positions
		# module location is /dls_sw/ixx/scripts/
		from beamline.sampleStage import * #@UnusedWildImport
		# module location is /dls_sw/ixx/scripts/
		from beamline.masterj import *
		# run "beamline/masterj.py"

print "Beamline initialization completed"
print "*"*100
