from gda.device.scannable import ScannableMotionBase
from gda.device import DeviceException
from gda.epics import CAClient
import time

OK_RESPONSE = "Command execution OK"

class BimorphCaenels(ScannableMotionBase):

	def __init__(self, name, channels, pv_prefix, channel_format, set_target_suffix):
		self.name = name
		self.pv_prefix = pv_prefix
		self.channel_format = channel_format
		self.channels = list(channels)
		self.set_target_suffix = set_target_suffix
		self.ca = CAClient()

		self.inputNames = ["CH%d" % c for c in channels]
		self.extraNames = []
		self.outputFormat = ["%5.5g"] * (len(self.inputNames) + len(self.extraNames))

	def isBusy(self):
		return int(self.ca.caget(self.pv_prefix + "BUSY")) != 0

	def getPosition(self):
		return [float(self.ca.caget((self.pv_prefix + self.channel_format + ":VOUT_RBV") % c)) for c in self.channels]

	def asynchronousMoveTo(self, target):
		for c, v in zip(self.channels, target):
			self.ca.caput((self.pv_prefix + self.channel_format + ":VTRGT") % c, v)
			self.waitForBusy(5)
			self.waitWhileBusy()
		self.ca.caput(self.pv_prefix + self.set_target_suffix, 1)
		self.waitForBusy(5)

	def moveOne(self, channel, target):
		self.ca.caput((self.pv_prefix + self.channel_format + ":VTRGT") % channel, target)
		self.waitForBusy(5)
		self.waitWhileBusy()
		self.ca.caput(self.pv_prefix + self.set_target_suffix, 1)
		self.waitForBusy(5)
		self.waitWhileBusy()

	def getResponse(self):
		response_string = self.ca.caget(self.pv_prefix + "RESPONSE")
		return response_string

	def isError(self):
		return self.getResponse() != OK_RESPONSE

	def raiseIfError(self):
		response = self.getResponse()
		if response != OK_RESPONSE: raise DeviceException(response)

	def waitForBusy(self, timeout):
		start_time = time.time()
		while time.time() < start_time + timeout:
			if self.isBusy(): return
		else:
			raise DeviceException("Device did not respond within timeout")
