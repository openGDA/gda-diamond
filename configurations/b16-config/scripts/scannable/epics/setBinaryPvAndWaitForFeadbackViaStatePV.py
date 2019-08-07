from gda.device.scannable import PseudoDevice
from gda.epics import CAClient 
import time

class SetBinaryPvAndWaitForFeadbackViaStatePV(PseudoDevice):

	""" This is the constructor for the class. """
	def __init__(self, name, pvTrigger, pvState, timeout):
		self.name = name
		self.setInputNames([name])
		self.setOutputFormat(['%d'])
		
		self.moveTriggeredTime = 0
		self.timeout = timeout

		self.trigger = CAClient(pvTrigger)
		self.state = CAClient(pvState)
		self.configure()

		self.destinationState = self.getPosition()

	def configure(self):
		self.trigger.configure()
		self.state.configure()

	def asynchronousMoveTo(self, dest):
		dest = (1 and dest) # Make it binary
		self.trigger.caput(dest)
		self.destinationState = dest
		self.moveTriggeredTime = time.time()

	def getPosition(self):		
		pos=self.state.caget()
		if pos=='1':
			return 1
		elif pos=='0':
			return 0
		else:
			raise Exception("Expected 0 or 1 for getPosition but got: {} (device={}, pvTrigger={}, pvState={})".format(pos, self.name, self.trigger.getPvName(), self.state.getPvName()))

	def isBusy(self):
		if time.time() > (self.moveTriggeredTime + self.timeout):
			raise Exception("Request to move device=%s, via pvTrigger=%s and pvState=%s to position=%s timed-out after %fs" % (self.name, self.trigger.getPvName(), self.state.getPvName(), self.destinationState, self.timeout))

		return self.getPosition() != self.destinationState






