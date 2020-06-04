from time import sleep
import java
from gda.device.scannable import ScannableMotionBase

from gda.factory import Finder

class currents(ScannableMotionBase):

	def __init__(self, name):
		self.setName(name)
		self.setInputNames(["current1", "current2", "current3", "current4"])
		self.Units=['uA', 'uA', 'uA', 'uA']
		self.setOutputFormat(['%4.3f', '%4.3f', '%4.3f', '%4.3f'])
		self.setLevel(9)

	def isBusy(self):	
		return 0

	def getPosition(self):
		self.current1 = Finder.getInstance().find("c1").getPosition()
		self.current2 = Finder.getInstance().find("c2").getPosition()
		self.current3 = Finder.getInstance().find("c3").getPosition()
		self.current4 = Finder.getInstance().find("c4").getPosition()
		self.cs = [self.current1, self.current2, self.current3, self.current4]
		return self.cs

c = currents("currents")
c.setOutputFormat(['%12.9f', '%12.9f', '%12.9f', '%12.9f'])
c1.setOutputFormat(['%12.9f'])
c1.setLevel(9)
c2.setOutputFormat(['%12.9f'])
c2.setLevel(9)
c3.setOutputFormat(['%12.9f'])
c3.setLevel(9)
c4.setOutputFormat(['%12.9f'])
c4.setLevel(9)
