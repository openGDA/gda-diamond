from gdascripts.scan.installStandardScansWithProcessing import *  # @UnusedWildImport
from gdascripts.watchdogs.watchdogs import enable_watchdogs, disable_watchdogs, list_watchdogs  # @UnusedImport
from gda.jython.commands.GeneralCommands import run
from gdascripts.scannable.timerelated import TimeSinceScanStart
from java.io import FileNotFoundException
import sys
from k11_utilities import is_live

print("Initialisation Started");

run("k11_utilities.py")

scan_processor.rootNamespaceDict = globals()  # @UndefinedVariable

# For access to new mscan mapping scan command.
print("Adding mscan mapping scan command. Use help(mscan) to get information on how to use it.")
#run('mapping_scan_commands.py')
from gdascripts.mscanHandler import *

run("jythonscannables.py")

# Watchdogs
print("Adding watchdog commands: enable_watchdogs, disable_watchdogs, list_watchdogs")
alias("enable_watchdogs")
alias("disable_watchdogs")
alias("list_watchdogs")

# timer scannable
# e.g. expose d1_det for 1 second every 5 seconds for 1 minute from now:
# scan timerScannable 0 60 5 d1_det 1
timerScannable = TimeSinceScanStart("timerScannable")


# experiment listener: writes visit to PV and copies template files
from experiment_listener import ExperimentListener
visit_pv = "BL11K-BL-SET-01:EXPERIMENTID" if is_live() else "ws413-AD-SIM-01:STAT:NDArrayPort"
listener = ExperimentListener(visit_pv)
add_reset_hook(listener.close)  # prevent multiple listeners on reset_namespace


print("Attempting to run localStationStaff.py from users script directory")
try:
    run("localStationStaff")
    print("localStationStaff.py completed")
except FileNotFoundException, e:
    print("No localStationStaff found")
except:
    print("Error running localStationStaff")
    print(sys.exc_info())
finally:
    print("=" * 80)

print("Initialisation Complete")