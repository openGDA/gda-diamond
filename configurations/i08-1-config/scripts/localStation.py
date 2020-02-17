from java.io import FileNotFoundException # @UnresolvedImport
from gdascripts.scan.installStandardScansWithProcessing import *  # @UnusedWildImport
from gdascripts.watchdogs.watchdogs import enable_watchdogs, disable_watchdogs, list_watchdogs  # @UnusedImport
from ScannableInvertedValue import PositionInvertedValue
from gda.jython.commands.GeneralCommands import run

from i08_1_utilities import is_live

print("Initialisation Started");

run("i08_1_utilities.py")

photoDiode1Inverted = PositionInvertedValue("photoDiode1Inverted", "photoDiode1")

scan_processor.rootNamespaceDict = globals()  # @UndefinedVariable

# For access to new mscan mapping scan command.
print("Adding mscan mapping scan command. Use help(mscan) to get information on how to use it.")
run('mapping_scan_commands.py')

# Energy to zone plate position
run('initialiseEnergyFocusFunction.py')
run('initialise_zpz_osa_function.py')

# Watchdogs
print("Adding watchdog commands: enable_watchdogs, disable_watchdogs, list_watchdogs")
alias("enable_watchdogs")
alias("disable_watchdogs")
alias("list_watchdogs")

# Mode-specific setup
if is_live():
    print("Running in live mode: attempting to run localStationUser.py in users script directory")
    try:
        run("localStationUser.py")
    except FileNotFoundException, e:
        print("No localStationUser run")
    except:
        print("Exception running localStationUser")
else:
    print("Running in dummy mode")

print("Initialisation Complete");
