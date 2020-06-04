from gda.device.scannable import ScannableMotionBase

class Simple_PD_EpicsDevice(ScannableMotionBase):
	def __init__(self, name, beamline, pv):
		self.setName(name);
		self.chan = beamline.createEpicsChannel(None,"Top",pv,30)

	def isBusy(self):
		return 0

	def getPosition(self):
		return self.chan.getValue()

	def asynchronousMoveTo(self, newPos):
		self.chan.setValue(newPos)		 	