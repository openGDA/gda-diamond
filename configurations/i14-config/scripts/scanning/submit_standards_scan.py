# Script to be called by the Standards scan GUI
# It splits up the arguments in the energy text box and calls standards_scan()
# The GUI sets the contents of the energy text box as a named value in the script service as "scanPath"
# and the exposure time as "exposureTime".

from gda.util.osgi import OsgiJythonHelper
from org.eclipse.dawnsci.analysis.api.persistence import IMarshallerService
from uk.ac.diamond.daq.mapping.api import StandardsScanParams
from gdaserver import xas_stage
from java.lang import Exception as JavaException #@Unresolvedimport #@Unusedimport

# An energy range specifies <start> <stop> <step> as a string such as: "5 20 0.001"
# Split the string and convert to floating point numbers
def split_and_convert_energy_range(energy_range):
    split_range = energy_range.split(' ')
    return [float(i) for i in split_range]

def move_xas_stage(position_value):
    print("Moving XAS stage to position: %.2f" % position_value)
    try:
        pos xas_stage position_value
        return True
    except Exception as e:
        print("[ERROR] Exception occurred while moving XAS stage: %s" % e)
        return False
    except JavaException as e:
        print("[ERROR] Exception occurred while moving XAS stage: %s" % e)
        return False

print("Running submit_standards_scan.py")

marshaller_service = OsgiJythonHelper.getService(IMarshallerService)
scanParams = marshaller_service.unmarshal(customParams, StandardsScanParams)

energy_ranges = scanParams.getScanPath().split(';')
path = [split_and_convert_energy_range(i) for i in energy_ranges]

# absorption energy line, not fluorescence energy line
lineToTrack = scanParams.getLineToTrack()
if lineToTrack is not None:
    lineToTrack = lineToTrack.getElement() + "-" + lineToTrack.getLine() + "a"
    print("Line to track = {}".format(lineToTrack))
    
xas_position = scanParams.getXasPosition()

if move_xas_stage(xas_position):
    try:
        standards_scan(path, scanParams.getExposureTime(), scanParams.isReverseScan(), lineToTrack)
    except Exception as e:
        print("[ERROR] Exception occurred during standards scan: %s" % e)
    except JavaException as e:
        print("[ERROR] Exception occurred during standards scan: %s" % e)
    finally:
        print("Moving XAS stage to 0")
        move_xas_stage(0)
else:
    print("[ERROR] XAS stage move failed, scan aborted.")


