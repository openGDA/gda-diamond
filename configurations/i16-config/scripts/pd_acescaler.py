from gda.epics import CAClient 
import java
import string 
from gda.device.scannable import ScannableMotionBase

from time import sleep
		
class acesca1(ScannableMotionBase):
	def __init__(self, name,formatstring,link,unitstring):
		self.setName(name);
		self.setLevel(3)
		self.link=link
		self.setInputNames([name+'low',name+'win'])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring,formatstring])
		
	def asynchronousMoveTo(self,new_position):
#		print new_position
		stringa = "WIN "+str(new_position[0])+" "+  str(new_position[1]) 
#		print stringa 
		self.link.sendValue('sca',stringa)


	def isBusy(self):
		return 0

	def getPosition(self):
		stringa=self.link.getValue('sca')
		print stringa
#		stringa=stringa.split()
#remove special chars in case interface is not set to remove them
		stringa=stringa.replace('\\',' ').split();		
		return [float(stringa[1]), float(stringa[2])]
