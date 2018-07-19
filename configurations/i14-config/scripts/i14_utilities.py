from gda.configuration.properties import LocalProperties
from gda.data import NumTracker
from gda.factory import Finder

print("Running i14_utilities.py...")

i14NumTracker = NumTracker("i14")
finder = Finder.getInstance()

def isLive():
    mode = LocalProperties.get("gda.mode")
    return mode =="live"
