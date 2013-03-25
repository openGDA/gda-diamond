import glob
import sys
import os
import math
from math import *
import time
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog

#
### PDs required for experiment using the PCO camera (5 Dec 08)
#
# Motors
class Anc150Axis(PseudoDevice):
	'''
	PD for Anc150Axis
	'''
	def __init__(self, name, root):

		self.setName(name);
		self.pvRoot = root
		self.CAFrequency = CAClient(self.pvRoot + "F")
		self.CAVoltage = CAClient(self.pvRoot + "V")
		self.CASize = CAClient(self.pvRoot + "TWSIZE")
		self.CAPos = CAClient(self.pvRoot + "TWPOS")
		self.CANeg = CAClient(self.pvRoot + "TWNEG")
		self.configure()
		
		self.absolutePosition = 0
		
	def isBusy(self):
		return 0

	def getPosition(self):
		"""
		Returns axis position
		"""
		return self.absolutePosition

	def asynchronousMoveTo(self, absPos):
		"""
		Moves axis position to new position
		"""
		diff = absPos - self.absolutePosition
		self.CASize.caput(abs(diff))
		
		# do the move
		if (diff > 0):
			self.CAPos.caput(1)
		else:
			self.CANeg.caput(1)

		# set the absolute position
		self.absolutePosition = absPos
	
	def configure(self):
		self.CAFrequency.configure()
		self.CAVoltage.configure()
		self.CASize.configure()
		self.CAPos.configure()
		self.CANeg.configure()
		
	def getFrequency(self):
		print "Frequency is " + str(self.CAFrequency.caget())
	
	def getVoltage(self):
		print "Voltage is: " + str(self.CAVoltage.caget())

	def setFrequency(self, newFrequency):
		print "Changing frequency from " + str(self.CAFrequency.caget()) + " to " + str(newFrequency) + "..."
		self.CAFrequency.caput(newFrequency)
		print "Done"
	
	def setVoltage(self, newVoltage):
		print "Changing voltage from " + str(self.CAVoltage.caget()) + " to " + str(newVoltage) + "..."
		self.CAVoltage.caput(newVoltage)
		print "Done"

	def resetAbsolute(self, newVal):
		print "Resetting absolute position from " + self.absolutePosition + " to " + str(newVal)
		self.absolutePosition = newVal
		print "Done"

def createAnc150Axis(name, pvname):
	try:
		result = Anc150Axis(name, pvname)
	except Exception, e:
		print "*** Could not create Anc150Axis for pv '" + str(pvname) + "' because: " + str(e)
	return result

print "Creating Anc150Axes..."	
anc1 = createAnc150Axis("anc1", "BL15I-MO-PIEZO:PIEZO-01:")
anc2 = createAnc150Axis("anc2","BL15I-MO-PIEZO:PIEZO-02:")
anc3 = createAnc150Axis("anc3","BL15I-MO-PIEZO:PIEZO-03:")
anc4 = createAnc150Axis("anc4","BL15I-MO-PIEZO:PIEZO-04:")
anc5 = createAnc150Axis("anc5","BL15I-MO-PIEZO:PIEZO-05:")
anc6 = createAnc150Axis("anc6","BL15I-MO-PIEZO:PIEZO-06:")
anc7 = createAnc150Axis("anc7","BL15I-MO-PIEZO:PIEZO-07:")
anc8 = createAnc150Axis("anc8","BL15I-MO-PIEZO:PIEZO-08:")
anc9 = createAnc150Axis("anc9","BL15I-MO-PIEZO:PIEZO-09:")
#
## Germanium detector
class Germanium(PseudoDevice):
	'''
	PD for Germanium detetcor
	'''
	def __init__(self, root):

		self.setName("Germanium");
		self.pvRoot = root
		self.CAReading = CAClient(self.pvRoot + "SCALER.S2")
		self.CAReset = CAClient(self.pvRoot + "SCALER.CNT")
		self.CAG1 = CAClient(self.pvRoot + "SCALER.G1")
		self.configure()
		
		self.CAG1.caput("N")
		
	def isBusy(self):
		return 0

	def getPosition(self):
		"""
		Get reading from detector
		"""
		reading = self.CAReading.caget()
		#self.CAReset.caput(0) 		# stop counting
		#self.CAReset.caput(1) 		# start counting
		return reading

	def asynchronousMoveTo(self, newPos):
		"""
		Do nothing
		"""
	
	def atPointStart(self):
		"""
		Reset the counter
		"""
		self.CAReset.caput(0) 		# stop counting
		self.CAReset.caput(1) 		# start counting
	
	def configure(self):
		self.CAReading.configure()
		self.CAReset.configure()
		self.CAG1.configure()
		
	def getReading(self):
		"""
		Gets reading with no reset
		"""
		return self.CAReading.caget()



germ = Germanium("BL15I-EA-DET-01:")

#
# Scan command:
# scan anc4 1 2 .1 w 0.2 germ
#
# Double scan command:
# scan anc4 1 2 .1 anc5 1 2 .1 w 0.2 germ
