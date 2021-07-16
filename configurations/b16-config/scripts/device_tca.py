from gda.epics import CAClient 
from java import lang
from gdascripts.utils import caput
from gdascripts.utils import caget
from time import sleep

class TCA:
	def __init__(self,pvstring):
		self.pvstring=pvstring
		
	def setDefaults(self):
		self.setProperty('POLARITY',0)
		self.setProperty('THRESHOLD',0)
		self.setProperty('SCA_ENABLE',0)
		self.setProperty('READBACK.SCAN',4)
		self.setProperty('PUR_ENABLE',0)
		self.setProperty('PUR_AMP',0)
		self.setProperty('TCA_SELECT',0)
		self.setProperty('SCA1_GATE',0)
		self.setProperty('SCA2_GATE',0)
		self.setProperty('SCA3_GATE',0)
		self.setProperty('SCA1_PUR',0)
		self.setProperty('SCA2_PUR',0)
		self.setProperty('SCA3_PUR',0)
	
	def setProperty(self,name,value):
        		caput(self.pvstring+name,value)

	
	def getProperty(self,name):
        		return caget(self.pvstring+name)