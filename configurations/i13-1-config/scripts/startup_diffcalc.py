###
# Start up Diffcalc for I13
###

if not 'en' in globals():
	en=qcm_energy
	print "Set 'en' as synonym for 'qcm_energy'"

print 'Running fivecircle example'
run('example/fivecircle')
