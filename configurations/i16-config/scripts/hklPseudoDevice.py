from gda.device.scannable import PseudoDevice

import RecSpace
import CalcAngles
import beamline_objects as BLobjects
from gda.jython import JythonServerFacade
from org.apache.commons.lang import ArrayUtils

from Jama import Matrix

from jarray import array
from java.lang import String


class hklPseudoDevice(PseudoDevice):

	def __init__(self,name,euler,tth,rs,cal,EDi,delta,gam,az):
		self.name = name
		self.euler = euler
		self.tth = tth
		self.rs = rs
		self.cal= cal
		self.EDi = EDi
		self.setInputNames(['h', 'k','l'])
		self.delta = delta
		self.gam = gam
		self.setName("hkl")
		self.setOutputFormat(["%4.4f","%4.4f","%4.4f"])
		self.az=az
		self.disable_gamma = False
		self.disable_delta = False

	def asynchronousMoveTo(self,new_position):
		new_position2 = []
		for el in new_position:
			new_position2 += [float(el)]
		new_position = new_position2

		new_position = ArrayUtils.toPrimitive(new_position)
		if self.EDi.getMode() == 3: 
			angles = self.cal.getAngles(self.EDi.getMode(),new_position,None,self.az.getPsi())
		else:
			angles = self.cal.getAngles(self.EDi.getMode(),new_position)
		euler_positions = [angles.Phi,angles.Chi,angles.Eta,angles.Mu,angles.Delta,angles.Gamma]
		
		########################## SAFETY IMPROVEMENTS (RDW) ########################
		# bypass storedAngles and check limits of motors directly
		# Euler
		# There is no outside method to go all the way and check all the limits on euler, as this would also
		# have to check the limits on the DOF motors it moves.  However if a request is made it will not 
		# be able to perform it will throw an exception.  As long as delta and gamma are moved after it, then we 
		# logically safe (assuming the exception really stops program flow)
		panicStop = JythonServerFacade.getInstance().panicStop
		
		# No need to checkEuler, as it will stop code if a limit is exceeded. 
		# Delta
		if not self.disable_delta:
			report = self.delta.checkPositionValid(angles.Delta)
			if (report != None):
				raise RuntimeError, "\nMove not performed because: \n" + report  

#		# Gamma
		if not self.disable_gamma:
			report = self.gam.checkPositionValid(angles.Gamma)
			if (report != None):
				raise RuntimeError, "\nMove not performed because: \n" + report

		# euler will stop the code if the move is outside limits or if another error prevents a move
		self.euler.asynchronousMoveTo(euler_positions) #! aslo sends in mu, delta, gamma!
		#self.delta.asynchronousMoveTo(angles.Delta)
		#self.gam.asynchronousMoveTo(angles.Gamma)

		if not self.disable_delta:
			try:
				self.delta.asynchronousMoveTo(angles.Delta)
			except:
				print "<<HKL move failed: problem moving Delta. Axis may be disabled, unhomed or kaput. Calling PanicStop incase other axes are allready moving...>>"
				panicStop()

		if not self.disable_gamma:
			try:
				self.gam.asynchronousMoveTo(angles.Gamma)
			except:
				print "<<HKL move failed: problem moving Gamma. Axis may be disabled, unhomed or kaput. Calling PanicStop incase other axes are allready moving...>>"
				panicStop()


	#
	# If the euler PD is busy then so is this device
	# TODO: Must also check delta ang gamma!
	def isBusy(self):
		if self.delta.isBusy() ==1 or self.gam() == 1 or self.euler.isBusy() == 1:
			return 1
		else:
			return 0


	#
	# Returns the current Eulerian coordinates as an array
	#
	def getPosition(self,mu=None,eta=None,chi=None,phi=None,delta=None,gamma=None,UB=None,wavelength=None):
		matrix = self.rs.calcHKL(mu,eta,chi,phi,delta,gamma,UB,wavelength)
		h = matrix.get(0,0)
		k = matrix.get(1,0)
		l = matrix.get(2,0)
#		print "Euler,delta",self.isBusy(), self.delta.isBusy()	
		return [h,k,l]

	#string representation of the data in an object
#	def toString(self):
#		return self.getName() + ":" + `self.getPosition()`

