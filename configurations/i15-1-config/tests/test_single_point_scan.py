from gda.configuration.properties import LocalProperties
from gdascripts.parameters import beamline_parameters
from rigs_local.j15 import j15
from rigs_local.scanrequests.generic_scanrequests import collect_arc
from rigs.ispyb.discovery import showMeTheSamples
from rigs.sample import SCANNABLE_SAMPLE_NAME

def test_single_point_scan_is_not_refused():
	j15.dummy_mode = True # Do not try to move any motors (does not set dummy mode for detectors)
	j15.setVisit(LocalProperties.get('gda.defVisit')) # Use the current commissioning visit
	first_valid_sample=showMeTheSamples().keys()[0] # Any sample should do, so use the first valid sample
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	arc = jythonNameMap['arc']
	arc.dummy_mode = True # Do not try to actually run the live detector
	arc.filename = "/dls_sw/i15-1/scripts/Xpdf/ProcessingFiles/arc_sim_1_frame.hdf5"
	# Tests on the beamline (2024-11-05) failed because setting arc.calibrationFilePath to an invalid path caused
	# a file not found error.

	collect_arc(sampleid=first_valid_sample, exposure_time=10, tths=None, frames=1, monitorsPerScan=[],
				monitorsPerPoint=[],comment="",f2="auto",preSleep=None,blocking=True,samX=None)

	# Tests on the beamline (2024-11-05) failed because `collect_arc` hadn't been run in 'live' mode since the beamline
	# was powered up. This is because in dummy mode, it doesn't set up devices, to ensure processing isn't attempted.

def test_multiple_point_scan_completes():
	j15.dummy_mode = True # Do not try to move any motors (does not set dummy mode for detectors)
	j15.setVisit(LocalProperties.get('gda.defVisit')) # Use the current commissioning visit
	first_valid_sample=showMeTheSamples().keys()[0] # Any sample should do, so use the first valid sample
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	arc = jythonNameMap['arc']
	arc.dummy_mode = True # Do not try to actually run the live detector
	arc.filename = "/dls_sw/i15-1/scripts/Xpdf/ProcessingFiles/arc_sim_1_frame.hdf5"

	collect_arc(sampleid=first_valid_sample, exposure_time=10, tths=None, frames=2, monitorsPerScan=[],
				monitorsPerPoint=[],comment="",f2="auto",preSleep=None,blocking=True,samX=None)
