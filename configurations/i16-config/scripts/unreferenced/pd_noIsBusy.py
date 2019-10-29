from gda.device.scannable import PseudoDevice

class PD_noisBusyClass(PseudoDevice):
	'''
	Make PD never busy
	'''
	def __init__(self,PD):
		self.PD=PD
		self.setName(PD.getName())
		self.setInputNames(PD.getInputNames())
		self.setOutputFormat(PD.getOutputFormat())
		self.setExtraNames(PD.getExtraNames())
		self.setLevel(PD.getLevel())
	

	def asynchronousMoveTo(self,position):
		self.PD.asynchronousMoveTo(position)
		

	def getPosition(self):
		return self.PD.getPosition()

	def isBusy(self):
		return 0
phin=phi_no_isbusy=PD_noisBusyClass(phi)
etan=eta_no_busy=PD_noisBusyClass(eta)
syn=sy_no_busy=PD_noisBusyClass(sy)
