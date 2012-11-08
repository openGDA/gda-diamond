def check_finepitch():
	while ic1()<0.1:
		pos w 10
	fp0 = finepitch()
	scan finepitch (fp0-20) (fp0+20) 1 ic1 vpos w .1
	peak = FindScanCentroid('IC1','finepitch')
	finepitch(peak['finepitch'])
	print 'old finepitch:', fp0
	print 'new finepitch:', peak['finepitch']
