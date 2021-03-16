from gda.factory import Finder
from java.util import ArrayList
from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from org.eclipse.scanning.api.event.scan import ScanRequest
from org.eclipse.scanning.api.script import ScriptLanguage
from org.eclipse.scanning.api.script import ScriptRequest
from mapping_scan_commands import submit

# Functions to perform polarisation scans

print("Running polarisaton_functions.py")

# Set the ID gap & phase motors for a particular polarisation
# This function also stores the existing positions of these motors in the pseudo-scannable polarisation_values
def set_polarisation(id_gap, phase_upper, phase_lower):
    # Get current values
    id_gap_scannable = Finder.find("idgap")
    phase_upper_scannable = Finder.find("phase_upper")
    phase_lower_scannable = Finder.find("phase_lower")

    id_gap_pos = id_gap_scannable.getPosition()
    phase_upper_pos = phase_upper_scannable.getPosition()
    phase_lower_pos = phase_lower_scannable.getPosition()

    # Save current values as an array in polarisation_values
    print("Saving current values: id_gap: {}, phase_upper: {}, phase_lower: {}".format(id_gap_pos, phase_upper_pos, phase_lower_pos))
    values = ArrayList()
    values.add(id_gap_pos)
    values.add(phase_upper_pos)
    values.add(phase_lower_pos)
    polarisation_values = Finder.find('polarisation_values')
    polarisation_values.setCurrentPosition(values)

    # Set the positions for the required polarisation
    print("Setting positions: id_gap: {}, phase_upper: {}, phase_lower: {}".format(id_gap, phase_upper, phase_lower))
    id_gap_scannable.moveTo(id_gap)
    phase_upper_scannable.moveTo(phase_upper)
    phase_lower_scannable.moveTo(phase_lower)

# Restore the previous position sof the ID gap & phase motors
def restore_polarisation():
    polarisation_values = Finder.find('polarisation_values')
    values = polarisation_values.getPosition()
    id_gap = values[0]
    phase_upper = values[1]
    phase_lower = values[2]

    print('Restoring polarisation - id_gap: {}, phase_upper: {}, phase_lower: {}'.format(id_gap, phase_upper, phase_lower))
    id_gap_scannable = Finder.find("idgap")
    phase_upper_scannable = Finder.find("phase_upper")
    phase_lower_scannable = Finder.find("phase_lower")

    id_gap_scannable.moveTo(id_gap)
    phase_upper_scannable.moveTo(phase_upper)
    phase_lower_scannable.moveTo(phase_lower)

# Convert a script name to a ScriptRequest object
def create_script_request(scriptName):
    scriptRequest = ScriptRequest()
    scriptRequest.setLanguage(ScriptLanguage.SPEC_PASTICHE)
    scriptRequest.setFile("polarisation/" + scriptName)
    return scriptRequest

# Deserialise a ScanRequest and add scripts to be run before & after the scan.
# The "after" script is always restore_polarisation.py
def submit_scan(scanRequestJson, beforeScript, scanName):
    marshaller_service = OsgiJythonHelper.getService(IMarshallerService)

    scanRequest = marshaller_service.unmarshal(scanRequestJson, ScanRequest)
    scanRequest.setBeforeScript(create_script_request(beforeScript))
    scanRequest.setAfterScript(create_script_request("restore_polarisation.py"))
    scanRequest.setAlwaysRunAfterScript(True)

    # Add scanName to the description defined in the GUI
    sampleName = scanRequest.getScanMetadata()[0].getFieldValue("name")
    submitName = sampleName + " - " + scanName

    print("Polarisation scan, name: {}, request: {}".format(submitName, scanRequest))
    submit(scanRequest, block = False, name = submitName)
