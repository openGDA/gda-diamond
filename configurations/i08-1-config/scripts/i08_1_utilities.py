from gda.configuration.properties import LocalProperties
from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names

print("Running i08_1_utilities.py")

def is_live():
    mode = LocalProperties.get("gda.mode")
    return mode =="live"

def ls_scannables():
    ls_names(Scannable)
