from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep
import threading


class delayedGetPositionScannable(ScannableMotionBase):
	"""
		Get position will block and return position only after time defined as delay_time in seconds.
		Scannable level is set to 6.

		Parameters
			name - name of the new scannable as string
			pvstring - PV address as a string
			unitstring - units if any as string
			formatstring - format string
			delay_time - delay time in seconds

		Example:
			ts = delayedGetPositionScannable("ts","ws410-AD-SIM-01:STAT:UniqueId_RBV"," ", "%f",5)
	"""
	def __init__(self, name, pvstring, unitstring, formatstring, delay_time=0.0):
		self.setName(name);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.outcli=CAClient(pvstring)
		self.delayTime = delay_time
		self.thread = threading.Thread(target=self.worker)
		self.setLevel(6)

	def worker(self):
		sleep(self.delayTime)

	def rawGetPosition(self):
		if not self.outcli.isConfigured():
			self.outcli.configure()
		self.thread = threading.Thread(target=self.worker)
		self.thread.start()
		self.thread.join()
		return float(self.outcli.caget())

	def rawAsynchronousMoveTo(self, position):
		return

	def isBusy(self):
		return self.thread.is_alive()
