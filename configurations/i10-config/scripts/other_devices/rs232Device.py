""" #########################################################################################################
Pseudo device which allows communication with rs232 devices on the user patch pannel.
provides: read, write and query.

With python reading and querying an rs232 device is done with callbacks. 
With Jython it is just forcing a delay between writing and reading.

David Burn - 1/4/16

######################################################################################################### """


from other_devices.epicsDevice_v4 import device
import os
import time

class rs232Device:
	def __init__(self, branch, port, baud=9600, ieos='\r', oeos='\r' ):
		if branch == "I":
			self.ser = device("BL10I-EA-USER-01")
		else:
			self.ser = device("BL10J-EA-USER-01")
			
		self.port = port
		if (os.name != "java"): self.ser.addCallback(self.port+".TINP", self.readCallback)		# read callback
		self.readValue=None
		self.ioMode=None							#1=write, 2=read

		self.waitTimeAfterWrite = 0.1
		
		self.ser.caput(self.port+".BAUD", baud)
		self.ser.caput(self.port+".IEOS", ieos)
		self.ser.caput(self.port+".OEOS", oeos)

	def flush(self):
		self.ser.caput(self.port+".TMOD", "Flush")
		self.ser.caput(self.port+".PROC", 1)					#process
		time.sleep(0.1)


	def write(self, string):
		self.ser.caput(self.port+".TMOD", 1)					#set to write mode
		self.ser.caput(self.port+".AOUT", string)
		time.sleep(self.waitTimeAfterWrite)

	def read(self):	
		self.readValue=None
		self.ser.caput(self.port+".TMOD", 2)					#set to read mode
		self.ser.caput(self.port+".PROC", 1)					#process

		while self.readValue==None:
			if (os.name == "java"): self.dummyCallback()
			time.sleep(0.1)
			#print self.ser.caget(self.port+".SEVR")
			#print type(self.ser.caget(self.port+".SEVR"))
			if int(self.ser.caget(self.port+".SEVR")) == 2:		#major
				#print "major"
				self.ser.caput(self.port+".PROC", 1)		
				#time.sleep(1)
		return self.readValue


	def query(self, request):
		
		self.readValue=None
		self.ser.caput(self.port+".TMOD", 0)					#set to read and write mode

		self.ser.caput(self.port+".AOUT", request)
		
		if (os.name == "java"): self.dummyCallback()
		while self.readValue==None:
			time.sleep(0.01)
		return self.readValue	


	def readCallback(self, value=None, **kws):
		#print "read callback, value= ", value		
		if value != "":
			self.readValue = value

		
			
		

	""" use a dummy callback when running in gda as gda epics callbacks are not implemented """
	def dummyCallback(self):
		time.sleep(0.8)
		#print "dummy callback"
		value = self.ser.caget(self.port+".TINP")
		if int(self.ser.caget(self.port+".SEVR")) != 2:	#major
			if value != "":
				self.readValue = value
		
	

	def setInputTerminator(self, terminator):
		self.ser.caput(self.port+".IEOS", terminator)
		#print self.port+".IEOS", terminator
		
	def setOutputTerminator(self, terminator):
		self.ser.caput(self.port+".OEOS", terminator)

