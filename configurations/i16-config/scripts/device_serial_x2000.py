from device_serial import SerialDevice
from gda.epics import CAClient 
import java
import string 

from time import sleep

class x2000class(SerialDevice):
	"""Create an instance of SerialDevice that allows to communicate with
	the x2000 module.
	x2000(PVname, ack string, command dictionary without the question mark) 
	 """

	def getValue(self,x):
		yyy=self.spare2[x]
		yyy=yyy+"?"
		self.setIO("0")
		self.sendString(yyy)
		sleep(0.5)
#		print self.getString()
		ans=self.getString()
		ans=ans[len(self.spare1):-2] ## Changed from x2000.spare1
		return ans

	def sendValue(self,x,value):
		yy=self.spare2[x]
		yy=yy+' '+value
		self.setIO("1")
		self.sendString(yy)
		return 


