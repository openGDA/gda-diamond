from gda.device.scannable import ScannableMotionBase
from gda.device import DeviceException
import time

class Shutter(ScannableMotionBase):
	
	def __init__(self, name, enumPositioner ):
		self.setName(name)
		self.setInputNames([name])
		self.setOutputFormat(['%i'])
		self.positioner = enumPositioner
		
	def asynchronousMoveTo(self, state):
		# blocks while moving
		if state == 0:
			self.positioner.moveTo('Close')
		elif state == 1:
			self.positioner.moveTo('Reset')
			self.positioner.moveTo('Open')
		else:
			raise ValueError("Could no move %s to %s, Position must be '1' for open or '0' for closed" % self.name, state)
		
	def getPosition(self):
		pos_string = str(self.positioner.getPosition())
		if pos_string == 'Fault':
			raise Exception("\n** Problem with " + self.name + ": the shutter is returning a status of 'Fault' **")
		return {'Open': 1, 'Closed': 0, 'Reset': 0}[pos_string]

	def isBusy(self):
		return False
		

class DummyEpicsShutterPositioner:
	
	def __init__(self):
		self.state = 'Close'
		
	def getPosition(self):
		return self.state
	
	def moveTo(self, state):
		if state not in('Open', 'Close', 'Reset'):
			raise ValueError()
		if state == 'Close':
			self.state = 'Closed'
		else:
			self.state = state
		time.sleep(.2)
		