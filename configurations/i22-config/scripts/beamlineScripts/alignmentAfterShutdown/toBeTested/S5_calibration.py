"""
Purpose: To calibrate the S5 slits and re-zero the EPICS calibration field
Author: Andy Smith
Date: Nov 6th 2013

Function:   Script performs knife edge scans with each slit blade in turn (Y+, Y-, X+, X-) and uses the built-in
            GDA edge finding routine to define the mid-point of the beam.
            Scans are done against d10d2, so a diode must be positioned on sample table and connected to correct Femto 
            amplifier.
            Each knife edge is run twice, coarse (0.1mm) to find approximate position then fine (0.01mm)
            to define beam position.
            Logic for second scan parameters should ensure no motor limit violations.
            After beam centres are found, pairs of blades are brought to beam centre in turn and gap incremented 
            negatively until beam extinguished.
            EPICS calibrations are then reset and blades driven out to 4mm gap.
            A text file is generated in the current directory containing scan file numbers for the fine scans and a
            calculation of the apparent beam motion from the change in calibration offset.
"""


import time
from gda.data import NumTracker
from gda.data import PathConstructor
i22NumTracker = NumTracker("i22");

print "Calibrating s5"

file = open(PathConstructor.createFromDefaultProperty()+"s5_calibration_"+time.strftime("%Y-%m-%d")+".txt","a")
file.write("Slits 5 calibration on "+time.strftime("%Y-%m-%d")+"\n\n")

d10d2gain.setFixed(False)
d10d2.setSettletime(500)

pos s5_xcentre 0
pos s5_xgap 4
pos s5_ycentre 0
pos s5_ygap 4

scan s5_yplus 2 s5_yplus.getLowerInnerLimit()+0.05 0.1 d10d2
go edge
rscan_lower_limit = s5_yplus.getLowerInnerLimit()-s5_yplus.getPosition()
rscan_upper_limit = s5_yplus.getUpperInnerLimit()-s5_yplus.getPosition()
if s5_yplus.getPosition()-1 <= s5_yplus.getLowerInnerLimit():
    rscan s5_yplus 1 rscan_lower_limit+0.02 0.01 d10d2
elif s5_yplus.getPosition()+1 >= s5_yplus.getUpperInnerLimit():
    rscan s5_yplus rscan_upper_limit-0.02 -1 0.01 d10d2
else:
    rscan s5_yplus 1 -1 0.01 d10d2
s5_yplus_edge = edge.result.pos
s5_yplus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s5 Y+ blade scan number: "+s5_yplus_scan+"\n")
pos s5_yplus 2

scan s5_yminus -2 s5_yminus.getUpperInnerLimit()-0.05 0.1 d10d2
go edge
rscan_lower_limit = s5_yminus.getLowerInnerLimit()-s5_yminus.getPosition()
rscan_upper_limit = s5_yminus.getUpperInnerLimit()-s5_yminus.getPosition()
if s5_yminus.getPosition()+1 >= s5_yminus.getUpperInnerLimit():
    rscan s5_yminus -1 rscan_upper_limit-0.02 0.01 d10d2
elif s5_yminus.getPosition()-1 <= s5_yminus.getLowerInnerLimit():
    rscan s5_yminus rscan_lower_limit+0.02 1 0.01 d10d2
else:
    rscan s5_yminus -1 1 0.01 d10d2
s5_yminus_edge = edge.result.pos
s5_yminus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s5 Y- blade scan number: "+s5_yminus_scan+"\n")
pos s5_yminus -2

scan s5_xplus 2 s5_xplus.getLowerInnerLimit()+0.05 0.1 d10d2
go edge
rscan_lower_limit = s5_xplus.getLowerInnerLimit()-s5_xplus.getPosition()
rscan_upper_limit = s5_xplus.getUpperInnerLimit()-s5_xplus.getPosition()
if s5_xplus.getPosition()-1 <= s5_xplus.getLowerInnerLimit():
    rscan s5_xplus 1 rscan_lower_limit+0.02 0.01 d10d2
elif s5_xplus.getPosition()+1 >= s5_xplus.getUpperInnerLimit():
    rscan s5_xplus rscan_upper_limit-0.02 -1 0.01 d10d2
else:
    rscan s5_xplus 1 -1 0.01 d10d2
s5_xplus_edge = edge.result.pos
s5_xplus_scan = str(i22NumTracker.getCurrentFileNumber())
file.write("s5 X+ blade scan number: "+s5_xplus_scan+"\n")
pos s5_xplus 2

delta_yplus = s5_yplus.getPosition()-s5_yplus_edge
while abs(delta_yplus) > 0.01:
    pos s5_yplus s5_yplus_edge
    delta_yplus = s5_yplus.getPosition()-s5_yplus_edge

delta_yminus = s5_yminus.getPosition()-s5_yminus_edge
while abs(delta_yminus) > 0.01:
    pos s5_yminus s5_yminus_edge
    delta_yminus = s5_yminus.getPosition()-s5_yminus_edge

while d10d2 >= 100 :
    inc s5_ygap -0.005
    sleep(1)

s5_yplus_offset = caget("BL22I-AL-SLITS-05:Y:PLUS.OFF")
caput("BL22I-AL-SLITS-05:Y:PLUS.OFF", 0)
s5_yplus_offset_new = caget("BL22I-AL-SLITS-05:Y:PLUS.RBV")
caput("BL22I-AL-SLITS-05:Y:PLUS.OFF", -float(s5_yplus_offset_new))

s5_yminus_offset = caget("BL22I-AL-SLITS-05:Y:MINUS.OFF")
caput("BL22I-AL-SLITS-05:Y:MINUS.OFF", 0)
s5_yminus_offset_new = caget("BL22I-AL-SLITS-05:Y:MINUS.RBV")
caput("BL22I-AL-SLITS-05:Y:MINUS.OFF", -float(s5_yminus_offset_new))

y_zero_old = float(s5_yplus_offset)-float(s5_yminus_offset)
y_zero_new = float(s5_yplus_offset_new)-float(s5_yminus_offset_new)
y_motion = y_zero_new - y_zero_old
file.write("Apparent vertical beam motion: "+str(y_motion)+" mm\n")

pos s5_ygap 4

delta_xplus = s5_xplus.getPosition()-s5_xplus_edge
while abs(delta_xplus) > 0.01:
    pos s5_xplus s5_xplus_edge
    delta_xplus = s5_xplus.getPosition()-s5_xplus_edge

delta_xminus = s5_xminus.getPosition()-s5_xminus_edge
while abs(delta_xminus) > 0.01:
    pos s5_xminus s5_xminus_edge
    delta_xminus = s5_xminus.getPosition()-s5_xminus_edge

while d10d2 >= 100 :
    inc s5_xgap -0.005
    sleep(1)

s5_xplus_offset = caget("BL22I-AL-SLITS-05:X:PLUS.OFF")
caput("BL22I-AL-SLITS-05:X:PLUS.OFF", 0)
s5_xplus_offset_new = caget("BL22I-AL-SLITS-05:X:PLUS.RBV")
caput("BL22I-AL-SLITS-05:X:PLUS.OFF", -float(s5_xplus_offset_new))

s5_xminus_offset = caget("BL22I-AL-SLITS-05:X:MINUS.OFF")
caput("BL22I-AL-SLITS-05:X:MINUS.OFF", 0)
s5_xminus_offset_new = caget("BL22I-AL-SLITS-05:X:MINUS.RBV")
caput("BL22I-AL-SLITS-05:X:MINUS.OFF", -float(s5_xminus_offset_new))

x_zero_old = float(s5_xplus_offset)-float(s5_xminus_offset)
x_zero_new = float(s5_xplus_offset_new)-float(s5_xminus_offset_new)
x_motion = x_zero_new - x_zero_old
file.write("Apparent horizontal beam motion: "+str(x_motion)+" mm\n")
file.close()

pos s5_xgap 4

print "All Done!"

