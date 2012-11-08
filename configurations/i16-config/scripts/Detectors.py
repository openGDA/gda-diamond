from gda.epics import CAClient 
import java
import string 
from gda.device.scannable import PseudoDevice


class Detectors(PseudoDevice):
	def __init__(self,name,monitor1,monitor2,defcounter):
		self.setName(name)
		self.setInputNames([name])
 		self.monitor1=monitor1
		self.monitor2=monitor2
		self.setExtraNames([self.monitor1.name,self.monitor2.name,'ctime'])
		self.setOutputFormat(['%4.4f','%4.4f','%4.4f','%4.4f'])
 		self.counter = defcounter
		self.setLevel(self.counter.getLevel())
		self.new_position=None

	def setCounter(self,x):
		self.counter=x

	def asynchronousMoveTo(self,new_position):
		self.new_position=new_position
		self.counter.asynchronousMoveTo(new_position)

	def getPosition(self):
		if self.new_position == None:
			self.new_position=0
		return [self.counter.getPosition() self.monitor1() self.monitor2() self.new_position ]
		 

	def isBusy():
		if self.counter.isBusy() == 0:
			return 0
		if self.counter.isBusy() == 1:
			return 1

det=Detectors('det',ic1,ic2,ct3)