from gda.configuration.properties import LocalProperties
from gda.data import NumTracker

print("Running i14_utilities.py...")

i14NumTracker = NumTracker("i14")

def isLive():
    mode = LocalProperties.get("gda.mode")
    return mode =="live"
