print "<<< Entering: startup_diffractometer_euler.py ..."

from EulerianKconversionModes import EulerianKconversionModes
EKCM = EulerianKconversionModes()
EKCM.setEuleriantoKmode(1)

from diffractometer.scannable.EulerKappa import EulerKappa

euler = EulerKappa('euler',sixc, False)

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

euler_fly = EulerKappa('euler',sixckappa_fly, True)

phi_fly = euler_fly.phi_fly
chi_fly = euler_fly.chi_fly
eta_fly = euler_fly.eta_fly
mu_fly = euler_fly.mu_fly
delta_fly = euler_fly.delta_fly
gam_fly = euler_fly.gam_fly

print "... Leaving: startup_diffractometer_euler.py >>>"