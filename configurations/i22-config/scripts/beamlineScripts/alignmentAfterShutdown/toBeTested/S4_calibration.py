import time
from gda.data import NumTracker
from gda.data import PathConstructor
i22NumTracker = NumTracker("i22");
file = open(PathConstructor.createFromDefaultProperty()+"s4_calibration_"+time.strftime("%Y-%m-%d")+".txt","a")
file.write("Slits 4 calibration on "+time.strftime("%Y-%m-%d")+"\n\n")

print "Calibrating s4
d10d2gain.setFixed(False)
d10d2.setSettletime(500)

pos s4_xcentre 0
pos s4_xgap 10
pos s4_ycentre 0
pos s4_ygap 10

scan s4_yplus 5 -2 0.1 d10d2
go edge
rscan s4_yplus 1 -1 0.01 d10d2
s4_yplus_edge = edge.result.pos
s4_yplus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s4 Y+ blade scan number: "+s4_yplus_scan+"\n")
pos s4_yplus 5

scan s4_yminus -5 2 0.1 d10d2
go edge
rscan s4_yminus -1 1 0.01 d10d2
s4_yminus_edge = edge.result.pos
s4_yminus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s4 Y- blade scan number: "+s4_yminus_scan+"\n")
pos s4_yminus -5

scan s4_xplus 5 -2 0.1 d10d2
go edge
rscan s4_xplus 1 -1 0.01 d10d2
s4_xplus_edge = edge.result.pos
s4_xplus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s4 X+ blade scan number: "+s4_xplus_scan+"\n")
pos s4_xplus 5

scan s4_xminus -5 2 0.1 d10d2
go edge
rscan s4_xminus -1 1 0.01 d10d2
s4_xminus_edge = edge.result.pos
s4_xminus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s4 X- blade scan number: "+s4_xminus_scan+"\n\n")
pos s4_xminus -5

pos s4_yplus s4_yplus_edge
pos s4_yminus s4_yminus_edge

while d10d2 >= 100 :
    inc s4_ygap -0.005
    sleep(5)

s4_yplus_offset = caget("BL22I-AL-SLITS-04:Y:PLUS.OFF")
caput("BL22I-AL-SLITS-04:Y:PLUS.OFF", 0)
s4_yplus_offset_new = caget("BL22I-AL-SLITS-04:Y:PLUS.RBV")
caput("BL22I-AL-SLITS-04:Y:PLUS.OFF", -float(s4_yplus_offset_new))

s4_yminus_offset = caget("BL22I-AL-SLITS-04:Y:MINUS.OFF")
caput("BL22I-AL-SLITS-04:Y:MINUS.OFF", 0)
s4_yminus_offset_new = caget("BL22I-AL-SLITS-04:Y:MINUS.RBV")
caput("BL22I-AL-SLITS-04:Y:MINUS.OFF", -float(s4_yminus_offset_new))

y_zero_old = float(s4_yplus_offset)-float(s4_yminus_offset)
y_zero_new = float(s4_yplus_offset_new)-float(s4_yminus_offset_new)
y_motion = y_zero_new - y_zero_old
file.write("Apparent vertical beam motion: "+str(y_motion)+" mm\n")

pos s4_ygap 15

pos s4_xplus s4_xplus_edge
pos s4_xminus s4_xminus_edge

while d10d2 >= 100 :
    inc s4_xgap -0.005
    sleep(5)

s4_xplus_offset = caget("BL22I-AL-SLITS-04:X:PLUS.OFF")
caput("BL22I-AL-SLITS-04:X:PLUS.OFF", 0)
s4_xplus_offset_new = caget("BL22I-AL-SLITS-04:X:PLUS.RBV")
caput("BL22I-AL-SLITS-04:X:PLUS.OFF", -float(s4_xplus_offset_new))

s4_xminus_offset = caget("BL22I-AL-SLITS-04:X:MINUS.OFF")
caput("BL22I-AL-SLITS-04:X:MINUS.OFF", 0)
s4_xminus_offset_new = caget("BL22I-AL-SLITS-04:X:MINUS.RBV")
caput("BL22I-AL-SLITS-04:X:MINUS.OFF", -float(s4_xminus_offset_new))

x_zero_old = float(s4_xplus_offset)-float(s4_xminus_offset)
x_zero_new = float(s4_xplus_offset_new)-float(s4_xminus_offset_new)
x_motion = x_zero_new - x_zero_old
file.write("Apparent horizontal beam motion: "+str(x_motion)+" mm\n")
file.close()

pos s4_xgap 15

print "All Done!"

