# localStation.py
# For beamline specific initialisation code.
#
from gda.jython.commands.GeneralCommands import alias
from mapping_scan_commands import (
    mscan, detector, scan_request, submit, step, grid, circ, poly, rect)

print "Installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict = globals()

print("Importing watchdog commands")
from gdascripts.watchdogs.watchdogs import enable_watchdogs, disable_watchdogs, list_watchdogs, set_watchdog_enabled, is_watchdog_enabled
alias("enable_watchdogs")
alias("disable_watchdogs")
alias("list_watchdogs")
disable_watchdogs()
