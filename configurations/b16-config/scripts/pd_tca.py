from gda.epics import CAClient 
from java import lang
from gda.device.scannable import ScannableMotionBase

from time import sleep


class tcasca(ScannableMotionBase):
	def __init__(self, name,formatstring,tcaDevice,unitstring,roiNumber):
		self.setName(name);
		self.setLevel(3)
		self.tcaDevice=tcaDevice
		self.setInputNames([name+'_low',name+'_hi'])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring,formatstring])
		self.roiNumber=roiNumber
		self.on()
		
	def asynchronousMoveTo(self,new_position):
		if new_position[0] >= new_position[1]:
			print "error: wrong values"
		else:
			self.tcaDevice.setProperty('SCA'+self.roiNumber+'_LOW',new_position[0])
			self.tcaDevice.setProperty('SCA'+self.roiNumber+'_HI',new_position[1])


	def isBusy(self):
		return 0

	def getPosition(self):
		scalow=self.tcaDevice.getProperty('SCA'+self.roiNumber+'_LOW')
		scahi=self.tcaDevice.getProperty('SCA'+self.roiNumber+'_HI')
		return [float(scalow), float(scahi)]

	def on(self):
		stringa='SCA'+self.roiNumber+'_GATE'
		self.tcaDevice.setProperty(stringa,1)
		return self.tcaDevice.getProperty(stringa)


	def off(self):
		stringa='SCA'+self.roiNumber+'_GATE'
		self.tcaDevice.setProperty(stringa,0)
		return self.tcaDevice.getProperty(stringa)

