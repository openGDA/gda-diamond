from gda.epics import CAClient 
import java
import string 
from gda.device.scannable import PseudoDevice

from time import sleep
		
class acehead1(PseudoDevice):
	def __init__(self, name,formatstring,link,unitstring):
		self.setName(name);
		self.setLevel(3)
		self.link=link
		self.setInputNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		



	def isBusy(self):
		return 0

	def getPosition(self):
		stringa=self.link.getValue('ht')
		sleep(0.1)		
		return float(stringa)
  
