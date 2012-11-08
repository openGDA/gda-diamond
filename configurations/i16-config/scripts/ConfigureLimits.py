

import limits
reload(limits)
from limits import * #@UnusedWildImport
limits.ROOT_NAMESPACE = globals()

NOMINAL_LIMITS = {phi : (-999, 999),
				chi : (-90, 99),
				eta : (-22, 115),
				
				mu : (-1, 80),
				delta : (-1, 130),
				gam : (-1, 120),
				kphi : (-91, 271),
				kth : (-90, 212),
				kap: (-180, 180),
				}

# Record same defaults from kappa axes to make non-nominal limits report complete
limits.NOMINAL_LIMITS = NOMINAL_LIMITS
NOMINAL_LIMITS[kmu] = NOMINAL_LIMITS[mu]
NOMINAL_LIMITS[kgam] = NOMINAL_LIMITS[gam]
NOMINAL_LIMITS[kdelta] = NOMINAL_LIMITS[delta]

for scn, lower_upper_tuple in NOMINAL_LIMITS.iteritems():
	lower, upper = lower_upper_tuple
	setlm_no_offset(scn, lower, upper)

################################################################################
### put new limits in here ###

#setllm phi -900 
#setulm phi 900 
#setlm phi -900 900

kgam_minus_kmu_min = -11
kth_minus_kdelta_max_MODE1 = 80
kth_minus_kdelta_max_MODE2 = 136
################################################################################
################################################################################



if EKCM.getEuleriantoKmode() == 1:
	print "e2k mode is 1: This is the standard vertical mode of the diffractometer"
	print "               The kappa counter weight is upstream with kth=0"
	print
	print "Setting appropriate limits:"
	kth_minus_kdelta_max = kth_minus_kdelta_max_MODE1 ###check this one
	print "   kth_minus_kdelta_max:", kth_minus_kdelta_max

elif EKCM.getEuleriantoKmode() == 2:
	print "e2k mode is 2: This is a special, infrequently used, vertical mode of the diffractometer"
	print "               The kappa counter weight is downstream with kth=0"
	print "Setting appropriate limits"
	kth_minus_kdelta_max = kth_minus_kdelta_max_MODE2 ###check this one
	print "   kth_minus_kdelta_max:", kth_minus_kdelta_max

sixckappa.getAdditionalPositionValidators()['kth_minus_kdelta_max'].setMaximumDifference(kth_minus_kdelta_max)
sixckappa.getAdditionalPositionValidators()['kgam_minus_kmu_min'].setMinimumDifference(kgam_minus_kmu_min)



