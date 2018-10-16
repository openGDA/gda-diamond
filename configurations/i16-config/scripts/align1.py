def ptl3cal():
	ptl3=11.564
	print "===Calibrating energy - last chance to abort!";
	if m2y()>0:
		print "===Looks like you have the Si mirror coating - change to Rh by typing energy.rh()"
	else:
		sleep(5)
		pos mono_screens 0
		pos ic1.gain 4
		pos uharmonic 9
		pos energy ptl3
		idgappos=idgap()
		pos shutter 1
		scan idgap idgappos-.1 idgappos+.1 .002 w .2 ic1
		#idgap(FindScanPeak('IC1')['IDgap'])
		go maxpos
		print "===Calibrating idgap - last chance to abort!"; sleep(5)
		#ucalibrate(en())
		ucalibrate()
		pos d3a 12
		scan energy ptl3-.05 ptl3+.05 .001 w .2 ic1
#		print "Now go to edge and type: en.calibrate(11.564) "  ##
		edgeval=eedge()
		go edgeval                     #
		print('=== Energy calibration change: %.1f eV' % (1000*(edgeval-ptl3))) #Steve 28 Feb 2018
		print('Going to '+str(edgeval)+' keV and calibrating')  #  Gareth 27 April 2016
		en.calibrate(11.564)                                    #
		pos d3a 90 energy ptl3
	
def go8keV():
	print "===Go to 8keV - last chance to abort!"; sleep(5)
	pos mono_screens 0
	#clear
	pos d3a 90
	pos ic1.gain 4
	pos ic2.gain 4
	pos diode.gain 0
	pos uharmonic 7
	pos energy 8.0
	idgappos=idgap()
	pos shutter 1
	scan idgap idgappos-.02 idgappos+.02 .001 w .2 ic1
	#idgap(FindScanPeak('IC1')['IDgap'])
	go maxpos
	print "===Calibrating idgap - last chance to abort!"; sleep(5)
	#ucalibrate(en())
	ucalibrate()
	pos energy 8

def alignpinh():
	pos phi 0
	print "===Align pin - edge must be aligned with camera at phi=0. Last chance to abort!"; sleep(5)
	pos eta 0
	pos chi 90
	# pos tthp tthp.diode # Removed by PRH 10/10/2018
	pos delta 0
#	pos diodegain 0
#	pos qbpm6inserter 1
	#qbpm6.set_range(3)
	pos s5vgap 5 s5hgap 5 s6vgap 5 s6hgap 5 #uncomment
	bypos=base_y()
	#scan base_y bypos-1 bypos+1 .02 w 1 diode hpos
	scan base_y bypos-1 bypos+1 .02 w 1 checkbeam diode
	pos phi 180
	#scan base_y bypos-1 bypos+1 .02 w 1 diode hpos
	scan base_y bypos-1 bypos+1 .02 w 1 diode
	#print "===Now you must move base_y to centre...";
	baseycen=(edge(0,'base_y','diode')[1]+edge(-1,'base_y','diode')[1])/2.
	go baseycen
	#pos s5vgap .5 s5hgap .5 s6vgap 1 s6hgap 1
	print 'Moving base_y to ' + str(baseycen)


def alignpinhAPDkapton():
	pos phi 90
	print "===Align pin - edge must be aligned with camera at phi=90. Last chance to abort!"; sleep(5)
	pos eta 0
	pos chi 90
	#pos tthp tthp.apd+90
	pos delta 0
#	pos diodegain 0
#	pos qbpm6inserter 1
	#qbpm6.set_range(3)
	pos s5vgap 5 s5hgap 5 s6vgap 5 s6hgap 5 #uncomment
	bypos=base_y()
	#scan base_y bypos-1 bypos+1 .02 w 1 diode hpos
	scan base_y bypos-1 bypos+1 .02 checkbeam t 1
	pos phi -90
	#scan base_y bypos-1 bypos+1 .02 w 1 diode hpos
	scan base_y bypos-1 bypos+1 .02 checkbeam t 1
	#print "===Now you must move base_y to centre...";
	baseycen=(edge(0,'base_y','APD')[1]+edge(-1,'base_y','APD')[1])/2.
	go baseycen
	#pos s5vgap .5 s5hgap .5 s6vgap 1 s6hgap 1
	print 'Moving base_y to ' + str(baseycen)


def alignpinhcryoDiode():
	pos phi 90
	print "===Align pin - edge must be aligned with camera at phi=90. Last chance to abort!"; sleep(5)
	pos eta 0
	pos chi 90
	#pos tthp tthp.apd+90
	pos delta 0
#	pos diodegain 0
#	pos qbpm6inserter 1
	#qbpm6.set_range(3)
	pos s5vgap 5 s5hgap 5 s6vgap 5 s6hgap 5 #uncomment
	bypos=base_y()
	#scan base_y bypos-1 bypos+1 .02 w 1 diode hpos
	scan base_y bypos-1 bypos+1 .02 checkbeam w .5 diode
	pos phi -90
	#scan base_y bypos-1 bypos+1 .02 w 1 diode hpos
	scan base_y bypos-1 bypos+1 .02 checkbeam w .5 diode
	#print "===Now you must move base_y to centre...";
	baseycen=(edge(0,'base_y','diode')[1]+edge(-1,'base_y','diode')[1])/2.
	go baseycen
	#pos s5vgap .5 s5hgap .5 s6vgap 1 s6hgap 1
	print 'Moving base_y to ' + str(baseycen)

def alignpinv():
	#please stop editing this!
	pos phi 180
	print "===Centre pin vertically on edge. Do horizontal first.Last chance to abort!"; sleep(5)
#	pos chi 45
	pos chi 0
	bzpos=base_z()[0]
	scan base_z bzpos-0.5 bzpos+0.5 .01 w 1 diode
	pos phi 0
	scan base_z bzpos-0.5 bzpos+0.5 .01 w 1 diode
	#print "===Now you must move base_z to centre...";
	basezcen=(edge(0,'Base_z','diode')[1]+edge(-1,'Base_z','diode')[2])/2. # now uses rising edge of first scan
	print 'Moving base_z to ' + str(basezcen)
	print base_z(basezcen)	#spc 2/10/11
	print "If the plots look ok then type energy.calibrate()"


def aligns5APDkapton():
	#use s5xgap because ss won't scan properly due to bug
	print "=== check pin out, APD in Kapton scattering in, delta 0"
	pos ds [3 3] ss [.05 2]
	scancn ss.x .02 21 t .5 
	go maxpos
	#scan s5xgap .1 -.05 -0.005 w .5 diode
	pos ds [3 3] ss [2 0.005]
	#pos ss [1 .01]
	scancn ss.y .005 31 t .5 
	go maxpos
	#scan s5ygap .05 -.02 -0.002 w .5 diode
	#pos ss [0 0]
	print "=== pos s5xgap and s5ygap to values where signal goes to zero, then set all s5 values to zero in epics"
	print "=== Make sure you move the right gaps!!"
	print "=== Don't do anything if they look close"

def aligns5():
	#use s5xgap because ss won't scan properly due to bug
	print "=== check pin out, diode in, delta 0"
	pos ds [3 3] ss [.05 2]
	scancn ss.x .02 21 w .5 diode
	go maxpos
	scan s5xgap .1 -.05 -0.005 w .5 diode
	pos ss [1 .01]
	scancn ss.y .005 31 w .5 diode
	go maxpos
	scan s5ygap .05 -.02 -0.002 w .5 diode
	pos ss [0 0]
	print "=== pos s5xgap and s5ygap to values where signal goes to zero, then set all s5 values to zero in epics"
	print "=== Make sure you move the right gaps!!"
	print "=== Don't do anything if they look close"

	
def aligns6():
	print "=== check pin out, diode in, delta 0"
	pos ss [3 3] ds [.05 2]
	scancn ds.x .02 21 w .5 diode
	go maxpos
	scan s6xgap .1 -.05 -0.005 w .5 diode
	pos ds [1 .01]
	scancn ds.y .005 31 w .5 diode
	go maxpos
	scan s6ygap .05 -.02 -0.002 w .5 diode
	pos ds [0 0]
	print "=== pos s6xgap and s6ygap to values where signal goes to zero, then set all s6 values to zero in epics"
	print "=== Make sure you move the right gaps!!"
	print "=== Don't do anything if they look close"
#base-z

#l3cal()
#go8kev()
#alignpinh()
#alignpinv()
