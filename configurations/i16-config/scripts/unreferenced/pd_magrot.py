from gda.device.scannable import PseudoDevice

class magrotClass(PseudoDevice):
	'''magrot PD Class - mag rot is absolute magnet angle (depends on psi)'''
	def __init__(self, name, magmot):
		self.magmot=magmot
		self.setName(name)
		self.setInputNames([name])
		self.setExtraNames([self.magmot.getName()])
		self.Units=['Units']
		self.setOutputFormat(['%5.1f', '%5.1f'])
		self.setLevel(7)

	def isBusy(self):
		return self.magmot.isBusy()

	def getPosition(self):
		return [psi()-self.magmot(), self.magmot()]	

	def asynchronousMoveTo(self,new_position):
		self.magmot.asynchronousMoveTo(psic()-new_position)

magrot=magrotClass('magrot', xps3m1)

