from gda.epics import CAClient 
from gdascripts.utils import caget
from gdascripts.utils import caput



class EpicsAsynSerialInterface:
	"""
	Class to communicate with the EPICS serial port record 
	
	>>> export EPICS_DISPLAY_PATH=/dls_sw/prod/R3.14.8.2/support/asyn/4-9/medm
	>>> medm -x -macro "P=BL16B-EA-ACE-01,R=:ASYN" asynRecord.adl & 
	
	"""
	def __init__(self, pvstring, baudrate=None, databits=None, stopbits=None, parity=None, outterm=None, interm=None):
		
		self.pvstring = pvstring
		self.outChannel = None
		self.inChannel  = None
		
		if baudrate is not None:
			self.setProperty('BAUD', baudrate)		
		if databits is not None:
			self.setProperty('DBIT', databits)		
		if stopbits is not None:
			self.setProperty('SBIT', stopbits)
		if parity is not None:
			self.setProperty('PRTY', parity)		
		if outterm is not None:
			self.setProperty('OEOS', outterm)		
		if parity is not None:
			self.setProperty('IOES', interm)		

	def configure(self):
		"""Creates epics channels for input and output string fields.  Configures serial port
		if any optional parameters are given.  Otherwise defaults to the ioc's configuration."""
		self.outChannel = CAClient(self.pvstring + ".AOUT")
		self.outChannel.configure()
		self.inChannel  = CAClient(self.pvstring + ".TINP")
		self.inChannel.configure()
		
	def clearup(self):
		"""Does nothing to async record, but closes the ca channels used to read and write strings.
		"""
		self.outChannel.clearup()
		self.inChannel.clearup()	 
	
	def isConfigured(self):
		return ( self.outChannel.isConfigured() and self.inChannel.isConfigured() )

	def setProperty(self,name,value):
		caput(self.pvstring+ '.' +name, value)
		
	def getProperty(self,name):
		return caget(self.pvstring+ '.' +name)
		
	def sendString(self,string):
		"""Sends a string. Run configure() method to create channel first"""
		if self.outChannel==None:
			raise Exception, "before calling sendString() on this EpicsAsysnSerialInterface object first call configure() to open the epics channels"
		self.outChannel.caput(string)
	
	def getString(self):
		if self.inChannel==None:
			raise Exception, "before calling getString() on this EpicsAsysnSerialInterface object first call configure() to open the epics channels"
		return self.inChannel.caget()




