import time
from gda.data import NumTracker
from gda.data import PathConstructor
i22NumTracker = NumTracker("i22");
file = open(PathConstructor.createFromDefaultProperty()+"s2_calibration_"+time.strftime("%Y-%m-%d")+".txt","a")
file.write("Slits 2 calibration on "+time.strftime("%Y-%m-%d")+"\n\n")

print "Calibrating s2
pos d4filter "IL Diode VFM"
d4d1gain.setFixed(False)
d4d1.setSettletime(500)

pos s2_xcentre 0
pos s2_xgap 10
pos s2_ycentre 0
pos s2_ygap 10

scan s2_yplus 5 -2 0.1 d4d1
go edge
rscan s2_yplus 1 -1 0.01 d4d1
s2_yplus_edge = edge.result.pos
s2_yplus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s2 Y+ blade scan number: "+s2_yplus_scan+"\n")
pos s2_yplus 5

scan s2_yminus -5 2 0.1 d4d1
go edge
rscan s2_yminus -1 1 0.01 d4d1
s2_yminus_edge = edge.result.pos
s2_yminus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s2 Y- blade scan number: "+s2_yminus_scan+"\n")
pos s2_yminus -5

scan s2_xplus 5 -2 0.1 d4d1
go edge
rscan s2_xplus 1 -1 0.01 d4d1
s2_xplus_edge = edge.result.pos
s2_xplus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s2 X+ blade scan number: "+s2_xplus_scan+"\n")
pos s2_xplus 5

scan s2_xminus -5 2 0.1 d4d1
go edge
rscan s2_xminus -1 1 0.01 d4d1
s2_xminus_edge = edge.result.pos
s2_xminus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s2 X- blade scan number: "+s2_xminus_scan+"\n\n")
pos s2_xminus -5

pos s2_yplus s2_yplus_edge
pos s2_yminus s2_yminus_edge

while d4d1 >= 100 :
    inc s2_ygap -0.005
    sleep(5)

s2_yplus_offset = caget("BL22I-AL-SLITS-02:Y:PLUS.OFF")
caput("BL22I-AL-SLITS-02:Y:PLUS.OFF", 0)
s2_yplus_offset_new = caget("BL22I-AL-SLITS-02:Y:PLUS.RBV")
caput("BL22I-AL-SLITS-02:Y:PLUS.OFF", -float(s2_yplus_offset_new))

s2_yminus_offset = caget("BL22I-AL-SLITS-02:Y:MINUS.OFF")
caput("BL22I-AL-SLITS-02:Y:MINUS.OFF", 0)
s2_yminus_offset_new = caget("BL22I-AL-SLITS-02:Y:MINUS.RBV")
caput("BL22I-AL-SLITS-02:Y:MINUS.OFF", -float(s2_yminus_offset_new))

y_zero_old = float(s2_yplus_offset)-float(s2_yminus_offset)
y_zero_new = float(s2_yplus_offset_new)-float(s2_yminus_offset_new)
y_motion = y_zero_new - y_zero_old
file.write("Apparent vertical beam motion: "+str(y_motion)+" mm\n")

pos s2_ygap 1.28

pos s2_xplus s2_xplus_edge
pos s2_xminus s2_xminus_edge

while d4d1 >= 100 :
    inc s2_xgap -0.005
    sleep(5)

s2_xplus_offset = caget("BL22I-AL-SLITS-02:X:PLUS.OFF")
caput("BL22I-AL-SLITS-02:X:PLUS.OFF", 0)
s2_xplus_offset_new = caget("BL22I-AL-SLITS-02:X:PLUS.RBV")
caput("BL22I-AL-SLITS-02:X:PLUS.OFF", -float(s2_xplus_offset_new))

s2_xminus_offset = caget("BL22I-AL-SLITS-02:X:MINUS.OFF")
caput("BL22I-AL-SLITS-02:X:MINUS.OFF", 0)
s2_xminus_offset_new = caget("BL22I-AL-SLITS-02:X:MINUS.RBV")
caput("BL22I-AL-SLITS-02:X:MINUS.OFF", -float(s2_xminus_offset_new))

x_zero_old = float(s2_xplus_offset)-float(s2_xminus_offset)
x_zero_new = float(s2_xplus_offset_new)-float(s2_xminus_offset_new)
x_motion = x_zero_new - x_zero_old
file.write("Apparent horizontal beam motion: "+str(x_motion)+" mm\n")
file.close()

pos s2_xgap 2.04
pos d4filter("Clear deflected")

print "All Done!"

