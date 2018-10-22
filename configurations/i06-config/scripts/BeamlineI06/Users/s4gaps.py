
import math;
from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass

print "Enable the Gap control of of I06 Exit Slits S4";
#####################################################################################
#
#Use the CorrespondentDevice Class to create a scannable Exit Slits Gap (um) 
# based on the X motor position (mm)
#
#Usage:
#	CorrespondentDeviceClass(name, lowLimit, highLimit, refObj, funForeward, funBackward)
#
#Parameters:
#   name:   Name of the exit slits gap
#	lowLimit: lower limit of slits gap
#	highLimit: Upper limit of slits gap
#	refObj: Name of the real motor (for example: "s4y")
#	funForeward: Name of the function to calculate the new position based on refObj position
#	funBackward: Name of the function to calculate back the refObj position based on new position
#
#Example: When calculate the yGap based on xMotor
#	name = yGap
#	refObj = xMotor
#	yGap = funForewardFun(xMotor)
#	xMotor = funBackward(yGap)
#
#####################################################################################

#Enable the S4 Y Gap control in micrometer
print "--> s4ygap: the S4 Y Gap control in micormeter"

s4ygap = CorrespondentDeviceClass("s4ygap", 0.0, 1000.0, "s4x","s4_x_ygap", "s4_ygap_x");
#dgap = CorrespondentDeviceClass("dgap", 0.0, 1000.0, "testMotor1","s4_x_ygap", "s4_ygap_x");

#Calculate Exit Slit S4 X negative motor position from the YGap
#input: slit gap opening (um)
#output: motor position (mm)
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
	ygap = 24.6357*math.exp(-0.04012*x**1.33062+6.00358)+242.53832*x-5956.4881+0.5*x**(0.1);
	return int(ygap);
