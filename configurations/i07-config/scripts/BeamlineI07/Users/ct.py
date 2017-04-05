def ct(integrationTime = 0):
	if integrationTime == 0:
		integrationTime = ct.defaultTime
	if ct.specWarning:
		print "This is not SPEC!"
	pos(fs, 1)
	sleep(ct.fsSleep)
	pos(ct.detector, integrationTime)
	pos(fs, 0)
	print "Sum: " + str(ct.detector.readout()[10]) + "  Max: " + str(ct.detector.readout()[7]) + " (" + str(ct.detector.readout()[6]) + "," + str(ct.detector.readout()[5]) + ") Filename: " + ct.detector.filename
ct.detector = pil1stats
ct.specWarning = False
ct.defaultTime = 1
ct.fsSleep = 0.5
alias("ct")
