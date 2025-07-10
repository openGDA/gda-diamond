from gda.factory import Finder
from gdascripts.utils import caget
from gda.configuration.properties import LocalProperties

ringCurrentThreshold = 50.0

def checkForBeamlineProblems():
	if LocalProperties.get("gda.mode")=="dummy":
		print "Skip checking beamline problems for dummy mode"
		return 0

	try:
		FE_status = int(caget('FE05I-CS-BEAM-01:STA'))
	except:
		print "Fetching FE shutter status failed, Skipping all remaining checks in checkForBeamlineProblems"
		return -1

	if (FE_status != 1):
		print "FE shutter status is NOT OPEN"
		return 2

	try:
		OP_status = int(caget('FE05I-PS-SHTR-02:STA'))
	except:
		print "Fetching Optics shutter status failed, Skipping all remaining checks in checkForBeamlineProblems"
		return -1

	if (FE_status != 1):
		print "Optics shutter status is NOT OPEN"
		return 2

	ringCurrent = Finder.find("ring_current")
	if (ringCurrent==None):
		print "Ring current scannable not found! Skipping all remaining checks in checkForBeamlineProblems"
		return -1

	if (float(ringCurrent.getPosition())<ringCurrentThreshold):
		print "Ring current less than %.1f mA" % ringCurrentThreshold
		return 1

	print "FE and Optics shutters are open, ring current more than %.1f mA" % ringCurrentThreshold
	return 0