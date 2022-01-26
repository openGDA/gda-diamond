from gda.device.detector import NXDetectorDataWithFilepathForSrs

def ct(integrationTime = 0):
	if integrationTime == 0:
		integrationTime = ct.defaultTime
	if ct.specWarning:
		print "This is not SPEC!"
	pos(fs, 1)
	sleep(ct.fsSleep)
	pos(ct.detector, integrationTime)
	pos(fs, 0)
	detectorReadout = ct.detector.readout()
	if isinstance(detectorReadout, NXDetectorDataWithFilepathForSrs):
		detectorReadout = detectorReadout.toString().split('\t')

	print "Sum: " + str(detectorReadout[10]) + "  Max: " + str(detectorReadout[7]) + " (" + str(detectorReadout[6]) + "," + str(detectorReadout[5]) + ") Filename: " + ct.detector.filename
ct.detector = pil1stats
ct.specWarning = False
ct.defaultTime = 1
ct.fsSleep = 0.5
alias("ct")
