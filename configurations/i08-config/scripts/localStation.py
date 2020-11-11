import os
import sys

from ScannableInvertedValue import PositionInvertedValue
from gda.configuration.properties import LocalProperties
from gda.jython.commands.GeneralCommands import run, alias  # @UnusedImport
from gdascripts.pd.time_pds import waittimeClass, showtimeClass, showincrementaltimeClass, actualTimeClass
from gdascripts.scan.installStandardScansWithProcessing import *  # @UnusedWildImport
from gdascripts.watchdogs.watchdogs import enable_watchdogs, disable_watchdogs, list_watchdogs  # @UnusedImport
from gdascripts.malcolm.malcolm import reset_malcolm_after_scan


# Add config/scripts to import search path (why is this not already set in gda9?).
# Also, this seems to be different to run search path... imh 11/11/2016
scriptDir = LocalProperties.get("gda.config") + "/scripts/"
sys.path.append(os.path.abspath(scriptDir))

print("Initialisation Started");

run("i08_utilities.py")

photoDiode1Inverted = PositionInvertedValue("photoDiode1Inverted", "photoDiode1")

alias("setTitle")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

scan_processor.rootNamespaceDict = globals()  # @UndefinedVariable

waittime = waittimeClass('waittime')
showtime = showtimeClass('showtime')
inctime = showincrementaltimeClass('inctime')
actualTime = actualTimeClass("actualTime")

# For access to new mscan mapping scan command.
print("Adding mscan mapping scan command. Use help(mscan) to get information on how to use it.")
run('mapping_scan_commands.py')

# Energy to zone plate position
run('initialiseEnergyFocusFunction.py')

# Define function for Live Controls
run('sample_stage_control.py')
run('ioc_control.py')

# Define functions for sample movement
run('sample_control/move_sample.py')
alias('MoveSampleToTransferPos')
alias('MoveSampleToOpsPos')

# Watchdogs
print("Adding watchdog commands: enable_watchdogs, disable_watchdogs, list_watchdogs")
alias("enable_watchdogs")
alias("disable_watchdogs")
alias("list_watchdogs")

print("Initialisation Complete");
