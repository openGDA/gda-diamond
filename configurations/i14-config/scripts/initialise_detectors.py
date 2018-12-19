# Before taking a snapshot for setting up processing, there must be an image in the appropriate detector's array.
# This script ensures that this is done for each detector at startup.

from i14_utilities import isLive
from gdascripts.detectors.initialise_detector import initialise_detector

def initialise_detectors():
	from gdaserver import xsp3_addetector, xreye_addetector, merlin_addetector
	print('Initialising detectors...')
	if isLive():
		initialise_detector("Excalibur", "BL14I-EA-EXCBR-01:CONFIG:ACQUIRE", "BL14I-EA-EXCBR-01:MASTER:ARR", "Internal", "Single")
		initialise_detector("Merlin", merlin_addetector.getAdBase().getBasePVName(), merlin_addetector.getNdArray().getBasePVName(), "Software", "Single")
		initialise_detector("Xspress3", xsp3_addetector.getAdBase().getBasePVName(), xsp3_addetector.getNdArray().getBasePVName(), "Software", "Single")
		initialise_detector("Xray Eye", xreye_addetector.getAdBase().getBasePVName(), xreye_addetector.getNdArray().getBasePVName(), "Internal", "Fixed")
	else:
		initialise_detector("Simulator", xreye_addetector.getAdBase().getBasePVName(), xreye_addetector.getNdArray().getBasePVName(), "Internal", "Single")
	print('Detector initialisation complete')
