from gda.device.scannable import ScannableMotionBase

class OffsetAxisClass(ScannableMotionBase):
	'''Create offsetable PD from a scalar PD and offset PD'''
	#OffsetAxisClass.py (devices with user offsets, e.g. th is eta with eta_off as offset)
	def __init__(self, name, PD, offsetPD, help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.PD=PD
		self.offsetPD=offsetPD
		self.setInputNames([name])
		self.setOutputFormat(self.PD.getOutputFormat())
		self.setLevel(self.PD.getLevel())

	def getPosition(self):
		return self.PD()-self.offsetPD()

	def asynchronousMoveTo(self,new_position):
		self.PD.asynchronousMoveTo(new_position+self.offsetPD())

	def isBusy(self):
		return self.PD.isBusy()
	
	def stop(self):
		print "calling stop"
		self.PD.stop()

	def atScanStart(self):
		print self.offsetPD.name+': '+str(self.offsetPD())