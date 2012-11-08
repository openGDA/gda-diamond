from gda.device.scannable import PseudoDevice


from Jama import Matrix

class PsicPseudoDevice(PseudoDevice):

	def __init__(self,name,azimuth):
		self.name = name
#		self.euler = euler
		self.azimuth = azimuth
#		self.calc = calcAngles
#		self.hkl = hkl

	def asynchronousMoveTo(self,new_position):
		self.azimuth.setPsi(new_position)
#		angles = self.calc.getAngles(3,self.hkl.getPosition())
#		self.euler.moveTo([angles.Phi,angles.Chi,angles.Eta])
		

	def isBusy(self):
		return 0


	def getPosition(self):
		psi=self.azimuth.getPsi()
		return psi

	#string representation of the data in an object
	def toString(self):
		return self.getName() + ":" + `self.getPosition()`
