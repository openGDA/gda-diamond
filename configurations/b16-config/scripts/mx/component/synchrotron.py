from gda.factory import Finder
from gda.device.epicsdevice import ReturnType
from gda.configuration.properties.LocalProperties import isDummyModeEnabled

# To see the mode names:
#   $ caget -d 31 CS-CS-MSTAT-01:MODE

SHUTDOWN = "Shutdown"
INJECTION = "Injection"
NO_BEAM = "No Beam"
MACH_DEV = "Mach. Dev."
USER = "User"
SPECIAL = "Special"
BL_STARTUP = "BL Startup"

mode_names = (SHUTDOWN, INJECTION, NO_BEAM, MACH_DEV, USER, SPECIAL, BL_STARTUP)

def _get_ring_device():
	ring = Finder.find("Ring")
	return ring

def get_beam_mode_name():
	if isDummyModeEnabled():
		return USER
	else:
		ring = _get_ring_device()
		synchrotron_mode_value = ring.getValueAsString("BeamMode","")
		return synchrotron_mode_value

def get_ring_current():
	if isDummyModeEnabled():
		return 250.0
	else:
		ring = _get_ring_device()
		ring_current_value = ring.getValue(ReturnType.DBR_NATIVE,"Current","")
		return ring_current_value

def seconds_to_topup():
	if isDummyModeEnabled():
		return 180
	else:
		ring = _get_ring_device()
		seconds_to_topup = ring.getValue(ReturnType.DBR_NATIVE,"TimeUntilRefill","")
		return seconds_to_topup
