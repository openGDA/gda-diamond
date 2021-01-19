from abstract import abstract


class DetectorWrapperBase:
	
	def __init__(self, detector, beamXYConverter):
		self.detector = detector
		self.beamXYConverter = beamXYConverter
	
	####################################################################################################################
	### Threshold
	####################################################################################################################
	
	def set_threshold(self, handler, energy):
		abstract()
	
	def create_set_threshold_thread(self, handler, new_energy, differenceThreshold):
		abstract()
	
	####################################################################################################################
	### Beam position
	####################################################################################################################
	
	def getBeamPositionMm(self, detector_distance):
		
		xBeamMM = self.beamXYConverter.getBeamXUsingMM(detector_distance)
		yBeamMM = self.beamXYConverter.getBeamYUsingMM(detector_distance)
		
		return (xBeamMM, yBeamMM)
	
	def getBeamPositionPixels(self, detector_distance):
		
		detectorXSize = self.detector.getSizeX()
		detectorYSize = self.detector.getSizeY()
		
		detectorDimensionInMm = self.detector.getDimensionInMm()
		
		xBeamPixels = self.beamXYConverter.getBeamXUsingPixels(detector_distance, detectorXSize, detectorDimensionInMm.getWidth())
		yBeamPixels = self.beamXYConverter.getBeamYUsingPixels(detector_distance, detectorYSize, detectorDimensionInMm.getHeight())
		
		return (xBeamPixels, yBeamPixels)
	
	####################################################################################################################
	### Recovery
	####################################################################################################################
	
	def reset_after_error(self, handler, visitPath=None):
		abstract()


class DataCollectionDetectorWrapperBase:
	
	def check_detector_before_requests(self):
		abstract()
	
	def prepare_for_request(self, handler, extendedRequest, wavelength, flux, transmission, delayTime, gonio_rotation_vector, data_collection_id):
		abstract()
	
	def prepare_for_oscillation(self, handler, oscillation, osc_axis):
		abstract()
	
	def start_before_oscillation(self):
		abstract()
	
	def check_detector_before_image(self, handler):
		abstract()
	
	def prepare_for_image(self, handler, oscillation, start_image_num, start_angle):
		abstract()
	
	def start_before_image(self):
		abstract()
	
	def after_image(self, handler, start_image_num):
		abstract()
	
	def after_oscillation(self):
		abstract()


class GridScanDetectorWrapperBase:
	
	def at_scan_start(self, handler, mode, exposureTime, wavelength, detector_distance, directory, prefix, delayTime, omega, transmissionInPercent, flux, osc_axis, gonio_rotation_vector, data_collection_id, omega_increment):
		abstract()
	
	###########################################################################
	
	def multi_sweep_before_all_rows_or_columns(self, num_sweeps, images_per_sweep):
		abstract()
	
	def multi_sweep_start_before_all_rows_or_columns(self):
		abstract()
	
	def multi_sweep_before_row_or_column(self, startImageNumber, numImages):
		abstract()
	
	def multi_sweep_start_before_row_or_column(self):
		abstract()
	
	def multi_sweep_after_row_or_column(self, handler, startImageNumber):
		abstract()
	
	def multi_sweep_after_all_rows_or_columns(self):
		abstract()
	
	###########################################################################
	
	def single_sweep_before_sweep(self, startImageNumber, numImages):
		abstract()
	
	def single_sweep_start_before_sweep(self):
		abstract()
	
	def single_sweep_after_sweep(self):
		abstract()


class LineScanDetectorWrapperBase:
	
	def at_scan_start(self, handler, num_wedges, images_per_wedge, exposure_time, detector_distance, wavelength, angle_range, directory, prefix, delay_time, transmission_percent, flux, gonio_rotation_vector, data_collection_id):
		abstract()
	
	###########################################################################
	
	def wedged_start_before_all_wedges(self):
		abstract()
	
	def wedged_at_wedge_start(self, image_number, start_angle):
		abstract()
	
	def wedged_start_before_wedge(self):
		abstract()
	
	def wedged_at_wedge_end(self, handler, image_number):
		abstract()
	
	def wedged_after_all_wedges(self):
		abstract()
	
	###########################################################################
	
	def helical_at_wedge_start(self, image_number, start_angle):
		abstract()
	
	def helical_start_before_wedge(self):
		abstract()
	
	def helical_at_wedge_end(self, handler, image_number):
		abstract()
