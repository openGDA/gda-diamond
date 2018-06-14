# Before taking a snapshot for setting up processing, there must be an image in the appropriate detector's array.
# This script ensures that this is done for each detector at startup.

from gda.epics import CAClient
from i14_utilities import isLive

def caput(pv, val):
	CAClient.put(pv, val)

def caget(pv):
	return CAClient.get(pv)

def add_colon_if_necessary(pv):
	if pv.endswith(':'):
		return pv
	return pv + ':'

def prepare_detector(detector_name, ad_base_pv, ndarray_base_pv, trigger_mode, image_mode):
	"""
	Parameters:
		detector_name: name of detector to use in status and error messages
		addetector: addetector object for the detector
		trigger_mode: value of the trigger mode required to acquire data in this way. Normally Software or Internal.
		image_mode: value of the image mode required to acquire data in this way. Normally Single or Fixed.
	"""
	ad_base_pv_norm = add_colon_if_necessary(ad_base_pv)
	ndarray_base_pv_norm = add_colon_if_necessary(ndarray_base_pv)

	try:
		# Do nothing if the detector is already acquiring
		if caget(ad_base_pv_norm + 'Acquire_RBV') == 'Acquiring':
			print('Detector {} is already acquiring: no initialisation required'.format(detector_name))
			return

		# Enable callbacks in the array plugin, then acquire a single frame
		print('Initialising array plugin for {}: ad_base_pv = {} ndarray_base_pv = {}'.format(detector_name, ad_base_pv_norm, ndarray_base_pv_norm))
		caput(ndarray_base_pv_norm + "EnableCallbacks", "Enable")

		# set trigger mode to software
		prev_trigger_mode = caget(ad_base_pv_norm + "TriggerMode")
		trigger_mode_changed = prev_trigger_mode != trigger_mode
		if (trigger_mode_changed):
			caput(ad_base_pv_norm + "TriggerMode", trigger_mode)

		# set image mode to single
		prev_img_mode = caget(ad_base_pv_norm + "ImageMode")
		image_mode_changed = prev_img_mode != image_mode
		if (image_mode_changed):
			caput(ad_base_pv_norm + "ImageMode", image_mode)

		# acquire single frame
		caput(ad_base_pv_norm + "Acquire", "Acquire")

		# restore trigger and image mode if necessary
		if (trigger_mode_changed):
			caput(ad_base_pv_norm + "TriggerMode", prev_trigger_mode)
		if (image_mode_changed):
			caput(ad_base_pv_norm + "ImageMode", prev_img_mode)

	except:
		print('Error preparing detector {}'.format(detector_name))

def prepare_detectors():
	from gdaserver import xsp3_addetector, xreye_addetector
	print('Initialising detectors...')
	if isLive():
		prepare_detector("Excalibur", "BL14I-EA-EXCBR-01:CONFIG:ACQUIRE", "BL14I-EA-EXCBR-01:MASTER:ARR", "Internal", "Single")
		prepare_detector("Xspress3", xsp3_addetector.getAdBase().getBasePVName(), xsp3_addetector.getNdArray().getBasePVName(), "Software", "Single")
		prepare_detector("Xray Eye", xreye_addetector.getAdBase().getBasePVName(), xreye_addetector.getNdArray().getBasePVName(), "Internal", "Fixed")
	else:
		prepare_detector("Simulator", xreye_addetector.getAdBase().getBasePVName(), xreye_addetector.getNdArray().getBasePVName(), "Internal", "Single")
	print('Detector initialisation complete')
