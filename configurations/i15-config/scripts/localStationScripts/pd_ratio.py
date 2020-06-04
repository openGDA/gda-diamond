from gda.device.scannable import ScannableMotionBase
from time import sleep

class Simple_PD_Ratio(ScannableMotionBase):
	"""
	Class that creates a scannable that is the ratio of 2 others
	"""
	def __init__(self, name, top, bottom):
		self.setName(name)
		self.setInputNames([name])
		self.top = top
		self.bottom = bottom

	def isBusy(self):
		return 0

	def getPosition(self):
		ratio=0
		try:
			ratio = self.top()/self.bottom()
		except:
			ratio=0	
			simpleLog("Warning: One of the diodes read zero")
		return ratio

	def asynchronousMoveTo(self,new_position):
		pass	