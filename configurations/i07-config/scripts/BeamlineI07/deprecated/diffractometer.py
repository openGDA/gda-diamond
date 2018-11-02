raise DeprecationWarning("This script is no longer supported (as of November 2018) and should not be used")

from time import sleep


from Diamond.PseudoDevices.DiffractometerDevices import DiffractometerModeClass, DiffractometerAxisClass;

"""
	I07 diffractometer mode setting:
	mode in "diff1 Horizontal" or 0:
		alpha = diff1halpha;
		delta = diff1vgamma;
		gamma = diff1vdelta; 
		omega = diff1homega;
		chi = diff1cchi;
		phi = diff1cphi;
		
	mode in "diff1 Vertical" or 1:
		alpha = diff1valpha;
		delta = diff1vdelta;
		gamma = diff1vgamma; 
		omega = diff1vomega;
		chi = diff1cchi;
		phi = diff1cphi;

	mode in "Dummy" or 2:
		alpha = dummyAlpha;
		delta = dummyDelta;
		gamma = dummyGamma; 
		omega = dummyOmega;
		chi = dummyChi;
		phi = dummyPhi;

	mode in "EH2DIFF " or 3:
		alpha = diff2alpha;
		delta = diff2delta;
		gamma = diff2gamma; 
		omega = diff2omega;
		chi = dummyChi;
		phi = dummyPhi;

"""

exec("diff1mode, alpha, delta, gamma, omega, chi, phi = None, None, None, None, None, None, None");

diffmode = DiffractometerModeClass('diffmode', DIFF);

alpha = DiffractometerAxisClass('alpha', diff1halpha, diff1valpha, dummyAlpha, diff2alpha);
delta = DiffractometerAxisClass('delta', diff1vgamma, diff1vdelta, dummyDelta, diff2delta);
gamma = DiffractometerAxisClass('gamma', diff1vdelta, diff1vgamma, dummyGamma, diff2gamma);
omega = DiffractometerAxisClass('omega', diff1homega, diff1vomega, dummyOmega, diff2omega);
chi = DiffractometerAxisClass('chi', diff1cchi, diff1cchi, dummyChi, dummyChi);
phi = DiffractometerAxisClass('phi', diff1cphi, diff1cphi, dummyPhi, dummyPhi);

DIFF.addGroupMember(alpha);
DIFF.addGroupMember(delta);
DIFF.addGroupMember(gamma);
DIFF.addGroupMember(omega);
DIFF.addGroupMember(chi);
DIFF.addGroupMember(phi);

DIFF.addGroupMember(diffmode);

diffmode.setMode(DiffractometerModeClass.VERTICAL);


print
print "===================================================================";
print "Diffractometer1 setup using DiffCalc"

# Currently configured to create dummy axes alpha, delta, gamma, omega, chi, phi.
#execfile(gdaScriptDir + "BeamlineI07/sixcircle_dummy.py");

execfile(gdaScriptDir + "BeamlineI07/sixcircle_i07.py");
#execfile(gdaScriptDir + "BeamlineI07/sixcircle_dummy.py");
