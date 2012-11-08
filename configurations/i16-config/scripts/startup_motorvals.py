

##PIN alignement
#infinity graticule at -1(H)  +168(V) 10/05/07
# sz 10.9

# table_horiz = 15 #14 on 17may2007
# base_z1 = 2.39
# base_z2 = 0.19
# base_z3 = 1.09
# base_y = 0 #mirrors out
# base_y = 15.00 #mirrors in

#print 'mirror positions: mirrors out of beam - switch on current'
#print m1x(-5) #normally the only thing that needs moving

#print 'mirror positions: mirrors in beam - switch on current' 1/06/07
#print m1x(-0.5)
#print m1y(-2.1)
#print m1pitch(3.8189)
#print m1roll(-0.0869)
#print m1yaw(0.3832)
#print m2x(14.447)
#print m2y(-8) - Rh coating
#print m2y(3) - plane Si 
#print m2pitch(3.832)
#print m2roll(0.0579)
#print m2yaw(0.0800)

#print "setting primary slit"
#3/3/07
#print s1xgap(1.5)
#print s1ygap(0.75)
#print s1xcentre(1.46)
#print s1ycentre(0.23)

#print "setting A2 and D1 to clear"
#print a2a(23.5)	#clear
#print d1a(40.5); print "clear 40.5", d1() 

#print "D2 not implemented - should be open"

#fixed beam height=12 mm

#print "moving s2 slits"
#print s2xminus(-5)
#print s2xplus(5)
#print s2yminus(-5)
#print s2yplus(5)

#print "setting d3"
#print d3a(90); print "clear 90", d3a()
#print d3a(60); print "Al foil 60", d3a()
# d3a(34); print "Nd foil 34"
# d3a(12); print "Pt foil 12"; L3=11.564 keV

#print d3d(0); print "screen 0", d3d() 
#print d3d(33); print "clear 33", d3d() 
#d3d(76.3); print "diode 76.3"

#ppp out of beam
#ppth(0)
#ppx20
#ppy7

#print "moving s3 slits"
#print s3xminus(-5)
#print s3xplus(5) 
#print s3yminus(-5)
#print s3yplus(5)

#print "setting d4"
#print d4a(20); print "clear 20", d4a() 
#print d4d(0); print "screen 0", d4d() 
#print d4d(33); print "clear 33", d4d
#print d4d(75.5); print "diode", d4d() 

#print "moving s4 slits"
#print s4xminus(-5)
#print s4xplus(5)
#print s4yminus(-5)
#print s4yplus(5)

#print "setting d5"03
#print d5a(20); print "clear 20", d5a() 
#print d5d(35); print "clear 35", d5d()
#print d5d(78); print "diode 78", d5d()# 76.5 mm on 25/4/07
#print d5d(0); print "screen OK for mirrors in and out"

#print 'Script completed'

#roll1=0.12 16/5/07 from survey
#pitch=-4.06 16/5/07
#finepitch=0
#roll2=+0.815 16/5/07
#perp=2;

#tthp(-18.5) Vortex (10th May 07)
# APD #tthp(-1.8) 10th May 07### tthp(-3) 7thDec07###tthp(-1.8) 30Jan08### tthp(-1.7) 1fev08
#tthp(29.5) camera (14th Nov 07) ## tthp(30)
#tthp(17) scintillator (10th May 07)
#tthp(51) diode
# tthp(70) nothing 

### PA LIMITS with diode
# tthp 86  # max (complete eta rotation)
# tthp -83 # min absolute and complete eta rot.

### Imp with offset @ -5.8 tthp 70 in the middle of the pillar!!!
###
#acesca([0.32 3.]) #standard settings for APD

#idgap_offset(0.543)

#jan08 tthp_offset with APD on PA =-3.74
#jan08 tthp_offset with vortex on PA =-21.5




