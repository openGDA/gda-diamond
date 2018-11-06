""" #########################################################################################################
XFMR detector
######################################################################################################### """


from gda.device.detector import DetectorBase
import time
import scisoftpy as dnp


class xfmrDetector(DetectorBase):
	def __init__(self, name, xch, ych, liaSensitivity):
		self.setName(name)
		self.setInputNames(['collectionTime'])
		self.setExtraNames(['x', 'y'])
		self.setOutputFormat(["%5.5g","%5.5g","%5.5g"])
		self.isCollecting = 0 
		
		self.collectionTime = 1
		
		self.xch = xch
		self.ych = ych
		self.liaSensitivity = 0
		self.liaSensitivityScannable = liaSensitivity
		
		self.xraw = 0
		self.yraw = 0
		self.x = 0
		self.y = 0
		#self.magnitude = 0
		
		

	def collectData(self):
		self.isCollecting = 1
		self.xch.setCollectionTime(self.collectionTime)
		self.xch.collectData()
		
		while self.xch.getStatus() != 0:	# wait until detectors have finished collecting
			time.sleep(0.01)

		self.xraw = self.xch.readout()
		self.yraw = self.ych.readout()
		self.x = (self.xraw / float(self.collectionTime) / 100000.0 - 5) * self.liaSensitivity
		self.y = (self.yraw / float(self.collectionTime) / 100000.0 - 5) * self.liaSensitivity
		
		#self.magnitude = float(dnp.sqrt(self.x**2 + self.y**2))
		self.isCollecting = False
		


	def getStatus(self):
		return self.isCollecting

	def readout(self):	
		return [self.x, self.y]
	
	def getDataDimensions(self):
		return 1
	
	def createsOwnFiles(self):
		return False
	
	def atScanStart(self):
		self.liaSensitivity = self.liaSensitivityScannable.getPosition()


