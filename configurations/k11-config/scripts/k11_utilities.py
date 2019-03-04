from gda.configuration.properties import LocalProperties
from gda.device import Scannable
from gda.factory import Finder
from gda.jython.commands.GeneralCommands import ls_names


print("Running k11_utilities.py")

finder = Finder.getInstance()

def is_live():
    mode = LocalProperties.get("gda.mode")
    return mode =="live"

def ls_scannables():
    ls_names(Scannable)
