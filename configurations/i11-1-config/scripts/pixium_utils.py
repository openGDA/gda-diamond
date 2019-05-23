from gdaserver import pixium_hdf

# {mode: (base exposure, base period)}
DEFAULT_EXPOSURES = {1: (1.0, 1.25)}

def checkPixiumMode(mode):
	"""
	Check the pixium_hdf detector is in the given mode

	and change mode and calibrate if not.
	"""
	if pixium_hdf.PUMode != mode:
		print 'Changing Pixium to mode %d' %mode
		pixium_hdf.PUMode = mode
		if mode in DEFAULT_EXPOSURES:
			exposure, period = DEFAULT_EXPOSURES[mode]
			pixium_hdf.baseExposure = exposure
			pixium_hdf.baseAcquirePeriod = period
		pixium_hdf.calibrate()
