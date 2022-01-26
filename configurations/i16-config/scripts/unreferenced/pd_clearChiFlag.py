from gda.device.scannable import ScannableMotionBase

import time


class clearChiFlagClass(ScannableMotionBase):
	'''clear chi flag before each scan'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setOutputFormat([])

	def getPosition(self):
		pass

	def isBusy(self):
		return 0
	
	def atCommandFailure(self):
		print time.ctime()+" clearing chi flag"
		chi.chif_flag=0


clearchiflagpd=clearChiFlagClass('clear_chi_flag')
