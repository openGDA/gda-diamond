import base
from gda.px.detector import PilatusDetectorCollectionParameters
from PilatusScripts import getDetectorWriteFilepath
from PilatusScripts import clearPilatusLastImage
from PilatusScripts import PilatusCheckThreshold
from PilatusScripts import PilatusThresholdAndGainThread
from PilatusScripts import checkPilatusFilenumberUpdate
from gda.px import MxProperties
from gda.px.detector import DetectorStatus

FILE_NUMBER_UPDATE_TIMEOUT = 10


class PilatusDetectorWrapper(base.DetectorWrapperBase):
	
	def __init__(self, detector, beamXYConverter, template_writer):
		base.DetectorWrapperBase.__init__(self, detector, beamXYConverter)
		self.template_writer = template_writer
	
	####################################################################################################################
	### Threshold
	####################################################################################################################
	
	def set_threshold(self, handler, energy):
		PilatusCheckThreshold(self.detector, energy, handler.update)
	
	def create_set_threshold_thread(self, handler, new_energy, differenceThreshold):
		
		pilatusDiff = abs(self.detector.getThresholdEnergy() * 2 - new_energy)
		
		changeThreshold = (pilatusDiff > differenceThreshold)
		
		if changeThreshold:
			
			pilatusThread = PilatusThresholdAndGainThread(self.detector, new_energy, handler.log)
			return pilatusThread
		
		return None
	
	####################################################################################################################
	### Miscellaneous
	####################################################################################################################
	
	def handleDetectorErrorStatus(self):
		
		if self.detector.getDetectorStatus().getValue() == DetectorStatus.ERROR:
			raise Exception("Detector in an error state")
	
	def waitUntilDetectorReady(self, handler):
		
		handler.update("Checking whether detector is ready")
		self.detector.waitForReady()
		handler.update("Detector is ready")
	
	####################################################################################################################
	### Recovery
	####################################################################################################################
	
	def reset_after_error(self, handler, visitPath=None):
		clearPilatusLastImage(self.detector, handler.update, visitPath)


class PilatusDataCollectionDetectorWrapper(PilatusDetectorWrapper, base.DataCollectionDetectorWrapperBase):
	
	def check_detector_before_requests(self):
		
		self.handleDetectorErrorStatus()
	
	def prepare_for_request(self, handler, extendedRequest, wavelength, flux, transmission, delayTime, gonio_rotation_vector, data_collection_id):
		
		(xBeamPixels, yBeamPixels) = self.getBeamPositionPixels( extendedRequest.getSampleDetectorDistanceInMM() )
		
		actualFilepath = getDetectorWriteFilepath(extendedRequest.requestDir)
		
		params = PilatusDetectorCollectionParameters()
		
		params.setWavelength(wavelength)
		params.setSampleDetectorDistance( extendedRequest.getSampleDetectorDistanceInMM() )
		params.setDetectorVOffset(0)
		params.setPolarization(0.99)
		params.setBeamX(xBeamPixels)
		params.setBeamY(yBeamPixels)
		params.setTransmission(transmission)
		params.setFlux(flux)
		params.setPhiIncrement(0)
		params.setChi(0)
		params.setChiIncrement(0)
		
		params.setKappa(extendedRequest.kappa if extendedRequest.hasMiniKappaAngles() else 0)
		params.setChi(extendedRequest.chi if extendedRequest.hasSmarGonAngles() else 0)
		params.setPhi(extendedRequest.phi if extendedRequest.hasMiniKappaAngles() or extendedRequest.hasSmarGonAngles() else 0)
		
		self.detector.sendParameters(params)  # use sendParameters so that the exposure time/period do not get changed
		
		self.detector.setFilepath(actualFilepath)
		
		self.detector.setGapFill(-1)
		
		if extendedRequest.hasMiniKappaAngles():
			header = "Mini kappa in use"
		else:
			header = "Mini kappa not in use"
		self.detector.setFileHeader(header)
		
		self.detector.setFileprefix(extendedRequest.dnaFilePrefix)
		
		self.detector.setNumberOfExposures(1)
		
		self.detector.setFileformat("%s%s" + MxProperties.IMAGE_NUMBER_FORMAT + "." + self.detector.getSuffix())
		
		self.detector.setAutoIncrement("Yes")
		
		self.detector.setDelayTime(delayTime)
		
		self.detector.setMode("Ext. Trigger")
		
		self.template_writer.configure_template(handler, self.detector, (xBeamPixels, yBeamPixels), extendedRequest.getSampleDetectorDistanceInMM(), gonio_rotation_vector)
	
	def prepare_for_oscillation(self, handler, oscillation, osc_axis):
		
		pilatusSpecialCollection = (oscillation.getOverlap() == 0)
		
		params = PilatusDetectorCollectionParameters()
		
		params.setExposureTime(oscillation.getExposure_time())
		params.setOscillationSize(oscillation.getRange())
		params.setOmegaIncrement(oscillation.getRange())
		params.setOscillationAxis(osc_axis)
		
		if pilatusSpecialCollection:
			params.setStartAngle(oscillation.getStart())
			params.setOmega(oscillation.getStart())
		
		self.detector.initialiseDataSet(params)  # use initialiseDataSet so that the exposure time/period get updated
		
		if pilatusSpecialCollection:
			self.detector.setNumberOfImages(oscillation.getNumber_of_images())
		else:
			self.detector.setNumberOfImages(1)
	
	def start_before_oscillation(self):
		
		# Nothing has to be done here for the Pilatus
		pass
	
	def check_detector_before_image(self, handler):
		
		self.waitUntilDetectorReady(handler)
	
	def prepare_for_image(self, handler, oscillation, start_image_num, start_angle):
		
		pilatusSpecialCollection = (oscillation.getOverlap() == 0)
		
		if not pilatusSpecialCollection:
			params = PilatusDetectorCollectionParameters()
			params.setStartAngle(start_angle)
			params.setOmega(start_angle)
			self.detector.sendParameters(params)  # use sendParameters so that the exposure time/period do not get changed
		
		self.detector.setFilenumber(start_image_num)
	
	def start_before_image(self):
		
		self.detector.start(None, 0)
	
	def after_image(self, handler, start_image_num):
		
		self.waitUntilDetectorReady(handler)
		
		checkPilatusFilenumberUpdate(self.detector, handler.update, start_image_num, FILE_NUMBER_UPDATE_TIMEOUT)
		
		self.handleDetectorErrorStatus()
	
	def after_oscillation(self):
		
		# Nothing has to be done here for the Pilatus
		pass


class PilatusGridScanDetectorWrapper(PilatusDetectorWrapper, base.GridScanDetectorWrapperBase):
	
	def at_scan_start(self, handler, mode, exposureTime, wavelength, detector_distance, directory, prefix, delayTime, omega, transmissionInPercent, flux, osc_axis, gonio_rotation_vector, data_collection_id, omega_increment):
		
		(xBeamPixels, yBeamPixels) = self.getBeamPositionPixels(detector_distance)
		
		filepath = getDetectorWriteFilepath(directory)
		
		params = PilatusDetectorCollectionParameters()
		
		params.setOscillationSize(0)
		params.setExposureTime(float(exposureTime))
		params.setBeamX(xBeamPixels)
		params.setBeamY(yBeamPixels)
		params.setWavelength(wavelength)
		params.setSampleDetectorDistance(detector_distance)
		params.setOmegaIncrement(omega_increment)
		
		params.setDetectorVOffset(0)
		params.setStartAngle(omega)
		params.setPolarization(0.99)
		params.setTransmission(transmissionInPercent / 100.)
		params.setFlux(flux)
		
		params.setPhiIncrement(0)
		params.setChi(0)
		params.setChiIncrement(0)
		params.setOmega(omega)
		params.setOmegaIncrement(0)
		
		params.setOscillationAxis(osc_axis)
		
		self.detector.initialiseDataSet(params)  # use initialiseDataSet so that the exposure time/period get updated
		
		self.detector.setFilepath(filepath)
		
		self.detector.setFileprefix(prefix)
		
		self.detector.setNumberOfExposures(1)
		
		self.detector.setFileformat("%s%s" + MxProperties.IMAGE_NUMBER_FORMAT + "." + self.detector.getSuffix())
		
		self.detector.setAutoIncrement("Yes")
		
		self.detector.setDelayTime(delayTime)
		
		self.detector.setGapFill(-1)
		
		multipleTriggers = (mode == "pmac")
		self.detector.setMode("Mult. Trigger" if multipleTriggers else "Ext. Trigger")
		
		self.template_writer.configure_template(handler, self.detector, (xBeamPixels, yBeamPixels), detector_distance, gonio_rotation_vector)
	
	###########################################################################
	
	def multi_sweep_before_all_rows_or_columns(self, num_sweeps, images_per_sweep):
		
		# Nothing has to be done here for the Pilatus
		pass
	
	def multi_sweep_start_before_all_rows_or_columns(self):
		
		# Nothing has to be done here for the Pilatus
		pass
	
	def multi_sweep_before_row_or_column(self, startImageNumber, numImages):
		
		self._before_sweep(startImageNumber, numImages)
	
	def multi_sweep_before_subsequent_row_or_column(self, startImageNumber):
		
		self._before_subsequent_sweep(startImageNumber)
	
	def multi_sweep_start_before_row_or_column(self):
		
		self._start_before_sweep()
	
	def multi_sweep_after_row_or_column(self, handler, startImageNumber):
		
		checkPilatusFilenumberUpdate(self.detector, handler.update, startImageNumber, FILE_NUMBER_UPDATE_TIMEOUT)
	
	def multi_sweep_after_all_rows_or_columns(self):
		
		# Nothing has to be done here for the Pilatus
		pass
	
	###########################################################################
	
	def single_sweep_before_sweep(self, startImageNumber, numImages):
		
		self._before_sweep(startImageNumber, numImages)
	
	def single_sweep_start_before_sweep(self):
		
		self._start_before_sweep()
	
	def single_sweep_after_sweep(self):
		
		self.detector.waitForReady()
	
	###########################################################################
	
	def _before_sweep(self, startImageNumber, numImages):
		
		self.detector.waitForReady()
		
		self.detector.setFilenumber(startImageNumber)
		self.detector.setNumberOfImages(numImages)
	
	def _before_subsequent_sweep(self, startImageNumber):
		
		self.detector.waitForReady()
		
		self.detector.setFilenumber(startImageNumber)	
	
	def _start_before_sweep(self):
		
		self.detector.start(None, 0)


class PilatusLineScanDetectorWrapper(PilatusDetectorWrapper, base.LineScanDetectorWrapperBase):
	
	def at_scan_start(self, handler, num_wedges, images_per_wedge, exposure_time, detector_distance, wavelength, angle_range, directory, prefix, delay_time, transmission_percent, flux, gonio_rotation_vector, data_collection_id):
		
		(xBeamPixels, yBeamPixels) = self.getBeamPositionPixels(detector_distance)
		
		filepath = getDetectorWriteFilepath(directory)
		
		params = PilatusDetectorCollectionParameters()
		
		params.setExposureTime(exposure_time)
		
		params.setBeamX(xBeamPixels)
		params.setBeamY(yBeamPixels)
		
		params.setWavelength(wavelength)
		
		params.setSampleDetectorDistance(detector_distance)
		
		params.setOscillationSize(angle_range)
		
		params.setDetectorVOffset(0)
		params.setPolarization(0.99)
		params.setTransmission(transmission_percent / 100.)
		params.setFlux(flux)
		
		params.setPhiIncrement(0)
		params.setChi(0)
		params.setChiIncrement(0)
		params.setOmegaIncrement(angle_range)
		
		self.detector.initialiseDataSet(params)  # use initialiseDataSet so that the exposure time/period get updated
		
		self.detector.setFilepath(filepath)
		
		self.detector.setFileprefix(prefix)
		
		self.detector.setNumberOfExposures(1)
		
		self.detector.setNumberOfImages(images_per_wedge)
		
		self.detector.setFileformat("%s%s" + MxProperties.IMAGE_NUMBER_FORMAT + "." + self.detector.getSuffix())
		
		self.detector.setAutoIncrement("Yes")
		
		self.detector.setDelayTime(delay_time)
		
		self.detector.setGapFill(-1)
		
		self.detector.setMode("Ext. Trigger")
		
		self.template_writer.configure_template(handler, self.detector, (xBeamPixels, yBeamPixels), detector_distance, gonio_rotation_vector)
	
	###########################################################################
	
	def wedged_start_before_all_wedges(self):
		
		# Nothing has to be done here for the Pilatus
		pass
	
	def wedged_at_wedge_start(self, image_number, start_angle):
		
		self._at_wedge_start(image_number, start_angle)
	
	def wedged_start_before_wedge(self):
		
		self._start_before_wedge()
	
	def wedged_at_wedge_end(self, handler, image_number):
		
		self._at_wedge_end(handler, image_number)
	
	def wedged_after_all_wedges(self):
		
		# Nothing has to be done here for the Pilatus
		pass
	
	###########################################################################
	
	def helical_at_wedge_start(self, image_number, start_angle):
		
		self._at_wedge_start(image_number, start_angle)
	
	def helical_start_before_wedge(self):
		
		self._start_before_wedge()
	
	def helical_at_wedge_end(self, handler, image_number):
		
		self._at_wedge_end(handler, image_number)
	
	###########################################################################
	
	def _at_wedge_start(self, image_number, start_angle):
		
		self.detector.waitForReady()
		
		params = PilatusDetectorCollectionParameters()
		
		params.setStartAngle(start_angle)
		params.setOmega(start_angle)
		
		self.detector.sendParameters(params)  # use sendParameters so that the exposure time/period do not get changed
		
		self.detector.setFilenumber(image_number)
	
	def _start_before_wedge(self):
		
		self.detector.start(None, 0)
	
	def _at_wedge_end(self, handler, image_number):
		
		self.detector.waitForReady()
		
		self.handleDetectorErrorStatus()
		
		checkPilatusFilenumberUpdate(self.detector, handler.update, image_number, FILE_NUMBER_UPDATE_TIMEOUT)
