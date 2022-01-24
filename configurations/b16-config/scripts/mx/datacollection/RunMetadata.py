from gda.px import AxisChoice

class RunMetadata():

	DIRECTION_AXIS_INC = 1.0
	DIRECTION_AXIS_DEC = -1.0

	def __init__(self):
		self.label = "Run"
		self.oscillation = None
		self.ecr = None
		self._collectionId = 0
		self._direction = RunMetadata.DIRECTION_AXIS_INC
		self._userStep = None
		self._preScanPosition = 0.0
		self._overRangeDelta = 0.0
		self.index = 0


	def __call__(self):
		print self


	def __str__(self):
		lines = []
		lines.append('Run Metadata :: %s' % (self.label))
		
		attributes = [
			'axis choice',
			'wavelength',
			'detector distance',
			'two theta',
			'omega',
			'phi',
			'kappa',
			'start',
			'end',
			'step',
			'span',
			'exposure',
			'duration',
			'speed',
			'num images'
		]
		formats = ['%s '] + ['%10.5f '] * 13 + ['%4d']
		values = [
			self.axisChoice(),
			self.wavelength(),
			self.detDistance(),
			self.twoThetaVal(),
			self.omegaVal(),
			self.phiVal(),
			self.kappaVal(),
			self.start(),
			self.end(),
			self.step(),
			self.span(),
			self.exposure(),
			self.duration(),
			self.speed(),
			self.numImages()
		]
		
		for name, fmt, position in zip(attributes, formats, values):
			lines.append(" " + name.ljust(10) + ": " + str(fmt%position))
		return '\n'.join(lines)


	def axisChoice(self):
		return self.ecr.getAxisChoice()


	def collectionId(self):
		return self._collectionId


	def countTotalNumImages(self):
		total = 0
		for osc in self.ecr.getRequest().getOscillation_sequence():
			total += osc.getNumber_of_images()
		return total


	def detDistance(self):
		return self.ecr.getSampleDetectorDistanceInMM()


	def direction(self):
		return self._direction

	def duration(self):
		return self.exposure() * self.numImages()


	def end(self):
		return self.start() + (self.step() * self.numImages())


	def exposure(self):
		return self.oscillation.getExposure_time()


	def isRotationOmega(self):
		return self.axisChoice() == AxisChoice.OMEGA.getCode()


	def isRotationPhi(self):
		return self.axisChoice() == AxisChoice.PHI.getCode()


	def kappaVal(self):
		return self.ecr.getKappa()


	def label(self):
		return self.label


	def numImages(self):
		return self.oscillation.getNumber_of_images()


	def numPasses(self):
		return self.oscillation.getNumber_of_passes()


	def omegaVal(self):
		if self.axisChoice() == AxisChoice.OMEGA.getCode():
			return self.start()
		return self.otherAxis()


	def oscillation(self, index=None):
		if index is not None:
			oscillation = self.ecr.getRequest().getOscillation_sequence()[index]
		else:
			oscillation = self.oscillation
		return oscillation


	def otherAxis(self):
		return self.ecr.getOtherAxis()


	def overRangeDelta(self):
		if not self._overRangeDelta:
			self._overRangeDelta = self.range() / self.exposure()
		return self._overRangeDelta


	def phiVal(self):
		if self.axisChoice() == AxisChoice.PHI.getCode():
			return self.start()
		return self.otherAxis()


	def preScanPosition(self):
		return self._preScanPosition


	def range(self):
		return self.oscillation.getRange()


	def runNumber(self):
		return self.ecr.getRunNumber()


	def setCollectionId(self, collection_id):
		self._collectionId = collection_id


	def setDetectorDistance(self, distance):
		self.ecr.setSampleDetectorDistanceInMM(distance)


	def setDirection(self, delta):
		if delta < 0.0:
			self._direction = RunMetadata.DIRECTION_AXIS_DEC
		else:
			self._direction = RunMetadata.DIRECTION_AXIS_INC


	def setExposureTime(self, exptime):
		self.oscillation.setExposure_time(exptime)


	def setExtendedCollectRequest(self, ecr, index=0):
		self.ecr = ecr
		self.index = index
		self.oscillation = ecr.getRequest().getOscillation_sequence()[index]


	def setKappa(self, kappaVal):
		self.ecr.setKappa(kappaVal)


	def setLabel(self, label):
		self.label = label


	def setNumImages(self, count):
		self.oscillation.setNumber_of_images(count)
		self.ecr.setTotalNumberOfImages(self.countTotalNumImages())


	def setNumPasses(self, count):
		self.oscillation.setNumber_of_passes(count)


	def setOmega(self, omegaVal):
		if self.axisChoice() == AxisChoice.OMEGA.getCode():
			self.setStart(omegaVal)
		else:
			self.ecr.setOtherAxis(omegaVal)


	def setOverRangeDelta(self, delta):
		self._overRangeDelta = delta



	def setPhi(self, phiVal):
		if self.axisChoice() == AxisChoice.PHI.getCode():
			self.setStart(phiVal)
		else:
			self.ecr.setOtherAxis(phiVal)


	def setPreScanPosition(self, position):
		self._preScanPosition = position


	def setStart(self, start):
		self.oscillation.setStart(start)


	def setStep(self, step):
		self.oscillation.setRange(step)


	def setTransmissionInPercent(self, transmission):
		self.ecr.setTransmissionInPercent(transmission)


	def setTwoTheta(self, twoThetaVal):
		self.ecr.setTwoTheta(twoThetaVal)


	def setUserStep(self, value):
		self._userStep = value


	def setWavelength(self, wavelength):
		self.ecr.getRequest().setWavelength(wavelength)


	def span(self):
		return self.step() * self.numImages()


	def speed(self):
		return abs(self.step() / self.exposure())


	def start(self):
		return self.oscillation.getStart()


	def startImageNumber(self):
		if self.oscillation.hasStart_image_number():
			return self.oscillation.getStart_image_number()
		else:
			return 1


	def step(self):
		return self.oscillation.getRange()


	def totalNumberOfImages(self):
		return self.ecr.getTotalNumberOfImages()


	def transmissionInPercent(self):
		return self.ecr.getTransmissionInPerCent()


	def twoThetaVal(self):
		return self.ecr.getTwoTheta()


	def userStep(self):
		return self._userStep


	def wavelength(self):
		return self.ecr.getRequest().getWavelength()

