raise DeprecationWarning("This script is no longer supported (as of November 2018) and should not be used")

from time import sleep


from Diamond.PseudoDevices.DiffractometerDevices import DiffractometerModeClass, DiffractometerAxisClass;

"""
	I07 diffractometer mode setting:
	mode in "Horizontal" or 0:
		alpha = diff1halpha;
		delta = diff1vgamma;
		gamma = diff1vdelta; 
		omega = diff1homega;
		chi = diff1cchi;
		phi = diff1cphi;
		
	mode in "Vertical" or 1:
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
"""

exec("diff1mode, alpha, delta, gamma, omega, chi, phi = None, None, None, None, None, None, None");

diff1mode = DiffractometerModeClass('diff1mode', CDIFF1);

alpha = DiffractometerAxisClass('alpha', diff1halpha, diff1valpha, dummyAlpha);
delta = DiffractometerAxisClass('delta', diff1vgamma, diff1vdelta, dummyDelta);
gamma = DiffractometerAxisClass('gamma', diff1vdelta, diff1vgamma, dummyGamma);
omega = DiffractometerAxisClass('omega', diff1homega, diff1vomega, dummyOmega);
chi = DiffractometerAxisClass('chi', diff1cchi, diff1cchi, dummyChi);
phi = DiffractometerAxisClass('phi', diff1cphi, diff1cphi, dummyPhi);

CDIFF1.addGroupMember(alpha);
CDIFF1.addGroupMember(delta);
CDIFF1.addGroupMember(gamma);
CDIFF1.addGroupMember(omega);
CDIFF1.addGroupMember(chi);
CDIFF1.addGroupMember(phi);

CDIFF1.addGroupMember(diff1mode);

diff1mode.setMode(DiffractometerModeClass.VERTICAL);


print
print "===================================================================";
print "Diffractometer1 setup using DiffCalc"

# Currently configured to create dummy axes alpha, delta, gamma, omega, chi, phi.
#execfile(gdaScriptDir + "BeamlineI07/sixcircle_dummy.py");

execfile(gdaScriptDir + "BeamlineI07/sixcircle_i07.py");
#execfile(gdaScriptDir + "BeamlineI07/sixcircle_dummy.py");
