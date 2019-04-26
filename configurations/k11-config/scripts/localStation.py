from gdascripts.scan.installStandardScansWithProcessing import *  # @UnusedWildImport
from gdascripts.watchdogs.watchdogs import enable_watchdogs, disable_watchdogs, list_watchdogs  # @UnusedImport
from gda.jython.commands.GeneralCommands import run
from gdascripts.scannable.timerelated import TimeSinceScanStart

print("Initialisation Started");

run("k11_utilities.py")

scan_processor.rootNamespaceDict = globals()  # @UndefinedVariable

# For access to new mscan mapping scan command.
print("Adding mscan mapping scan command. Use help(mscan) to get information on how to use it.")
#run('mapping_scan_commands.py')
from gdascripts.mscanHandler import *

# Watchdogs
print("Adding watchdog commands: enable_watchdogs, disable_watchdogs, list_watchdogs")
alias("enable_watchdogs")
alias("disable_watchdogs")
alias("list_watchdogs")

# timer scannable
# e.g. expose d1_det for 1 second every 5 seconds for 1 minute from now:
# scan timerScannable 0 60 5 d1_det 1
timerScannable = TimeSinceScanStart("timerScannable")

print("Initialisation Complete")
