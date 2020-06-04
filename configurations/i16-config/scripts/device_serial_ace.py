from device_serial import SerialDevice
from gda.epics import CAClient 
import java
import string 

from time import sleep

class ace(SerialDevice):
	"""Create an instance of SerialDevice that allows to communicate with
	the ACE module. 
	ACE(PCname, command dictionary without the question mark)
	 """
	def __init__(self,pvstring,spare1=None,spare2=None):
		self.pvstring=pvstring
		self.setProperty('BAUD',9600)
		self.setProperty('DBIT',8) 
		self.setProperty('SBIT',1) 
#		self.setProperty('PRTY','None')
#		self.setProperty('TMOD','\n')
		self.setProperty('OEOS',"\\r\\n") #test if it works?
		self.setProperty('IEOS',"\\r\\n")
		self.spare1 =spare1
		self.spare2 =spare2
		print "Init script completed"


	def getValue(self,x):
		yyy=self.spare1[x]
		yyy="?"+yyy
#		if yyy =="?HELP":
#			self.setProperty('IEOS',"")
		self.setIO("0")
		self.sendString(yyy)
		sleep(0.2)
		self.setIO("2")
		ans=self.getString()
#		if yyy =="?HELP":
#			self.setProperty('IEOS',"\\r\\n")
		return ans

	def sendValue(self,x,value):
		yyy=self.spare1[x]
		yyy=yyy+' '+value
		self.setIO("1")
		self.sendString(yyy)
		return 

