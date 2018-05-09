###
# Start up Diffcalc for I13
###
from gdascripts.scannable.dummy import SingleInputDummy as Dummy

if not 'en' in globals():
	# en=qcm_energy
	# print "Set 'en' as synonym for 'qcm_energy'"
	en = Dummy('en')
	en(9.35)
	print "Creating Dummy en scannable and setting energy to 9.35 keV"

	



print 'Running startup/i13'
# For 2.0 branch
run('startup/i13')


