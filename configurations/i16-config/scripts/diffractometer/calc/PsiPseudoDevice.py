from gda.device.scannable import ScannableMotionBase


from Jama import Matrix

#import EulerianDiffractometerInfo as EDi



class PsiPseudoDevice(ScannableMotionBase):

	def __init__(self,name,euler,azimuth,calcAngles,hkl):
		self.name = name
		self.euler = euler
		self.azimuth = azimuth
		self.calc = calcAngles
		self.hkl = hkl

	def asynchronousMoveTo(self,new_position,current_hkl=None):
		self.azimuth.setPsi(new_position)
		angles = self.calc.getAngles(3,self.hkl.getPosition())
		self.euler.moveTo([angles.Phi,angles.Chi,angles.Eta])
		

	def isBusy(self):
		return self.euler.isBusy()


	def getPosition(self):
		psi=self.azimuth.calcPsi(None,self.hkl.getPosition())
		return psi[0]


	#string representation of the data in an object
	def toString(self):
		return self.getName() + ":" + `self.getPosition()`


class PsicPseudoDevice(ScannableMotionBase):

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
		return 

	#string representation of the data in an object
	def toString(self):
		return self.getName() + ":" + `self.getPosition()`
