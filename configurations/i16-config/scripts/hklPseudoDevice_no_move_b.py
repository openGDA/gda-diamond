from gda.device.scannable import PseudoDevice

import RecSpace
import CalcAngles
import EulerianKconversionModes

from Jama import Matrix

from jarray import array
from java.lang import String

class hklPseudoDeviceb(PseudoDevice):

	def __init__(self,name,euler,tth,rs,cal,EDi,az):
		self.name = name
		self.euler = euler
		self.tth = tth
		self.rs = rs
		self.cal= cal
		self.EDi = EDi
		self.az=az
		self.inputNames = array(['h', 'k','l'], String)
		self.ekcm = EulerianKconversionModes.EulerianKconversionModes()
		self.setOutputFormat(["%4.8f","%4.8f","%4.8f"])
		self.angles=None

	def asynchronousMoveTo(self,new_position):
		angles = self.cal.getAngles(self.EDi.getMode(),new_position)
		self.alpha_angle=self.az.getAlpha(angles,new_position)
		euler_positions = [angles.Phi,angles.Chi,angles.Eta,angles.Mu,angles.Delta,angles.Gamma]
		new_positions = self.ekcm.getKPossibleAngles(euler_positions[2::-1])
		print "New alpha value",self.alpha_angle
		print "Kphi would have moved to",new_positions.KPhi
		print "KTheta would have moved to",new_positions.KTheta
		print "Kappa would have moved to",new_positions.K
		print "phi would have moved to: ", angles.Phi
		print "chi would have moved to: ", angles.Chi
		print "eta would have moved to: ", angles.Eta
		print "mu would have moved to: ", angles.Mu
		print "delta would have moved to: ", angles.Delta
		print "gamma would have moved to: ", angles.Gamma
		self.angles=angles 

	#
	# If the euler PD is busy then so is this device
	#
	def isBusy(self):
		return self.euler.isBusy()

	#
	# Returns the current Eulerian coordinates as an array
	#
	def getPosition(self,tth=None,theta=None,chi=None,phi=None,UB=None,wl=None):
		matrix = self.rs.calcHKL(tth,theta,chi,phi,UB,wl)
		h = matrix.get(0,0)
		k = matrix.get(1,0)
		l = matrix.get(2,0)
		return [h,k,l]


	#string representation of the data in an object
#	def toString(self):
#		return self.getName() + ":" + `self.getPosition()`



