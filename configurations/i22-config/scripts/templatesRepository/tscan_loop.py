# This script will inc a motor and then carry out a simple stability scan by measuring a diode reading,
#in this case mfbsdiode, 1000 times at 10msec intervals

for count in range (200):
    inc mfstage_y 0.001
    tscan 1000 0.01 mfbsdiode
print "script finished"