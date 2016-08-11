import time
from gda.data import NumTracker
from gda.data import PathConstructor
i22NumTracker = NumTracker("i22");
file = open(PathConstructor.createFromDefaultProperty()+"s3_calibration_"+time.strftime("%Y-%m-%d")+".txt","a")
file.write("Slits 3 calibration on "+time.strftime("%Y-%m-%d")+"\n\n")

print "Calibrating s3
pos d4filter "IL Diode VFM"
d4d1gain.setFixed(False)
d4d1.setSettletime(500)

pos s3_xcentre 0
pos s3_xgap 10
pos s3_ycentre 0
pos s3_ygap 10

scan s3_yplus 5 -2 0.1 d4d1
go edge
rscan s3_yplus 1 -1 0.01 d4d1
s3_yplus_edge = edge.result.pos
s3_yplus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s3 Y+ blade scan number: "+s3_yplus_scan+"\n")
pos s3_yplus 5

scan s3_yminus -5 2 0.1 d4d1
go edge
rscan s3_yminus -1 1 0.01 d4d1
s3_yminus_edge = edge.result.pos
s3_yminus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s3 Y- blade scan number: "+s3_yminus_scan+"\n")
pos s3_yminus -5

scan s3_xplus 5 -2 0.1 d4d1
go edge
rscan s3_xplus 1 -1 0.01 d4d1
s3_xplus_edge = edge.result.pos
s3_xplus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s3 X+ blade scan number: "+s3_xplus_scan+"\n")
pos s3_xplus 5

scan s3_xminus -5 2 0.1 d4d1
go edge
rscan s3_xminus -1 1 0.01 d4d1
s3_xminus_edge = edge.result.pos
s3_xminus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s3 X- blade scan number: "+s3_xminus_scan+"\n\n")
pos s3_xminus -5

pos s3_yplus s3_yplus_edge
pos s3_yminus s3_yminus_edge

while d4d1 >= 100 :
    inc s3_ygap -0.005
    sleep(5)

s3_yplus_offset = caget("BL22I-AL-SLITS-03:Y:PLUS.OFF")
caput("BL22I-AL-SLITS-03:Y:PLUS.OFF", 0)
s3_yplus_offset_new = caget("BL22I-AL-SLITS-03:Y:PLUS.RBV")
caput("BL22I-AL-SLITS-03:Y:PLUS.OFF", -float(s3_yplus_offset_new))

s3_yminus_offset = caget("BL22I-AL-SLITS-03:Y:MINUS.OFF")
caput("BL22I-AL-SLITS-03:Y:MINUS.OFF", 0)
s3_yminus_offset_new = caget("BL22I-AL-SLITS-03:Y:MINUS.RBV")
caput("BL22I-AL-SLITS-03:Y:MINUS.OFF", -float(s3_yminus_offset_new))

y_zero_old = float(s3_yplus_offset)-float(s3_yminus_offset)
y_zero_new = float(s3_yplus_offset_new)-float(s3_yminus_offset_new)
y_motion = y_zero_new - y_zero_old
file.write("Apparent vertical beam motion: "+str(y_motion)+" mm\n")

pos s3_ygap 15

pos s3_xplus s3_xplus_edge
pos s3_xminus s3_xminus_edge

while d4d1 >= 100 :
    inc s3_xgap -0.005
    sleep(5)

s3_xplus_offset = caget("BL22I-AL-SLITS-03:X:PLUS.OFF")
caput("BL22I-AL-SLITS-03:X:PLUS.OFF", 0)
s3_xplus_offset_new = caget("BL22I-AL-SLITS-03:X:PLUS.RBV")
caput("BL22I-AL-SLITS-03:X:PLUS.OFF", -float(s3_xplus_offset_new))

s3_xminus_offset = caget("BL22I-AL-SLITS-03:X:MINUS.OFF")
caput("BL22I-AL-SLITS-03:X:MINUS.OFF", 0)
s3_xminus_offset_new = caget("BL22I-AL-SLITS-03:X:MINUS.RBV")
caput("BL22I-AL-SLITS-03:X:MINUS.OFF", -float(s3_xminus_offset_new))

x_zero_old = float(s3_xplus_offset)-float(s3_xminus_offset)
x_zero_new = float(s3_xplus_offset_new)-float(s3_xminus_offset_new)
x_motion = x_zero_new - x_zero_old
file.write("Apparent horizontal beam motion: "+str(x_motion)+" mm\n")
file.close()

pos s3_xgap 15
pos d4filter("Clear deflected")

print "All Done!"

