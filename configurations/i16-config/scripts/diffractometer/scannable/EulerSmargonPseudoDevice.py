#
#	A Scannable (pseudo device) which creates three pseudo devices representing
#	the Eulerian angles for a six circle diffractometer
# [phi, chi, eta,mu,delta,gamma]
#
from java.lang import Double
from java.lang import Thread
from java.lang import String
from jarray import array
import java.lang.Exception
from gda.device.scannable import ScannableMotionBase
from gda.jython import JythonServerFacade

import beamline_objects as BLobjects
import ShelveIO
import Angles

class EulerianPseudoDevice(ScannableMotionBase):

	#
	# Constructor.  Must have six motors to control.
	#
	def __init__(self,name,storedAngles,mu,delta,gam):
		self.setName(name)
		self.setInputNames(array(['phi','chi','eta'], String))
		self.setExtraNames(['mu','delta','gamma'])
		self.storedAngles = storedAngles
		self.mu = mu
		self.delta = delta
		self.gam = gam

		self.SO = 'SO'
		self.SO=ShelveIO.ShelveIO()
		self.SO.path=ShelveIO.ShelvePath+'SO'
		self.SO.setSettingsFileName('SO')
		self.Etaoff=None
		self.disable_kmu = False
		
		


	def setEtaOffset(self,angle):
		self.Etaoff=angle
		self.SO.ChangeValue('Eta',angle)

	def getEtaOffset(self):
		if self.Etaoff == None:
			self.Etaoff = self.SO.getValue('Eta')
		return self.Etaoff



	#
	# Simply return the modes of the convertor
	#
	def __repr__(self):
		positions = self.getPosition();
		#phi_pos = String.format(self.getOutputFormat()[0],str(positions[0]))
		# TODO: Should OutputFormat not be the full length of input names? (rdw April2008)
		phi_pos = String.format(self.getOutputFormat()[0], [ positions[0] ])
		chi_pos = String.format(self.getOutputFormat()[0], [ positions[1] ])
		eta_pos = String.format(self.getOutputFormat()[0], [ positions[2] ])
		mu_pos  = String.format(self.getOutputFormat()[0], [ positions[3] ])
		delta_pos = String.format(self.getOutputFormat()[0], [ positions[4] ])
		gamma_pos = String.format(self.getOutputFormat()[0], [ positions[5] ])


		return self.getName() + ".phi : " + phi_pos +"\n" + self.getName() + ".chi : " + chi_pos +"\n" + self.getName() + ".eta : " + eta_pos + "\n" +self.getName() + ".mu : " + mu_pos +"\n" + self.getName() + ".delta : " + delta_pos +"\n" + self.getName() + ".gamma : " + gamma_pos

		
	def toString(self):
		return self.__repr__()
	#
	#  Assume new position is in the form [phi, chi, theta]
	#
	def asynchronousMoveTo(self,new_position):
		#print new_position
		try:
			self.storedAngles.ChangeAngle('phi',new_position[0])
			self.storedAngles.ChangeAngle('chi',new_position[1])
			self.storedAngles.ChangeAngle('eta',new_position[2])
		except:
			print "Warning:it did not move the smargon"
		try:
			self.delta.asynchronousMoveTo(new_position[4])
			self.gam.asynchronousMoveTo(new_position[5]) 
		except:
			print "Warning::it did not move delta or gamma"



	#
	# Returns true if any of the six motors is busy
	#
	def isBusy(self):
		return BLobjects.isBusy()

	#
	# Returns the current Eulerian coordinates as an array
	#
	def getPosition(self):
		angles = self.storedAngles.getAngles()
		return [angles.Phi,angles.Chi,angles.Eta,angles.Mu,angles.Delta,angles.Gamma]

