
from gda.device.scannable import ScannableMotionBase

from time import sleep
		
class x2000scaClass(ScannableMotionBase):
	def __init__(self, name,formatstring,link,unitstring):
		self.setName(name);
		self.setLevel(9)
		self.link=link
		self.setInputNames([name,name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring,formatstring])
		
	def asynchronousMoveTo(self,new_position):
		self.link.sendValue('scalow',str(new_position[0]))
		sleep(0.3)
		self.link.sendValue('scaupp',str(new_position[1]))
				
	def getPosition(self):
		xxx=[]
#		try:
		self.link.getValue('scalow')			
		self.link.getValue('scalow')			
		xxx.append(float(self.link.getValue('scalow')))
		self.link.getValue('scaupp')			
		self.link.getValue('scaupp')			
		xxx.append(float(self.link.getValue('scaupp')))
		return xxx
#		except:
#			print "Error returning position"
#			return [-1, -1]
			
	def isBusy(self):
		return 0
