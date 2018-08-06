MirrorInUse=float(caget("BL05I-OP-SWTCH-01:MIRCTRL:RBV:MIRROR"))
sMirror = "Mi3"
dTime2Wait=5
dTime2WaitLong = 90

pos s2_xsize 6
pos s2_ysize 6
pos s2_xcentre 0.5
pos s2_ycentre 0

if MirrorInUse == 2:
    'for Mi3'
    print "Moving M1 for Mi3"
    pos m1_x -0.63 waittime dTime2Wait
    pos m1_y -0.62 waittime dTime2Wait
    pos m1_z 0 waittime dTime2Wait
    pos m1_pitch 800 waittime dTime2Wait
    pos m1_yaw 0 waittime dTime2Wait
    pos m1_roll -600 waittime dTime2Wait
    print "Moving Mi3"
    pos m3mj6_x -2.2 waittime dTime2Wait
    pos m3mj6_z 0 waittime dTime2Wait
    pos m3mj6_pitch 4810 waittime dTime2Wait 'changed to 4385 on 01/12/2013, was 4900 before PD, 4931 12/02/2014 PD, 4810 piezo 0 24/06/2014 PD'
    pos m3mj6_yaw 1700 waittime dTime2Wait
    pos m3mj6_roll 1000 waittime dTime2Wait
    pos m3mj6_y 0.14 waittime dTime2WaitLong
    sMirror = "Mi3"
elif MirrorInUse == 1:
    'for Mj6'
    sMirror = "Mj6"
    print "Moving M1 for Mj6"
    pos m1_x -0.63 waittime dTime2Wait
    pos m1_y -0.62 waittime dTime2Wait
    pos m1_z 0 waittime dTime2Wait
    pos m1_pitch 240 waittime dTime2Wait
    pos m1_yaw 0 waittime dTime2Wait
    pos m1_roll -600 waittime dTime2Wait 'Changed to -600 from 0 on 20.01.2014, PD'
    print "Moving Mj6"
    pos m3mj6_x 3.0997 waittime dTime2Wait
    pos m3mj6_z 0 waittime dTime2Wait
    pos m3mj6_pitch 4835 waittime dTime2Wait'4350 29.11.2013, before was 4840 20.01.2014 4385 PD'
    pos m3mj6_yaw 3000 waittime dTime2Wait
    pos m3mj6_roll 1000 waittime dTime2Wait 'Change to 1000 from -4250 on 20.01.2014, PD'
    pos m3mj6_y -0.9 waittime dTime2WaitLong'1.067 05.02.2014 PD'
print "Done, mirror ",sMirror," positioned"
