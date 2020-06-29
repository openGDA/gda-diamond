from time import sleep
import java
from gda.device.scannable import ScannableMotionBase

from gda.factory import Finder

class currents2(ScannableMotionBase):

	def __init__(self, name):
		self.setName(name)
		self.setInputNames(["current5", "current6", "current7", "current8"])
		self.Units=['uA', 'uA', 'uA', 'uA']
		self.setOutputFormat(['%4.3f', '%4.3f', '%4.3f', '%4.3f'])
		self.setLevel(9)

	def isBusy(self):	
		return 0

	def getPosition(self):
		self.current5 = Finder.find("c5").getPosition()
		self.current6 = Finder.find("c6").getPosition()
		self.current7 = Finder.find("c7").getPosition()
		self.current8 = Finder.find("c8").getPosition()
		self.cs = [self.current5, self.current6, self.current7, self.current8]
		return self.cs

cu2 = currents2("currents2")
cu2.setOutputFormat(['%12.9f', '%12.9f', '%12.9f', '%12.9f'])
c5.setOutputFormat(['%12.9f'])
c5.setLevel(9)
c6.setOutputFormat(['%12.9f'])
c6.setLevel(9)
c7.setOutputFormat(['%12.9f'])
c7.setLevel(9)
c8.setOutputFormat(['%12.9f'])
c8.setLevel(9)
