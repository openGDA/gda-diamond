from gda.configuration.properties import LocalProperties
from gdascripts.parameters import beamline_parameters
from rigs_local.j15 import j15
from rigs_local.scanrequests.generic_scanrequests import collect_pe2

def test_single_point_scan_is_not_refused():
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	robot=jythonNameMap['robot']
	real_janet=jythonNameMap['real_janet']

	j15.dummy_mode = True # Do not try to move any motors (does not set dummy mode for detectors)
	robot.dummy_mode = True
	real_janet.dummy_mode = True

	j15.setVisit(LocalProperties.get('gda.defVisit')) # Use the current commissioning visit

	collect_pe2(sampleid="bkg", exposure_time=9, frames=1,
				monitorsPerPoint=[],comment="",f2="auto",preSleep=None,blocking=True,samX=None)

def test_multiple_point_scan_completes():
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	robot=jythonNameMap['robot']
	real_janet=jythonNameMap['real_janet']
	pe2 = jythonNameMap['pe2']
	i0 = jythonNameMap['i0']

	j15.dummy_mode = True # Do not try to move any motors (does not set dummy mode for detectors)
	robot.dummy_mode = True
	real_janet.dummy_mode = True
	pe2.stopBetweenPoints = False
	i0.stopBetweenPoints = False

	j15.setVisit(LocalProperties.get('gda.defVisit')) # Use the current commissioning visit

	collect_pe2(sampleid="bkg", exposure_time=9, frames=2,
				monitorsPerPoint=[],comment="",f2="auto",preSleep=None,blocking=True,samX=None)
