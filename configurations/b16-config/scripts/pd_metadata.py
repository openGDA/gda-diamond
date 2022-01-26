from gda.device.scannable import ScannableMotionBase


class MetaDataPD(ScannableMotionBase):
	'''Dummy PD Class'''
	def __init__(self, name):
		self.setName(name)
		self.setInputNames([])
		self.setExtraNames([])
		self.setOutputFormat([])
		self.Units=['Units']
		self.setLevel(3)
		self.currentposition=0

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,new_position):
		pass

	def getPosition(self):
		pass
	
	def atScanStart(self):#
		global SRSWriteAtFileCreation
		SRSWriteAtFileCreation = "Vortex Xmap"
