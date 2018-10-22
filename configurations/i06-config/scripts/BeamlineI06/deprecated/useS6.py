
import math;

from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass;

print "Enable the Gap control of I06 Exit Slits S6";

s6ygap = CorrespondentDeviceClass("s6ygap","micron", 0.0, 600.0, "s6x","s6_x_ygap", "s6_ygap_x");
#S6.addGroupMember(s6ygap);

#Calculate Exit Slit S6 X negative motor position from the YGap
#input: slit gap opening (um)
#output: motor position (mm)
def s6_ygap_x(ygap):
	P0=-11.7279301227
	P1=0.0194152929711
	P2=-1.12948978658E-4
	P3=7.40297574845E-7
	P4=-3.46976646360E-9
	P5=1.09905068661E-11
	P6=-2.28882018062E-14
	P7=2.98659435609E-17
	P8=-2.20413687142E-20
	P9=6.99833786007E-24
	x = P0+P1*ygap+P2*ygap**2+P3*ygap**3+P4*ygap**4+P5*ygap**5+P6*ygap**6+P7*ygap**7+P8*ygap**8+P9*ygap**9;
	return x;



#Calculate Exit Slit S6 YGap from the X negative motor position
#input: motor position (mm)
#output: slit gap opening (um)
def s6_x_ygap(x):
	P0=2651881.10387
	P1=1815151.61909
	P2=456158.938778
	P3=33382.2547476
	P4=-7491.15586741
	P5=-2153.15957715
	P6=-247.276240465
	P7=-15.4640545570
	P8=-0.518283538999
	P9=-0.00732579507590
	ygap =P0+P1*x+P2*x**2+P3*x**3+P4*x**4+P5*x**5+P6*x**6+P7*x**7+P8*x**8+P9*x**9;
	return round(ygap,0);
