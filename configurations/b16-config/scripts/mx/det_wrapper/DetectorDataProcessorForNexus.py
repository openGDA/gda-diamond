from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi, DetectorDataProcessorPositionCallable

class CachingDetectorDataProcessorPositionCallable(DetectorDataProcessorPositionCallable):
	"""
	Caches result of callable
	"""
	def __init__(self, dataset_provider, processors, roi=None):
		DetectorDataProcessorPositionCallable.__init__(self, dataset_provider, processors, roi)
		self.last_position = None
	
	def call(self):
		self.last_position = DetectorDataProcessorPositionCallable.call(self)
		return self.last_position

class DetectorDataProcessorWithRoiForNexus(DetectorDataProcessorWithRoi):
	def __init__(self, name, processing_detector, twod_dataset_processors, prefix_name_to_extranames=True):
		DetectorDataProcessorWithRoi.__init__(self, name, processing_detector, twod_dataset_processors, prefix_name_to_extranames)
		self.cached_callable = None
	
	def _createPositionCallable(self, datasetProvider):
		self.cached_callable = DetectorDataProcessorWithRoi._createPositionCallable(self, datasetProvider)
		return self.cached_callable
	
	def getPosition(self, dataset=None):
		"""
		This gets called early on in the scan by the NeXus writing framework.
		We return already-acquired data, or dummy data of the correct dimensionality,
		to avoid advancing fragile scan state 
		"""
		try:
			position = self.cached_callable.last_position
			if not position:
				raise AttributeError
			return position
		except AttributeError:
			return [0.] * len(self.getExtraNames())