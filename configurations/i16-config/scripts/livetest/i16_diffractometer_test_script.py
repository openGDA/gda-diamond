#livetest/scripts/diffractometer_test.py




raise Exception ("Dangerous without setting the energy")
#pos energy  12.398 #moves bragg, undulator, mirros, diffractometer, optics table


if not (12.397 < energy()[0] < 12.399):
	raise Exception ("Dangerous without setting the energy to 12.398")

# DANGER: make sure it is safe to run this script. Everything must be at 0 to start
for p in sixc():
	if abs(p) > 1:
		raise Exception("All sixc angles must be 0 to start reasonably safely")



print "Creating reffile and setting crystal"
reffile('dummy_test_with_cubic')
mode euler 1
latt([1,1,1,90,90,90])

print "Going to first 001"
c2th([0,0,1])

pos delta c2th([0,0,1]) eta c2th([0,0,1])/2
pos mu 0 gam 0
pos phi 0
pos chi 90

saveref('001',[0,0,1])

ubm('001',[1,0,0]) # assumes [1,0,0] is in the vertical plane, and determines azimuth normallly found from or2
#array('d',[-0.9999723587733832, 0.007435165380914164, 2.2260001343412905E-6, -0.00743516540177009, -0.9999723587304612, -9.51241620544971E-6, 2.1552122170511666E-6, -9.528703949842119E-6, 0.9999999999522796]) 
#CHANGHED: [2.0279487889011407e-05, -1.8574238763105146e-06, 0.9999999997926461, 0.9999999997943638, 1.2221592424340106e-07, -2.0279487662200264e-05, -1.2217825677428857e-07, 0.9999999999982677, 1.857426354343684e-06])

#<new
#>>>ubm('001',[0,1,0])
#array('d', [0.9999999999781956, 6.165595328849872e-06, -2.365297020176496e-06, -6.165629582852549e-06, 0.999999999876127, -1.4482101354505243e-05, 2.365207728946222e-06, 1.4482115937673516e-05, 0.999999999892337])
#>
hkl_calc([0,1,1])

print "Going to first 011"
pos hkl [0 1 1]

# Normaly scan phi to find reflection
pos phi
saveref('011',[0,1,1])
ubm('001','011')
#array('d',[-0.9999726435469858, 0.007396766367641229, 2.22600013434129E-6, -0.007396766388498801, -0.999972643504065, -9.51241620544971E-6, 2.155578118353377E-6, -9.528621182518454E-6, 0.9999999999522796]) 
#CHANGED:  [2.02794602636248e-05, -1.8577254675842665e-06, 0.9999999997926461, 0.9999999996855967, -1.4749534326065894e-05, -2.0279487662200264e-05, 1.4749571996567403e-05, 0.9999999998895003, 1.8574263543436837e-06])
showref()

print "Scanning"
scan hkl [0 0.1 1] [0 1 1] [0 .1 0] euler inctime
#===Injection mode pausing is enabled: TimeToInjection must exceed 5
#Warning::Vector and Azimuthal reference //, azimuthal reference not used
#Writing data to file:96716.dat
#h	k	l	phi	chi	eta	mu	delta	gamma	time_increment
#-0.0000	0.0000	1.0000	 -76.82897	  89.99923	  30.00113	  -0.00000	  60.00218	   0.00001	 18.56
#0.0000	0.1000	1.0000	 -89.57942	  84.28967	  30.16514	   0.00001	  60.33248	   0.00000	  4.98
#0.0000	0.2000	1.0000	 -89.57534	  78.68951	  30.65834	   0.00001	  61.31688	   0.00001	  5.40
#0.0000	0.3000	1.0000	 -89.57501	  73.30078	  31.46812	   0.00001	  62.93740	   0.00001	  4.27
#-0.0000	0.4000	1.0000	 -89.57581	  68.19738	  32.58428	  -0.00001	  65.16770	   0.00000	  3.80
#0.0000	0.5000	1.0000	 -89.57570	  63.43471	  33.98882	   0.00000	  67.97812	  -0.00001	  4.14
#-0.0000	0.6000	1.0000	 -89.57395	  59.03423	  35.67067	   0.00002	  71.33964	   0.00001	  3.93
#0.0000	0.7000	1.0000	 -89.57655	  55.00874	  37.61381	  -0.00000	  75.22925	  -0.00000	  4.15
#-0.0000	0.8000	1.0000	 -89.57550	  51.33904	  39.81685	   0.00001	  79.63341	  -0.00002	 10.49
#-0.0000	0.9000	1.0000	 -89.57448	  48.01146	  42.27629	  -0.00001	  84.55201	  -0.00000	  4.90
#0.0000	1.0000	1.0000	 -89.57644	  44.99981	  45.00151	   0.00002	  90.00381	  -0.00002	  4.53
#Scan complete.

#NEW ONES
#Writing data to file:/dls/i16/data/2011/cm2063-2/184182.dat
#     h	      k	     l	     phi	    chi	    eta	     mu	   delta	     gam	time_increment	      ic1	     rc
#0.0000	-0.0000	1.0000	-0.00104	0.00010	30.0009	0.00000	60.00189	-0.00028	         18.64	-0.683839	-0.1017
#-0.0000	0.1000	1.0000	-0.00161	5.71070	30.1663	0.00005	60.33281	-0.00000	          3.15	-0.653310	-0.1043
#0.0000	0.2000	1.0000	-0.00109	11.31004	30.6584	-0.00001	61.31721	-0.00030	          3.04	-0.607514	-0.1015
#-0.0000	0.3000	1.0000	-0.00119	16.69935	31.4685	-0.00001	62.93775	-0.00000	          3.05	-0.766266	-0.0997
#-0.0000	0.4000	1.0000	-0.00158	21.80151	32.5836	-0.00006	65.16850	0.00002	          3.04	-0.595304	-0.1021
#-0.0000	0.5000	1.0000	-0.00202	26.56516	33.9888	-0.00002	67.97895	0.00006	          3.14	-0.732686	-0.1023
#-0.0000	0.6000	1.0000	-0.00147	30.96387	35.6698	-0.00009	71.34045	0.00016	          3.25	-0.692998	-0.1014
#-0.0000	0.7000	1.0000	-0.00146	34.99212	37.6145	-0.00006	75.23017	-0.00000	          3.35	-0.638043	-0.1028
#-0.0000	0.8000	1.0000	-0.00203	38.65991	39.8166	-0.00008	79.63417	0.00016	          3.45	-0.601411	-0.1025
#-0.0000	0.9000	1.0000	-0.00153	41.98732	42.2760	-0.00008	84.55253	-0.00000	          3.45	-0.686890	-0.1001
#-0.0000	1.0000	1.0000	-0.00160	45.00011	45.0018	-0.00010	90.00436	0.00010	          3.61	-0.680787	-0.1030