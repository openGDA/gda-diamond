from java.io import FileNotFoundException # @UnresolvedImport
from gdascripts.scan.installStandardScansWithProcessing import *  # @UnusedWildImport
from gdascripts.watchdogs.watchdogs import enable_watchdogs, disable_watchdogs, list_watchdogs  # @UnusedImport
from gdascripts.malcolm.malcolm import reset_malcolm_after_scan
from ScannableInvertedValue import PositionInvertedValue
from gda.jython.commands.GeneralCommands import run

from i08_shared_utilities import is_live, ls_scannables

print("Initialisation Started");

scan_processor.rootNamespaceDict = globals()  # @UndefinedVariable

# For access to new mscan mapping scan command.
print("Adding mscan mapping scan command. Use help(mscan) to get information on how to use it.")
run('mapping_scan_commands.py')

# Energy to zone plate position
run('initialiseEnergyFocusFunction.py')
run('initialise_zpz_osa_function.py')

# photoDiode1Inverted
run('definePhotoDiode1Inverted.py')

# Watchdogs
print("Adding watchdog commands: enable_watchdogs, disable_watchdogs, list_watchdogs")
alias("enable_watchdogs")
alias("disable_watchdogs")
alias("list_watchdogs")

# Andor information
try:
    run("ptycho/ptycho_setup.py")
except Exception, e:
    print("Exception getting Andor information: %s" %(e))

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
