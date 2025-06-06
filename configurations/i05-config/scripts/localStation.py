#localStation.py
#For beamline specific initialisation code.
#
print "="*20
print "Performing beamline specific initialisation code (i05)."
print "Importing generic features..."
import java
import array
from WorkFunctionCalculator import WorkFunctionCalculator
from gda.configuration.properties import LocalProperties
from gda.device.scannable.scannablegroup import ScannableGroup
from time import sleep, localtime
from gda.jython.commands.GeneralCommands import alias
from gdascripts.pd.time_pds import actualTimeClass
from gdascripts.scannable.timerelated import TimeSinceScanStart, clock, epoch  # @UnusedImport
from i05Shared.dirFileCommands import pwd, lwf, nwf, nfn

print "Installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()

print "load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport
from gdascripts.pd.dummy_pds import * #@UnusedWildImport

print "load time utilities for creating timer objects."
from gdascripts.pd.time_pds import * #@UnusedWildImport

print "Load utilities: caget(pv), caput(pv,value), attributes(object), "
from gdascripts.utils import * #@UnusedWildImport

print "load common physical constants"
from gdascripts.constants import * #@UnusedWildImport


class actTimeInInt(actualTimeClass):  # specialise to make displayed time semi-human-readable
	def rawGetPosition(self):
			pad = 10000
			t = localtime(time.time())      # t = localtime(super(actualTimeClass, self).rawGetPosition())
			tInInt = ((((((t[0]*100+t[1])*100+t[2])*pad+t[3])*100+t[4])*pad)+t[5])
			return tInInt                   # actual wall clock date & time
actTime = actTimeInInt("actTime")

# Make time scannable
# Example: scan timeScannable 0 3600 30 analyser - Make a scan starting now, for 1 hour, recording the analyser every 30 secs
timeScannable = TimeSinceScanStart('timeScannable')

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
def isgold():
	return saz.getPosition() < -18
sample_name=metadatatweaks.SampleNameScannable("sample_name","samplename",isgoldpost=isgold)

energy_group = ScannableGroup() # Make a new ScannableGroup
energy_group.addGroupMember(energy) # Add members
energy_group.setName('energy_group') # Set the group name
energy_group.configure() # Configure the group, once all the members are added
print "Scannable group 'energy_group' created containing 'energy'";

print "Loading Photon and Centre Energy Scan calculator... "
print "Usage: calculate_hv_scan_values(hv_start, hv_end, hv_step, start_centre_energy, centre_energy_hv_function_name)"
from scans.photonCentreEnergyScan import *

print "Loading Secondary Scannable Group Creator Script... "
print "Usage: scan_creator = ScanCreator(start, stop, step, input_list)"
print "scan_creator.create_group_and_tuples()"
from i05Shared.scan_creator import *
print "-" *20

print "Adding PGM backlash scannables pgm_gtrans_bl and pgm_mtrans_bl"
from beamlineGDA.pgm_with_backlash import *

print "\nLoading Work Function calculator... "
wf_calculator = WorkFunctionCalculator()
W_F = wf_calculator.getWorkFunction
alias("W_F")
# Add the work function calculator to the analyser
#analyser.setWorkFunctionProvider(wf_calculator)
#print "Added work function calculator - Usage: W_F(photon_energy)"
#binding_function = analyser.toBindingEnergy
def B_E(photon_energy):
		"""Since analyser.toBindingEnergy(scannable) returns an array,
		this function extracts the value from the array if that is the case"""
		result = binding_function(photon_energy)
		if isinstance(result, array.array):
				return result[0]
		return result
alias("B_E")
print "Added binding energy calculator - Usage: B_E(kinetic_energy)"

import arpes
from gdascripts.scan.pathscanCommand import pathscan
from i05Shared.pathscanTable import pathscanTable

print "Installing archiver client"
from gdascripts.archiver.archiver import archive
alias('archive')
archiver = Finder.find("archiver")

print "Importing Tenma PSU"
from gdaserver import tenma_psu

print "Adding ring_current as a default_scannable"
add_default(ring_current)

from plottings.configScanPlot import setYFieldVisibleInScanPlot,getYFieldVisibleInScanPlot,setXFieldInScanPlot,useSeparateYAxes,useSingleYAxis, getXFieldInScanPlot  # @UnusedImport
setXFieldInScanPlot(0)

from i05Shared.checkBeamlineHealth import *
checkForBeamlineProblems()

from i05Shared.resolutionEstimator import *
estimateResolution(100)

def set_analyser_slit(slit):
		""" Set analyser entrance slit by integer value """
		analyser.getEntranceSlitInformationProvider().setCurrentSlitByValue(slit)
		print "Analyser slit is set to: "
		print get_analyser_slit()

def get_analyser_slit():
		""" Get current analyser entrance slit parameters """
		return analyser.getEntranceSlitInformationProvider().getCurrentSlit()

print "="*20
if LocalProperties.get("gda.mode")=="live":  # don't execute in squish tests
	print "Running i05 scripts."
	# module location is /dls_sw/ixx/scripts/
	from beamline.master import *
	# run "beamline/master.py"
print "="*20
