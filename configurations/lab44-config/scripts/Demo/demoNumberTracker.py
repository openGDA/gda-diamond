
#How to use Track Number (Scan number)
from gda.data import NumTracker

nt = NumTracker("tmp")

#get current scan number
nt.getCurrentFileNumber()

#increase the scan number for one
nt.incrementNumber();
#set new scan number
#nt.setFileNumber(2000)

del nt