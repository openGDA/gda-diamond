from gda.factory import Finder
from java.util import ArrayList
from org.eclipse.scanning.api.event.scan import ScanRequest
from org.eclipse.scanning.api.script import ScriptLanguage
from org.eclipse.scanning.api.script import ScriptRequest
from uk.ac.diamond.daq.mapping.api import PolarisationScanParameters
from mapping_scan_commands import submit
from i08_shared_utilities import is_live
from id_energy_gap_mapping import set_mappings_for_linear_polarisation, set_mappings_for_circular_polarisation

# Functions to perform polarisation scans

# The scannables we need to move to set up the scan
id_gap_scannable = Finder.find("idgap")
phase_scannable = Finder.find("phase")

# Module-level variables to store the original phase motor positions and those required for this scan
original_phase_position = None
polarisation_phase_position = None
polarisation_idgap_position = 50

left_polarisation_script = "set_left_polarisation.py"
right_polarisation_script = "set_right_polarisation.py"

print("Running polarisation_functions.py")

def run_polarisation_scan(scanRequest, polarisationScanParameters):
    
    global original_phase_position
    global polarisation_phase_position
    global id_gap_scannable
    global phase_scannable
    
    print("Polarisation scan parameters: {}".format(polarisationScanParameters))
    
    original_phase_position = phase_scannable.getPosition()
    print("Original phase position {}".format(original_phase_position))
    
    polarisation_phase_position = polarisationScanParameters.getPhasePosition()
    print("Polarisation motor positions {}".format(polarisation_phase_position))
    
    print("Moving id gap to: {}".format(polarisation_idgap_position))
    id_gap_scannable.moveTo(polarisation_idgap_position)
    
    if polarisationScanParameters.getRunFirst() == PolarisationScanParameters.Polarisation.LEFT:
        submit_polarisation_scan("left", left_polarisation_script, scanRequest)
        submit_polarisation_scan("right", right_polarisation_script, scanRequest)
    else:
        submit_polarisation_scan("right", left_polarisation_script, scanRequest)
        submit_polarisation_scan("left", right_polarisation_script, scanRequest)


def set_polarisation(negative):
    global polarisation_phase_position
    target_phase = polarisation_phase_position
    if negative:
        target_phase = -target_phase
    
    move_phase(target_phase)
    set_mappings_for_circular_polarisation()

def move_phase(position):
    global phase_scannable
    print("Moving phase motors to: {}".format(position))
    phase_scannable.moveTo(0)
    phase_scannable.moveTo(position)
    
def restore_polarisation():
    global original_phase_position
    move_phase(original_phase_position)
    set_mappings_for_linear_polarisation()

def submit_polarisation_scan(scanName, beforeScript, scanRequest):
    scanRequest.setBeforeScript(create_script_request(beforeScript))
    scanRequest.setAfterScript(create_script_request("restore_polarisation.py"))
    scanRequest.setAlwaysRunAfterScript(True)

    # Add scanName to the description defined in the GUI
    submitName = scanRequest.getScanMetadata()[0].getFieldValue("name") + " - " + scanName

    print("Polarisation scan, name: {}, request: {}".format(submitName, scanRequest))
    submit(scanRequest, block = False, name = submitName)
    
# Convert a script name to a ScriptRequest object
def create_script_request(scriptName):
    scriptRequest = ScriptRequest()
    scriptRequest.setLanguage(ScriptLanguage.SPEC_PASTICHE)
    scriptRequest.setFile("polarisation/" + scriptName)
    return scriptRequest
