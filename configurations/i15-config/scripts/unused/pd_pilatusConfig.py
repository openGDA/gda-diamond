from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep
class PilatusGain(ScannableMotionBase):
	'''Pilatus config PD
	inputs: threshhold energy (eV), gain (0-3)
	gain 0 = fast rate/low gain
	gain 1 = medium rate/medium gain (normal setting)
	gain 2 = slow rate/high gain
	gain 3 = slow rate/Ultrahigh gain
	'''

	def __init__(self,name,pvroot):
		self.setName(name);
		self.setInputNames(['Gain'])
		self.setExtraNames([]);
		self.setOutputFormat(['%.0f'])
		self.setLevel(5)
		self.ClientRoot=pvroot

		self.CAGain=CAClient(self.ClientRoot+'Gain'); self.CAGain.configure()

	def isBusy(self):
		return 0

	def getPosition(self):
		return float( self.CAGain.caget())

	def asynchronousMoveTo(self,thresh_gain):
		self.CAGain.caput(thresh_gain)
		sleep(0.5)


class PilatusThreshold(ScannableMotionBase):
	'''Pilatus config PD

	'''

	def __init__(self,name,pvroot):
		self.setName(name);
		self.setInputNames(['Threshold'])
		self.setExtraNames([]);
		self.setOutputFormat(['%.0f'])
		self.setLevel(5)
		self.ClientRoot=pvroot

		self.CAThresholdEnergy=CAClient(self.ClientRoot+'ThresholdEnergy'); self.CAThresholdEnergy.configure()

	def isBusy(self):
		return 0

	def getPosition(self):
		return float(self.CAThresholdEnergy.caget())

	def asynchronousMoveTo(self,thresh_gain):
		self.CAThresholdEnergy.caput(thresh_gain)
		sleep(0.5)



