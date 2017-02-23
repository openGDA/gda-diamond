
import math;
from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass

print "Enable the Gap control of I06 Exit Slits S6";
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

s6ygap = CorrespondentDeviceClass("s6ygap", 0.0, 600.0, "s6x","s6_x_ygap", "s6_ygap_x");
#d6gap = CorrespondentDeviceClass("d6gap", 0.0, 600.0, "testMotor1","s6_x_ygap", "s6_ygap_x");

#Calculate Exit Slit S6 X negative motor position from the YGap
#input: slit gap opening (um)
#output: motor position (mm)
def s6_ygap_x(ygap):
	P0=-11.3;
	P1=0.01981163532855246;
	P2=-1.235075318082776E-4;
	P3=8.736225481365102E-7;
	P4=-4.402213559853138E-9;
	P5=1.487234101245926E-11;
	P6=-3.273842881640236E-14;
	P7=4.480457493471113E-17;
	P8=-3.447980817661539E-20;
	P9=1.137118178582843E-23;
	x = P0+P1*ygap+P2*ygap**2+P3*ygap**3+P4*ygap**4+P5*ygap**5+P6*ygap**6+P7*ygap**7+P8*ygap**8+P9*ygap**9;
	return x;

#Calculate Exit Slit S6 YGap from the X negative motor position
#input: motor position (mm)
#output: slit gap opening (um)
def s6_x_ygap(x):
	P0=-2484408.817699331;
	P1=-2644304.601890175;
	P2=-1243635.012222395;
	P3=-339424.8327910707;
	P4=-59249.54314690326;
	P5=-6859.428822203713;
	P6=-526.6605665631911;
	P7=-25.85873899355000;
	P8=-0.7367467452420894;
	P9=-0.00928053156668320;
	ygap =P0+P1*x+P2*x**2+P3*x**3+P4*x**4+P5*x**5+P6*x**6+P7*x**7+P8*x**8+P9*x**9;
	return round(ygap,0);
