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
from gda.device.scannable import PseudoDevice
from gda.jython import JythonServerFacade

import EulerianKconversionModes
import beamline_objects as BLobjects
import ShelveIO
import Angles

class EulerianPseudoDevice(PseudoDevice):

	#
	# Constructor.  Must have six motors to control.
	#
	def __init__(self,name,storedAngles,mu,delta,gam, sixckappa_for_stopping_only):
		self.setName(name)
		self.setInputNames(array(['phi','chi','eta'], String))
		self.setExtraNames(['mu','delta','gamma'])
		self.ekcm = EulerianKconversionModes.EulerianKconversionModes()
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
		self.sixckappa_for_stopping_only=sixckappa_for_stopping_only
		


	def setEtaOffset(self,angle):
		self.Etaoff=angle
		self.SO.ChangeValue('Eta',angle)

	def getEtaOffset(self):
		if self.Etaoff == None:
			self.Etaoff = self.SO.getValue('Eta')
		return self.Etaoff


	#
	# Sets the mode the convertor is to work in
	#
	def setMode(self,mode):
		self.ekcm.setEuleriantoKmode(mode)

	#
	# Returns the mode the convertor is working in
	#
	def getMode(self):
		return self.ekcm.getEuleriantoKmode()

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
		# Check new position is within limits
		report=self.checkPositionValid(new_position[0:3])
		if (report != None):
			print "Input position was:"
			print new_position
			raise RuntimeError, "\nMove not performed because: \n" + report


		new_positions = self.ekcm.getKPossibleAngles(new_position[2::-1])
		#need a class reference to the correct StoredAngles
		#print "get here"
		#kth.isPositionValid(new_positions.KTheta)

		#### These three motors should be moved as a group for safety #### 
		# As a compromise solution if calling an move throws an exception (due to out of bounds for example)
		# call panicStop to stop all movements.  Also the gda's XPS driver will call panicStop if a motor
		# returns a fault due perhaps to a following error, internal limit, or IR beam broken.
		# KLUDGE: The gda should really check all limits before moving any axis
		# to do this, it must check the scannable limits and the lower dof limits	 
		# Get the PanicStop method ready to call if need be!
		
		# Check the scannable-limits of each axis (should also check DOF limits too)
		if  not(BLobjects.isSimulation()):
			# then bypass storedAngles and check limits of motors directly
			# Kphi
			report=BLobjects.getKth().checkPositionValid(new_positions.KTheta)
			if (report != None):
				raise RuntimeError, "\nMove not performed because: \n" + report
			
			# Kap
			report=BLobjects.getKap().checkPositionValid(new_positions.K)
			if (report != None):
				raise RuntimeError, "\nMove not performed because: \n" + report

			# Kphi
			report=BLobjects.getKphi().checkPositionValid(new_positions.KPhi)
			if (report != None):
				raise RuntimeError, "\nMove not performed because: \n" + report



		# Get the PanicStop method ready to call if need be!
		self.sixckappa_for_stopping_only.stop()
		#panicStop = JythonServerFacade.getInstance().panicStop
		
#			self.storedAngles.ChangeAngle("Kth",new_positions.KTheta)
#			self.storedAngles.ChangeAngle("Kap",new_positions.K)
#			self.storedAngles.ChangeAngle("Kphi",new_positions.KPhi)
		# Move KTheta
		if not self.disable_kmu:
			try:
				self.storedAngles.ChangeAngle("Kmu",new_position[3]) # !refers to extra name!
			except java.lang.Exception, e:
				print "Problem moving kmu (stopping all): ", e
				self.sixckappa_for_stopping_only.stop()
			except Exception, e:
				print "Problem moving kmu (stopping all): ", e
				self.sixckappa_for_stopping_only.stop()
				

		try:
			self.storedAngles.ChangeAngle("Kth",new_positions.KTheta)
		except java.lang.Exception, e:
			print "Problem moving kth (stopping all): ", e
			self.sixckappa_for_stopping_only.stop()
		except Exception, e:
			print "Problem moving kth (stopping all): ", e
			self.sixckappa_for_stopping_only.stop()

		# Move Kappa
		try:
			self.storedAngles.ChangeAngle("Kap",new_positions.K)
		except java.lang.Exception, e:
			print "Problem moving kap (stopping all): ", e
			self.sixckappa_for_stopping_only.stop()
		except Exception, e:
			print "Problem moving kap (stopping all): ", e
			self.sixckappa_for_stopping_only.stop()	
		# Move Kphi
		try:
			self.storedAngles.ChangeAngle("Kphi",new_positions.KPhi)
		except java.lang.Exception, e:
			print "Problem moving kphi (stopping all): ", e
			self.sixckappa_for_stopping_only.stop()
		except Exception, e:
			print "Problem moving kphi (stopping all): ", e
			self.sixckappa_for_stopping_only.stop()



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
#		if self.getOffset('Eta') != 0.:
 #		  xxx=angles.Eta+self.getOffset('Eta')
#			return [angles.Phi,angles.Chi,xxx,angles.Mu,angles.Delta,angles.Gamma]
		return [angles.Phi,angles.Chi,angles.Eta,angles.Mu,angles.Delta,angles.Gamma]
#		return [angles.Phi,angles.Chi,angles.Eta]
