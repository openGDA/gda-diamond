#pos shutter 1 #0 or 1 to close or open
#pos tthp tthp.diode #selcts diode detector (OK for direct beam)
#energy = 8 keV
#pos delta 0 # detector in direct beamk

#sx, sy, sz	sample movements
#inc sz -3 	relative move

#pos atten 0 #attenuators 0 255

#reffile('S181')	#creates or reuses reflection file
#showref()
#latt([5.14465])

#scan sz 12 14 .1 diode	#basic scan
#scancn sz .01 21 w .5 diode	#centred scan (step, npts) goes back to start
#go maxpos - go to peak value after scan

#pos do 0	#normal detector bank
#pos do do.pil	#change to pilatus

#c2th([0 0 4]) #calculates tth value
#pos pil 1

#scancn eta .01 21 pil .5

#scancn chi .05 21 phi phi() pil .5 chiroi
#saveref('004sub',[0 0 4])
#showref() #show the ref rs defined
#ubm('004sub',[1 0 0 ])	#dummy UB using one reflection
#mode euler 2

#pos hkl_calc [1 1 3]
#mode euler 1	#bisecting mode (safer for asymmetric reflerctions)

#scancn delta .005 21 pil .5 delroi

#latt([5.14465*4/4.0042]


#pos atten 0
#pos hkl [0 0 3.054]
#scancn th2th [.2 .4] 21 pil 1
#194441
#scancn th2th [.05 .1] 81 eta delta pil 2

#pos phi 180
#pos hkl [0 0 3.054]
#194442
#scancn th2th [.05 .1] 81 eta delta pil 2

#pos phi 180
#pos hkl [0 0 3.054]
#194443 #phi=180 to avoid multiple scattering
#scancn th2th [.05 .1] 121 eta delta pil 4

#194445
#scan hkl [0 0 4.01] [0 0 4.3] [0 0 .005] eta delta pil 1

#194446
#scan hkl [0 0 4.01] [0 0 4.3] [0 0 .0025] eta delta pil 4

#194447
#scan hkl [0 0 4.04] [0 0 4.2] [0 0 .005] eta delta pil 1

#194448
#scan hkl [0 0 1.01] [0 0 1.05] [0 0 .001] eta delta pil 1

#194449
#scan hkl [0 0 1] [0 0 1.1] [0 0 .001] eta delta pil 4

#194450
#scan hkl [0 0 0.95] [0 0 1.15] [0 0 .001] eta delta pil 2

#194451
#scan hkl [0 0 2.9] [0 0 3.3] [0 0 .001] eta delta pil 2

#selects APD point detector

#pos tthp tthp.apd; pos do 0
#mode euler 2
#pos ds [4 2]	#det slit [h, v]
#pos phi 180
#194454-69
#for lval in frange(3,3.15,0.01):
#	scan hkl [-.1,0,lval] [0.1,0,lval] [0.01, 0, 0] checkbeam eta delta chi phi t 2

#pos phi 225-10	#close to 225 but avoid  multple scattering from code
##194470
#for lval in frange(3,3.15,0.01):
#	scan hkl [-.1,-.1,lval] [0.1,0.1,lval] [0.01, 0.01, 0] checkbeam eta delta chi phi t 2

#pos phi 180
#194486
#for lval in frange(3,3.16,0.004):
#	scan hkl [-.1,0,lval] [0.1,0,lval] [0.004, 0, 0] checkbeam eta delta chi phi t 5

#pos phi 225-10	#close to 225 but avoid  multple scattering from code
#19xx
#for lval in frange(3,3.16,0.004):
#	scan hkl [-.1,-.1,lval] [0.1,0.1,lval] [0.004, 0.004, 0] checkbeam eta delta chi phi t 5
#ended ok

#pos phi 180
#pos do do.pil
#pos hkl [0 0 3.054]
#194574 #phi=180 to avoid multiple scattering; longer exposure
#scancn th2th [.05 .1] 121 eta delta pil 16

#pos hkl [0 0 3.054]
#194575 - no obvious change with position except few streaks and sharp spots
#scancn sy .1 21 pil 4 lcroi
#194576
#scancn sx .1 21 pil 4 lcroi

#pos phi 176
#pos hkl [0 0 5.1]
#pos eta 49.2
#194580 005 scan eta only (close to delta limit) 
#scancn eta .05 81 delta pil 8

#KB mirrors in...

gam0=-0.4
del0=-0.4

#pos phi 180
#pos do do.pil
#pos gam 0
#pos hkl [0 0 3.054]
#pos gam gam0
#inc delta del0
#pos pil 5

#194646
#scancn sy .005 21 pil 4 lcroi

#ci=250.5; cj=104.5
#i1off=3
#j1off=35
#roidown = scroi=DetectorDataProcessorWithRoi('roidown', pil, [SumMaxPositionAndValue()])
#iw=16; jw=8; roidown.setRoi(int(ci-iw/2.+i1off),int(cj-jw/2.+j1off),int(ci+iw/2.+i1off),int(cj+jw/2.+j1off))
#i2off=3
#j2off=-10
#roiup = scroi=DetectorDataProcessorWithRoi('roiup', pil, [SumMaxPositionAndValue()])
#iw=16; jw=8; roiup.setRoi(int(ci-iw/2.+i2off),int(cj-jw/2.+j2off),int(ci+iw/2.+i2off),int(cj+jw/2.+j2off))
#194649 -some fluctuation ss=[.04 .02]
#scancn sy .001 101 pil 4 roiup roidown
#194650
#pos ss [.02 .02]
#scancn sy .001 101 pil 4 roiup roidown
#pos ss [.01 .01]#mainly just weaker
#194651
#scancn sy .001 101 pil 4 roiup roidown
#pos ss [.02 .02]
#194652
#scancn sx .001 101 pil 4 roiup roidown
#keep [0.02 x 0.02]
#pos sx 0.25 sy -1.685	#original position

#194653 003 pilatus scans at various points on sample with microfocus mirrors (few microns)
#sxylist=[[0.222,-1.685],[0.25,-1.71],[0,0],[0.25,-1.685],[1,0],[0,1]]
#for sxy in sxylist:
#	pos sx sxy[0] sy sxy[1]
#	scancn th2th [.05 .1] 121 checkbeam hkl eta delta pil 60

#phi scan #194659 chi 90
#phi scan #194660 chi 70

#second sample....S42 1000s deposition time

#reffile('S42')	#new ref file
#saveref('004a',[0 0 4])#mirrors in
#ubm('004a',[0 1 0])
#saveref('024a',[0 2 4])
#ubm('004a','024a')

#pos sx 0 sy 1
#pos hkl [0 0 3.054]
#194673
#scancn th2th [.05 .1] 121 checkbeam hkl eta delta pil 5
#194674
#pos sx 0 sy 0
#scancn th2th [.05 .1] 121 checkbeam hkl eta delta pil 5


#ci=250.5; cj=104.5
#i1off=-33
#j1off=45
#roidown = scroi=DetectorDataProcessorWithRoi('roidown', pil, [SumMaxPositionAndValue()])
#iw=12; jw=10; roidown.setRoi(int(ci-iw/2.+i1off),int(cj-jw/2.+j1off),int(ci+iw/2.+i1off),int(cj+jw/2.+j1off))
#i2off=-33
#j2off=-32
#roiup = scroi=DetectorDataProcessorWithRoi('roiup', pil, [SumMaxPositionAndValue()])
#iw=12; jw=10; roiup.setRoi(int(ci-iw/2.+i2off),int(cj-jw/2.+j2off),int(ci+iw/2.+i2off),int(cj+jw/2.+j2off))

#pos hkl [0 0 3.054]
#pos sx 0 sy 0
#194676
#scancn sy .001 101 pil 2 roiup roidown
#194677
#scancn sy .001 101 pil 2 roiup roidown
#finer scans at two sy values (max and min)
#194678
#pos sy -0.017
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5
#194679
#pos sy 0.04
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5

#194685
#pos sx -0.013 sy -0.017
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 10

#194686
#pos sx -0.013 sy 0
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 10

#194687
#scancn sy .001 1001 pil 2 roiup roidown

#194688
#scancn sy .001 1001 pil 2 roiup roidown

#194689
#pos sx -0.013 sy 0
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5

#194690
#pos sx -0.013 sy 0
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5

#194701
#sxylist=[[-0.013,0],[-0.014,0],[-0.015,0],[-0.016,0],[-0.012,0],[-0.011,0],[-0.010,0],[-0.013,-0.001],[-0.013,-0.002],[-0.013,-0.003],[-0.013,0.001],[-0.013,0.002],[-0.013,0.003],[-0.012,0.001],[-0.012,0.002],[-0.012,0.003],[-0.011,0.001],[-0.011,0.002],[-0.011,-0.001],[-0.011,-0.002],[-0.012,-0.001],[-0.012,-0.002],[-0.012,-0.003],[-0.014,-0.001],[-0.014,-0.002],[-0.014,-0.003],[-0.015,-0.001],[-0.015,-0.002],[-0.014,0.001],[-0.014,0.002],[-0.014,0.003],[-0.015,0.001],[-0.015,0.002],[-0.016,0.001],[-0.016,-0.001],[-0.01,-0.001],[-0.01,0.001]]   
#for sxy in sxylist:   
#	pos sx sxy[0] sy sxy[1]
#	scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5

#194735
#pos ss [0.2 0.2] open slits to 0.2 0.2 mm
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5

#194736
#pos ss [0.1 0.1] slits to 0.1 0.1 mm
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5

#194737
#pos ss [0.05 0.05] slits to 0.05 0.05 mm
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5

#194738
#pos ss [0.02 0.02] slits to 0.02 0.02 mm
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5

#194739
#pos ss [0.01 0.01] slits to 0.01 0.01 mm
scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5

#194742
#pos ss [0.05 0.05] slits to 0.05 0.05 mm
#pos sx -0.016
#scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 5


#194744
sxylist=[[-0.013,0],[-0.013,0],[-0.013,0],[-0.014,0],[-0.016,0],[-0.012,0],[-0.013,-0.001],[-0.013,0.001],[-0.013,0.003],[-0.012,0.001],[-0.012,-0.001],[-0.014,-0.001],[-0.014,0.001]]   
for sxy in sxylist:   
	pos sx sxy[0] sy sxy[1]
	scancn th2th [.025 .05] 241 checkbeam hkl eta delta pil 20






