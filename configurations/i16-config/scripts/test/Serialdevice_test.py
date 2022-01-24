from gda.epics import CAClient 
import java
import string 
from gda.device.scannable import ScannableMotionBase

from time import sleep

class NormInt(ScannableMotionBase):
	def __init__(self, name,counter1,counter2,formatstring):
		self.name = name
		self.counter1=counter1
		self.counter2=counter2
		self.setOutputFormat([formatstring])
		self.setLevel(9)

	
	def isBusy(self):
		if self.counter1.isBusy() == 0 and self.counter2.isBusy() == 0:
			return 0
		else:
			return 1


	def stop(self):
		try:
			self.counter1.stop()
			self.counter2.stop()
		except:
				pass 

	def asynchronousMoveTo(self,new_position):
		self.counter1.asynchronousMoveTo(new_position)

		
	def getPosition(self):
		ccc1=self.counter1.getPosition()
		ccc2=self.counter2.getPosition()
		xxx=float(ccc1)/float(ccc2)
		return xxx


nc1=NormInt('nc1',ct3,ct4,"%6.3f")
nc2=NormInt('nc2',ct3,ct5,"%6.3f")

