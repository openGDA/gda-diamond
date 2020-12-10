#localStation.py
#For beamline specific initialisation code.
#
print "===================================================================";
print "Performing beamline specific initialisation code (i05).";
print

print "Importing generic features...";
import java
import array
from WorkFunctionCalculator import WorkFunctionCalculator
from gda.configuration.properties import LocalProperties
from gda.device.scannable.scannablegroup import ScannableGroup
from time import sleep, localtime
from gda.jython.commands.GeneralCommands import alias
from gdascripts.pd.time_pds import actualTimeClass
from gdascripts.scannable.timerelated import TimeSinceScanStart
from dirFileCommands import pwd, lwf, nwf, nfn

# Get the location of the GDA beamline script directory
gdaScriptDir = LocalProperties.get("gda.config")+"/scripts/"
gdascripts = LocalProperties.get("gda.install.git.loc")+"/gda-core.git/uk.ac.gda.core/scripts/gdascripts/"

print "Installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()

execfile(gdascripts + "/pd/epics_pds.py");

execfile(gdascripts + "/pd/time_pds.py");


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

execfile(gdascripts + "/pd/dummy_pds.py");

execfile(gdascripts + "/utils.py");

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
def isgold():
   return saz.getPosition() < -18
sample_name=metadatatweaks.SampleNameScannable("sample_name","samplename",isgoldpost=isgold)

# Setting Analyser slices to 1000
try:
    analyser.setSlices(1000)
except:
    print "There was a problem setting the analyser slices to 1000, please check detector parameters." 
centre_energy=analyser.getCentreEnergyScannable()
centre_energy.setName("centre_energy")
centre_energy.setInputNames(["centre_energy"])

energy_group = ScannableGroup() # Make a new ScannableGroup
energy_group.addGroupMember(energy) # Add members
energy_group.addGroupMember(centre_energy)
energy_group.setName('energy_group') # Set the group name
energy_group.configure() # Configure the group, once all the members are added
print "Scannable group 'energy_group' created containing 'energy' and 'centre_energy'";

print "Loading Photon and Centre Energy Scan calculator... "
print "Usage: calculate_hv_scan_values(hv_start, hv_end, hv_step, start_centre_energy, centre_energy_hv_function_name)"
execfile(gdaScriptDir + "photonCentreEnergyScan.py")

print "Loading Secondary Scannable Group Creator Script... "
print "Usage: scan_creator = ScanCreator(start, stop, step, input_list)"
print "scan_creator.create_group_and_tuples()"
execfile(gdaScriptDir + "scan_creator.py")
print "-" *20
print "Adding PGM backlash scannables pgm_gtrans_bl and pgm_mtrans_bl"
execfile(gdaScriptDir + "/beamline/pgm_with_backlash.py")

print "\nLoading Work Function calculator... "
wf_calculator = WorkFunctionCalculator()
W_F = wf_calculator.getWorkFunction
alias("W_F")
# Add the work function calculator to the analyser
analyser.setWorkFunctionProvider(wf_calculator)
print "Added work function calculator - Usage: W_F(photon_energy)"
binding_function = analyser.toBindingEnergy
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
execfile(gdascripts + "scan/pathscanCommand.py");
from pathscanTable import pathscanTable

print "Installing archiver client"
from gdascripts.archiver.archiver import archive
alias('archive')
archiver = Finder.find("archiver")

print "Importing Tenma PSU"
from gdaserver import tenma_psu

print "==================================================================="
if LocalProperties.get("gda.mode")=="live":  # don't execute in squish tests
   print "Running i05 scripts."
   run "beamline/master.py"
print "==================================================================="
