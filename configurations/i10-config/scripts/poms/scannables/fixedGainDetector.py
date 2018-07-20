""" #########################################################################################################
Fixed gain detector

Use this to correct the counting card value into a current based on the gain of the current amplifier

Useful with diodes, except for reflectivity measurements where the gain needs to change


from beamline.scannables import fixedGainDetector
det = fixedGainDetector("det, macr17, 1e7)


David Burn
1/3/17

######################################################################################################### """


from gda.device.detector import DetectorBase

class fixedGainDetector(DetectorBase):
	def __init__(self, name, det, gain):
		self.setName(name)
		self.setInputNames(['collectionTime'])
		self.setExtraNames([name])
		self.setOutputFormat(["%5.5g","%5.5g"])
		self.Units("amps")
		self.isCollecting = 0 
		self.gain = gain
		self.collectionTime = 1
		self.det = det

	def collectData(self):
		isCollecting = 1
		self.det.setCollectionTime(self.collectionTime)
		self.det.collectData()
		isCollecting = 0

	def getStatus(self):
		return self.isCollecting

	def readout(self):	
		return self.det.readout() / 100000.0 * self.collectionTime * self.gain
	
	def getDataDimensions(self):
		return 1
	
	def stop(self):
		self.det.stop()