###
# Start up Diffcalc for I13
###

if not 'en' in globals():
	en=qcm_energy
	print "Set 'en' as synonym for 'qcm_energy'"

print 'Running fivecircle example'
run('example/fivecircle')

setmax(delta, 24)

setmin(delta, -1)

setmin(gam, 0)

setmax(gam, 15)

setmin(eta, -10)

setmax(eta, 10)

setmin(chi, 75)

setmax(chi, 105)

setmin(phi, -88)

setmax(phi, 88)

hardware()
