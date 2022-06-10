from gda.factory import Finder
from java.util import ArrayList
from org.eclipse.scanning.api.event.scan import ScanRequest
from org.eclipse.scanning.api.script import ScriptLanguage
from org.eclipse.scanning.api.script import ScriptRequest
from uk.ac.diamond.daq.mapping.api import PolarisationScanParameters
from mapping_scan_commands import submit

# Functions to perform polarisation scans

# The scannables we need to move to set up the scan
id_gap_scannable = Finder.find("idgap")
phase_scannable = Finder.find("phase")

# Module-level variables to store the original phase motor positions and those required for this scan
original_phase_position = None
polarisation_phase_position = None

print("Running polarisation_functions.py")

# main function to run a polarisation scan
def run_polarisation_scan(scanRequest, polarisationScanParameters):
    # Save current phase motor positions
    global original_phase_position
    global polarisation_phase_position
    global id_gap_scannable
    global phase_scannable

    print("Polarisation scan parameters: {}".format(polarisationScanParameters))

    original_phase_position = phase_scannable.getPosition()
    print("Original phase position {}".format(original_phase_position))

    polarisation_phase_position = polarisationScanParameters.getPhasePosition()
    print("Polarisation motor positions {}".format(polarisation_phase_position))

    # Submit the same ScanRequest with left & right polarisation
    if polarisationScanParameters.getRunFirst() == PolarisationScanParameters.Polarisation.LEFT:
        submit_left_polarisation_scan(scanRequest)
        submit_right_polarisation_scan(scanRequest)
    else:
        submit_right_polarisation_scan(scanRequest)
        submit_left_polarisation_scan(scanRequest)

# Submit scan with left polarisation
def submit_left_polarisation_scan(scanRequest):
    submit_polarisation_scan(scanRequest, "set_left_polarisation.py", "left")

# Submit scan with right polarisation
def submit_right_polarisation_scan(scanRequest):
    submit_polarisation_scan(scanRequest, "set_right_polarisation.py", "right")

# Take a ScanRequest and add scripts to be run before & after the scan.
# The "after" script is always restore_polarisation.py
def submit_polarisation_scan(scanRequest, beforeScript, scanName):
    scanRequest.setBeforeScript(create_script_request(beforeScript))
    scanRequest.setAfterScript(create_script_request("restore_polarisation.py"))
    scanRequest.setAlwaysRunAfterScript(True)

    # Add scanName to the description defined in the GUI
    sampleName = scanRequest.getScanMetadata()[0].getFieldValue("name")
    submitName = sampleName + " - " + scanName

    print("Polarisation scan, name: {}, request: {}".format(submitName, scanRequest))
    submit(scanRequest, block = False, name = submitName)

# Set the phase for a particular polarisation
# The required positions are taken from the global variable polarisation_phase_position
# If the parameter "negative" is set, the negative of the phase value will be used
def set_polarisation(negative):
    global polarisation_phase_position

    phase = polarisation_phase_position
    if negative:
        phase = -phase

    move_motors(phase)

# Move phase motors to their target positions.
# This cannot be done directly: instead, we need to:
#   - open the ID gap to 50 mm
#   - move the phase to zero
#   - move the phase to its target position
def move_motors(phase):
    global id_gap_scannable
    global phase_scannable

    print("Moving phase motors to: {}".format(phase))
    id_gap_scannable.moveTo(38)
    phase_scannable.moveTo(0)
    phase_scannable.moveTo(phase)

# Restore the previous positions of the ID gap & phase motors
def restore_polarisation():
    global original_phase_position
    move_motors(original_phase_position)

# Convert a script name to a ScriptRequest object
def create_script_request(scriptName):
    scriptRequest = ScriptRequest()
    scriptRequest.setLanguage(ScriptLanguage.SPEC_PASTICHE)
    scriptRequest.setFile("polarisation/" + scriptName)
    return scriptRequest
