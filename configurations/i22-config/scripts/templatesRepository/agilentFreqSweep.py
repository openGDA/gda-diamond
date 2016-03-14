import time
from gda.data.metadata import GDAMetadataProvider
frequencies=[2000,1000,500,100,10]
pos shutter "Reset"
pos shutter "Open"
for freq in frequencies:
		pos aw ["SIN", freq, 8.0, 0] 
		print "aw settings "+aw.getPosition().__str__()
		GDAMetadataProvider.getInstance().setMetadataValue("title","COL174 fr_scan_0Al" + aw())
		scan waittime 0 0 1 ncddetectors

pos aw ["SIN", 1000, 0.0, 0] 
print "Script done"
pos shutter "Close"
print "Safe to enter hutch - check HV !!!!"
