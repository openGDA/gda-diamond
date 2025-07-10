#localStation.py
#For beamline specific initialisation code.
#
print "="*100
print "Performing beamline initialisation code (i05)."

from i05Shared.localStation import * #@UnusedWildImport

print "-"*100
print "Creating beamline specific devices...";
print ("")

print("-"*100)
print(" Setting up sample_name ")
saz = Finder.find("saz")
def isgold():
	return saz.getPosition() < -18
sample_name=metadatatweaks.SampleNameScannable("sample_name","samplename", isgoldpost=isgold)
print("")

print "-"*100
print "Adding archiver to a global namespace"
archiver = Finder.find("archiver")
print ("")

print "-"*100
print "Creating energy_group scannable group";
energy_group = ScannableGroup() # Make a new ScannableGroup
energy_group.addGroupMember(energy) # Add members
energy_group.setName('energy_group') # Set the group name
energy_group.configure() # Configure the group, once all the members are added
print "Scannable group 'energy_group' created containing 'energy'";
print("")

print "-"*100
print "Loading Photon and Centre Energy Scan calculator... "
print "Usage: calculate_hv_scan_values(hv_start, hv_end, hv_step, start_centre_energy, centre_energy_hv_function_name)"
from scans.photonCentreEnergyScan import * #@UnusedWildImport
print("")

print "-"*100
print "Adding PGM backlash scannables pgm_gtrans_bl and pgm_mtrans_bl"
from beamlineGDA.pgm_with_backlash import * #@UnusedWildImport
print("")

print "-"*100
print "\nLoading Work Function calculator... "
from WorkFunctionCalculator import WorkFunctionCalculator
wf_calculator = WorkFunctionCalculator()
W_F = wf_calculator.getWorkFunction
alias("W_F")
print("")

print "-"*100
print "Importing Tenma PSU"
from gdaserver import tenma_psu
print("")

print "-"*100
print "Adding ring_current as a default_scannable"
add_default(ring_current)
print("")

print "-"*100
print "Importing plotting configurations"
from plottings.configScanPlot import setYFieldVisibleInScanPlot,getYFieldVisibleInScanPlot,setXFieldInScanPlot,useSeparateYAxes,useSingleYAxis, getXFieldInScanPlot  # @UnusedImport
setXFieldInScanPlot(0)
print("")

print "-"*100
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

def set_analyser_slit(slit):
		""" Set analyser entrance slit by integer value """
		analyser.getEntranceSlitInformationProvider().setCurrentSlitByValue(slit)
		print "Analyser slit is set to: "
		print get_analyser_slit()

def get_analyser_slit():
		""" Get current analyser entrance slit parameters """
		return analyser.getEntranceSlitInformationProvider().getCurrentSlit()

print "-"*100
from gdaserver import sax, say, saz, sapolar
from gdascripts.scannable.sample_positions import SamplePositions
sp = SamplePositions("sp", [sax, say, saz, sapolar])
print("Creating sample positioner object sp. Store sample manipulator position components in a dictionary, save them to a file and move sample manipulator to previously saved positions in the dictionary.")
help(sp)

print "="*100
if LocalProperties.get("gda.mode")=="live":  # don't execute in squish tests
	print "Running i05 LOCAL scripts."
	# module location is /dls_sw/ixx/scripts/
	from beamline.master import *
	# run "beamline/master.py"
	print "Finished running i05 LOCAL scripts."

print "Beamline initialization completed"
print "*"*100
