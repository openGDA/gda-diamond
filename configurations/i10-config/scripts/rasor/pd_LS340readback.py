from gda.device.scannable import PseudoDevice
from misc_functions import caput, caget, frange
from time import sleep

class DisplayEpicsPVClassLS(PseudoDevice):
	def __init__(self, name, pvstring, unitstring, formatstring,channel,level):
		self.setName(name);
		self.setInputNames([])
#		self.setExtraNames([name+'Sensor']);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
#		self.setOutputFormat([formatstring,formatstring])
		self.setLevel(level)
		self.pvstring=pvstring
		self.channel=channel

	def getPosition(self):
		return float(caget(self.pvstring+'KRDG'+self.channel))
		
	def isBusy(self):
		sleep(0.1)
		return 0




class DisplayEpicsPVClassLS2(PseudoDevice):
	def __init__(self, name, pvstring, unitstring, formatstring,channel,level):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name+'S']);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setOutputFormat([formatstring,formatstring])
		self.setLevel(level)
		self.pvstring=pvstring
		self.channel=channel

	def getPosition(self):
		return [float(caget(self.pvstring+'KRDG'+self.channel)),float(caget(self.pvstring+'SRDG'+self.channel))]
		
	def isBusy(self):
		sleep(0.05)
		return 0

class DisplayEpicsPVLakeshoreTemperatureInCelsius(PseudoDevice):
	def __init__(self, name, pvstring, unitstring, formatstring,channel,level):
		self.setName(name);
		self.setInputNames([])
#		self.setExtraNames([name+'S']);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
#		self.setOutputFormat([formatstring,formatstring])
		self.setLevel(level)
		self.pvstring=pvstring
		self.channel=channel

	def getPosition(self):
		return float(caget(self.pvstring+'CRDG'+self.channel))
		
	def isBusy(self):
		sleep(0.1)
		return 0
