from gda.configuration.properties import LocalProperties
from i15x.j15 import beamline as j15
#from rigs.j15.arc_scanrequests import do_arc_datacollections
from rigs.j15.hybrid_scanrequests import do_hybrid_datacollections
from rigs.ispyb.discovery import showMeTheSamples

# Test based on testOldScanning() in /dls_sw/i15-1/scripts/Visits/arc_testing_01.py

def test_single_point_scan_is_not_refused():
	# Do not try to move any motors
	j15.dummy_mode = True
	# Use the current commissioning visit
	j15.setVisit(LocalProperties.get('gda.defVisit'))
	# Any sample should do, so use the first valid sample
	first_valid_sample=showMeTheSamples().keys()[0]
	do_hybrid_datacollections(first_valid_sample, frames=1,
		pe1_time=10, pe2_time=None, samx=None, blocking=True, comment="test")
