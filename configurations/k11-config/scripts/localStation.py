from gdascripts.scan.installStandardScansWithProcessing import *  # @UnusedWildImport
from gdascripts.watchdogs.watchdogs import enable_watchdogs, disable_watchdogs, list_watchdogs  # @UnusedImport
from gda.jython.commands.GeneralCommands import run

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

print("Initialisation Complete")
