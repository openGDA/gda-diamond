
execfile("C:\Dev\gdaConfig\i06\scripts\enableCorrespondentDevice.py");

y=CorrespondentDeviceClass("y", 0, 10, "motor1", "s4_x_ygap2", "s4_ygap_x2");


def s4_ygap_x2(ygap):
	#convert targetenergy and timedelay to float numbers
#	x = 14.5006 -0.01368*ygap +3.62863E-5*ygap**2 -1.20877E-7*ygap**3 +3.10277E-10*ygap**4  -5.53949E-13*ygap**5  +6.55968E-16*ygap**6 -4.87657E-19*ygap**7 +2.05093E-22*ygap**8 -3.71121E-26*ygap**9
	x = ygap*ygap;
	return x;

def s4_x_ygap2(x):
#	ygap = sqrt(x);
	ygap = x**0.5;
	return ygap;
