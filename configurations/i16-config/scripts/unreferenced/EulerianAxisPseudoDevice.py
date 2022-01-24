#
#   A pseudo device which acts as one of the Eulerian psuedo-axes of a
#   kappa diffractometer.
#

from java.lang import Thread

from gda.device.scannable import ScannableMotionBase

import EulerianPseudoDevice
import EulerianKconversionModes


class EulerianAxisPseudoDevice(ScannableMotionBase):

	#
	# Constructor. Must have the EulerianPD object ref and which axis
	# this class represents.
	#
	def __init__(self,name,euler,storedAngles):
		EulerianAxisPseudoDevice.euler = euler
		self.name = euler.getName() + "." + name
		self.ekcm = EulerianKconversionModes.EulerianKconversionModes()
		self.storedAngles = storedAngles
		self.chif_flag=0
 
	#
	#  Assume new position is a single number
	#
	def asynchronousMoveTo(self,new_position):
		# Check new position is within limits

		report = self.checkPositionValid(new_position);
		if (report != None):
			raise RuntimeError, "\nMove not performed because: \n" + report			

		#chi moves all three kappa axes
		if self.name == 'euler.chi':
			##wait for any moves on the Euler device to complete first
			while self.euler.isBusy():
				Thread.sleep(200)
			##work out the new position to move to
			current_positions = self.euler.getPosition()
		## AB modified on 29/07/08 to prevent drift to go back
		#  remove atStart and atEnd and the first option in the following if  
			if self.chif_flag==1:
#				print "using fix phi and eta"
				self.startingpos[self.getAxis()] = new_position 
				self.euler.asynchronousMoveTo(self.startingpos)
			else: 
				current_positions[self.getAxis()] = new_position
				#this will NOT work until euler returns all six angles when asked
				self.euler.asynchronousMoveTo(current_positions)
		#eta only moves kth
		elif self.name == 'euler.eta':
			#wait for any moves on the Euler device to complete first
			while self.euler.isBusy():
				Thread.sleep(200)
			#work out the new position to move to
			current_positions = self.euler.getPosition()
			current_positions[self.getAxis()] = new_position
      			
			# calculate the new angles based
			new_positions = self.ekcm.getKPossibleAngles(current_positions[2::-1])

			#but only move kth, so if errors in others then they are not carried over
			self.storedAngles.ChangeAngle("Kth",new_positions.KTheta)

		#phi only moves kphi
		elif self.name == 'euler.phi':
			#wait for any moves on the Euler device to complete first
			while self.euler.isBusy():
				Thread.sleep(200)
			#work out the new position to move to
			current_positions = self.euler.getPosition()
			current_positions[self.getAxis()] = new_position
      			
			# calculate the new angles based
			new_positions = self.ekcm.getKPossibleAngles(current_positions[2::-1])

			#but only move kphi, so if errors in others then they are not carried over
			self.storedAngles.ChangeAngle("Kphi",new_positions.KPhi)
		else:
			print "wrong axis!"

			

	#
	# If the euler PD is busy then so is this device
	#
	def isBusy(self):
		return self.euler.isBusy()

	#
	# Return an integer matching the object name to the location of the position
	# in the array from the euler.getPosition() method.
	#
	def getAxis(self):
		if self.name == 'euler.phi':
			return 0
		elif self.name == 'euler.chi':
			return 1
		elif self.name == 'euler.eta':
			return 2
		else:
			return None
	#
	# Returns the current Eulerian coordinates as an array
	#
	def getPosition(self):
		return self.euler.getPosition()[self.getAxis()]



	#
	#AB 29/07/08 quick and dirt fix for drift of phi and eta in chi scans
	#
	def atScanStart(self):
		while self.euler.isBusy():
			Thread.sleep(200)
		if self.name =='euler.chi':
			print "Using fixed phi and eta AB 29/07/08"
			print "modify EulerianAxisPseudoDevice if you need to go back to old ver"
			self.chif_flag=1
			self.startingpos=self.euler.getPosition()
#			print "I have set it!!"
#			print self.startingpos
		else:
			pass
	#
	#AB 29/07/08 quick and dirt fix for drift of phi and eta in chi scans
	#
	def atScanEnd(self):
		if self.chif_flag ==1:
			self.chif_flag=0
			
	

	#string representation of the data in an object
	def __repr__(self):
		return self.__str__()

	#string representation of the object
	def __str__(self):
		return self.getName() + " : " + `self.getPosition()`

