def set_kth_minus_kdelta_max(val):
	sixckappa.getAdditionalPositionValidators()['kth_minus_kdelta_max'].setMaximumDifference(val)

def set_kgam_minus_kmu_min(val):
	sixckappa.getAdditionalPositionValidators()['kgam_minus_kmu_min'].setMinimumDifference(val)

NOMINAL_LIMITS = {
				'phi'	: (-999, 999),
				'chi'	: (-90, 99),
				'eta'	: (-22, 115),

				'mu'	: (-1, 80),
				'delta'	: (-1, 110),
				'gam'	: (-1, 120),
				'kth'	: (-90, 212),
				'kap'	: (-180, 180),
			}

if not USE_CRYO_GEOMETRY:
	NOMINAL_LIMITS['kphi'] = (-91, 271)

kgam_minus_kmu_min = -1
#kth_minus_kdelta_max_MODE1 = 80
kth_minus_kdelta_max_MODE1 = 77.5
#kth_minus_kdelta_max_MODE2 = 136

# Record same defaults from kappa axes to make non-nominal limits report complete
limits.NOMINAL_LIMITS = NOMINAL_LIMITS
NOMINAL_LIMITS['kmu'] = NOMINAL_LIMITS['mu']
NOMINAL_LIMITS['kgam'] = NOMINAL_LIMITS['gam']
NOMINAL_LIMITS['kdelta'] = NOMINAL_LIMITS['delta']

for scn_name, lower_upper_tuple in NOMINAL_LIMITS.iteritems():
	lower, upper = lower_upper_tuple
	setlm_no_offset(jythonNameMap[scn_name], lower, upper)

if not USE_CRYO_GEOMETRY:

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

else:
	print "In this cryo geometry mode choose limits as we would in the standard eulerian e2k mode of 1"
	kth_minus_kdelta_max = kth_minus_kdelta_max_MODE1

################################################################################
### put new limits in here ###

#setllm phi -900 
#setulm phi 900 
#setlm phi -900 900

#print "Setting limits for alessandro's horizontal geometry (Obtober 5th 2012)"
#setlm gam -2 130
#setlm chi 89.9 90.1
#setlm eta -0.1 0.1
#setlm delta -1 9
#setulm mu 60
#kgam_minus_kmu_min = -3

################################################################################
# DO NOT REMOVE THESE TWO LINES!
################################################################################

set_kth_minus_kdelta_max(kth_minus_kdelta_max)
set_kgam_minus_kmu_min(kgam_minus_kmu_min)

################################################################################

# 17/04//2018 delta limit with new s6 on long nose cone is  ~ 127 

setlm_kth_minus_kdelta_max=set_kth_minus_kdelta_max
setlm_kgam_minus_kmu_min=set_kgam_minus_kmu_min

alias('setlm_kth_minus_kdelta_max')
alias('setlm_kgam_minus_kmu_min')
