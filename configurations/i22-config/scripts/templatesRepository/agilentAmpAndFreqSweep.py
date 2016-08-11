import time
from gda.data.metadata import GDAMetadataProvider
amplitudes=[0.0,8.0]
frequencies=[1000,100,10,1]
for amp in amplitudes:
		pos shutter "Reset"
		pos shutter "Open"
#		time.sleep(1)
		pos aw ["SIN", 2000, amp, 0] 
		print "aw settings "+aw.getPosition().__str__()
		GDAMetadataProvider.getInstance().setMetadataValue("title","COL68_amp_scan_0Al" + aw())
		scan waittime 0 0 1 ncddetectors
#for freq in frequencies:
#		pos aw ["SIN", freq, 8.0, 0] 
#		print "aw settings "+aw.getPosition().__str__()
#		GDAMetadataProvider.getInstance().setMetadataValue("title","COL139_fr_scan_0Al" + aw())
#		scan waittime 0 0 1 ncddetectors


pos aw ["SIN", 1000, 0.0, 0] 
print "Script done"
pos shutter "Close"
print "Safe to enter hutch - check HV !!!!"

