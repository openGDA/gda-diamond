print "<<< Entering: startup_diffractometer_euler.py ..."

from EulerianKconversionModes import EulerianKconversionModes
EKCM = EulerianKconversionModes()
EKCM.setEuleriantoKmode(1)

from diffractometer.scannable.EulerKappa import EulerKappa

euler = EulerKappa('euler',sixc)

phi = euler.phi
chi = euler.chi
eta = euler.eta
exec("mu=euler.mu")
exec("delta=euler.delta")
exec("gam=euler.gam")

import beamline_objects as BLobjects

BLobjects.my_kphi = kphi
BLobjects.my_kap = kap
BLobjects.my_kth = kth
BLobjects.my_mu = mu
BLobjects.my_delta = delta
BLobjects.my_gam = gam

euler_fly = EulerKappa('euler',sixckappa_fly)

phi_fly = euler_fly.phi
chi_fly = euler_fly.chi
eta_fly = euler_fly.eta
mu_fly = euler_fly.mu
delta_fly = euler_fly.delta
gam_fly = euler_fly.gam

print "... Leaving: startup_diffractometer_euler.py >>>"