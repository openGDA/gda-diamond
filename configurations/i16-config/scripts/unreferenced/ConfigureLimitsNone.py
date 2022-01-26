# Set default limits on some scannables.
# These limits are not yet persistant and will not be remembered across gda restarts unless they are set here.

# ************************************************************
# **************** EDIT LIMITS IN HERE PLEASE ****************
# ************************************************************

# Raw Motors
kphi_low  = None
kphi_high = None

kap_low  = None
kap_high = None

kth_low  = None
kth_high = None

delta_low  = None
delta_high = None

gam_low  = None
gam_high = None

# Eulerian Axis
eta_low  = None
eta_high = None

phi_low  = None
phi_high = None

chi_low  = None
chi_high = None


# ************************************************************
# ************************************************************
# Raw Motors
kphi.setUpperScannableLimits(kphi_high)
kphi.setLowerGdaLimits(kphi_low)

kap.setUpperScannableLimits(kap_high)
kap.setLowerGdaLimits(kap_low)

kth.setUpperScannableLimits(kth_high)
kth.setLowerGdaLimits(kth_low)

delta.setUpperScannableLimits(delta_high)
delta.setLowerGdaLimits(delta_low)

gam.setUpperScannableLimits(gam_high)
gam.setLowerGdaLimits(gam_low)

#mu limit needs fixing
#mu.setUpperLimits(mu_high)
#mu.setLowerLimits(mu_low)

euler.setUpperScannableLimits([phi_high,chi_high,eta_high])
euler.setLowerGdaLimits([phi_low,chi_low,eta_low])

phi.setUpperScannableLimits(phi_high)
phi.setLowerGdaLimits(phi_low)

eta.setUpperScannableLimits(eta_high)
eta.setLowerGdaLimits(eta_low)

chi.setUpperScannableLimits(chi_high)
chi.setLowerGdaLimits(chi_low)
