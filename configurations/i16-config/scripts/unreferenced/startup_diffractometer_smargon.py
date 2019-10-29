print "<<< Entering: startup_diffractometer_euler.py ..."

#from EulerianKconversionModes import EulerianKconversionModes
#EKCM = EulerianKconversionModes()
#mode e2k 1

#from diffractometer.scannable.EulerKappa import EulerKappa

#euler = EulerKappa('euler',sixc)


phi = euler.phi
chi = euler.chi 
eta = euler.eta
exec("mu=euler.mu")
exec("delta=euler.delta")
exec("gam=euler.gam")
print "... Leaving: startup_diffractometer_euler.py >>>"

import beamline_objects as BLobjects

BLobjects.my_kphi = kphi
BLobjects.my_kap = kap
BLobjects.my_kth = kth
BLobjects.my_mu = mu
BLobjects.my_delta = delta
BLobjects.my_gam = gam

BLobjects.my_mu = mu
BLobjects.my_delta = delta
BLobjects.my_gam = gam
