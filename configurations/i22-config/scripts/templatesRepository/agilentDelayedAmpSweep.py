import time
from gda.data.metadata import GDAMetadataProvider
# amplitude sweep version
amplitudes=[0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,0.0,0.0,0.0]
#amplitudes=[0.0,0.0,0.0]
#
for amp in amplitudes:
		pos shutter "Reset"
		pos shutter "Open"
		time.sleep(1)
		pos aw ["SIN", 2000, amp, 0] 
		print "aw settings "+aw.getPosition().__str__()
		GDAMetadataProvider.getInstance().setMetadataValue("title","COL303_amp_scan_0Al" + aw())
		scan waittime 0 0 1 ncddetectors
		pos shutter "Close"
		time.sleep(590)

pos aw ["SIN", 1000, 0.0, 0] 
print "Script done"
pos shutter "Close"
print "Safe to enter hutch - check HV !!!!"
