print
print "Applying configured limits:"
print


print "   ", '%4i'%kphi_low, " <= kphi <=", kphi_high
print "   ", '%4i'%kap_low, " <= kap <=", kap_high
print "   ", '%4i'%kth_low, " <= kth <=", kth_high
print "   ", '%4i'%gam_low, " <= gam <=", gam_high
print "   ", '%4i'%mu_low, " <= mu <=", mu_high
print "   ", '%4i'%delta_no_offset_low, " <= delta_no_offset <=", delta_no_offset_high
print
print "   ", '%4i'%phi_low, " <= phi <=", phi_high
print "   ", '%4i'%chi_low, " <= chi <=", chi_high
print "   ", '%4i'%eta_low, " <= eta <=", eta_high
print
print "             kth-kdelta <=", kth_minus_kdelta_max
print "    ", '%4i'%kgam_minus_kmu_min, "<= kgam-kmu"

kphi.setUpperGdaLimits(kphi_high)
kphi.setLowerGdaLimits(kphi_low)

kap.setUpperGdaLimits(kap_high)
kap.setLowerGdaLimits(kap_low)

kth.setUpperGdaLimits(kth_high)
kth.setLowerGdaLimits(kth_low)

gam.setUpperGdaLimits(gam_high)
gam.setLowerGdaLimits(gam_low)

mu.setUpperGdaLimits(mu_high)
mu.setLowerGdaLimits(mu_low)

euler.setUpperGdaLimits([phi_high,chi_high,eta_high,mu_high, None, gam_high])
euler.setLowerGdaLimits([phi_low,chi_low,eta_low,mu_low, None, gam_low])
kdelta_offset_value = kdelta.getOffset()[0] if kdelta.getOffset()!=None else 0.
kdelta.setUpperGdaLimits(delta_no_offset_high + kdelta_offset_value)
kdelta.setLowerGdaLimits(delta_no_offset_low + kdelta_offset_value)

phi.setUpperGdaLimits(phi_high)
phi.setLowerGdaLimits(phi_low)

chi.setUpperGdaLimits(chi_high)
chi.setLowerGdaLimits(chi_low)

eta.setUpperGdaLimits(eta_high)
eta.setLowerGdaLimits(eta_low)

sixckappa.getAdditionalPositionValidators()['kth_minus_kdelta_max'].setMaximumDifference(kth_minus_kdelta_max)
sixckappa.getAdditionalPositionValidators()['kgam_minus_kmu_min'].setMinimumDifference(kgam_minus_kmu_min)
