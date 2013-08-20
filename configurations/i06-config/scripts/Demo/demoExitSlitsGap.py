import math;

print "Enable Exit Slits S4 Gap Control s4ygap";
#execfile("/opt/gda/config/scripts/enableExitSlitsGap.py");
#execfile("C:\Dev\gdaConfig\i06\scripts\enableExitSlitsGap.py");


#####################################################################################
#
#The Class is for creating a scannable Exit Slits Gap
#Usage:
#	EixtSlitsGapClass(name, refObj, gapFun, bladeFun)
#
#Parameters:
#   name:   Name of the exit slits gap
#	lowLimit: lower limit of slits gap
#	highLimit: Upper limit of slits gap
#	refObj: Name of the real motor (for example: s4y)
#	gapFun: Name of the function to calculate the slits gap based on blade position
#	bladeFun: Name of the function to calculate the real blade position based on gap
#
#####################################################################################
#s4ygap = EixtSlitsGapClass("s4ygap", 0, 10, "motor1","funTest01", "funTest02");
dgap = EixtSlitsGapClass("dgap", 16.0, 200.0, "testMotor1","s4_x_ygap", "s4_ygap_x");
#s4ygap = EixtSlitsGapClass("s4ygap", 16.0, 200.0, "testMotor1","s4_x_ygap", "s4_ygap_x");

#Calculate Exit Slit S4 X negative motor position from the YGap
#input: slit gap opening (um)
#output: motor position (mm)execfile("/opt/gda/config/scripts/setCAOutputFormat.py");
def s4_ygap_x(ygap):
	P0=14.5006;
	P1=-0.01368;
	P2=3.62863E-5;
	P3=-1.20877E-7;
	P4=3.10267E-10;
	P5=-5.53949E-13;
	P6=6.55968E-16;
	P7=-4.87657E-19;
	P8=2.05092E-22;
	P9=-3.71121E-26;
	x = P0+P1*ygap+P2*ygap**2+P3*ygap**3+P4*ygap**4+P5*ygap**5+P6*ygap**6+P7*ygap**7+P8*ygap**8+P9*ygap**9;
	return x;

#Calculate Exit Slit S4 YGap from the X negative motor position
#input: motor position (mm)
#output: slit gap opening (um)
def s4_x_ygap(x):
	ygap = 24.6357*math.exp(-0.04012*x**1.33062+6.00358)+242.53832*x-5956.4881;
	return ygap;

#Two test functions
def funTest02(ygap):
	x = ygap*ygap;
	return x;

def funTest01(x):
#	ygap = sqrt(x);
	ygap = x**0.5;
	return ygap;
