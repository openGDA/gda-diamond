
#How to use Track Number (Scan number)
from gda.data import NumTracker
from gda.configuration.properties import LocalProperties

nt = NumTracker(LocalProperties.get("gda.data.numtracker.extension"))

#get current scan number
nt.getCurrentFileNumber()

#increase the scan number for one
nt.incrementNumber();
#set new scan number
#nt.setFileNumber(2000)

del nt