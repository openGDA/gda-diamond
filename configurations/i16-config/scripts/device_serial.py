from gda.epics import CAClient 
import java
import string 

from time import sleep

class empty(java.lang.Object):
	pass


class SerialDevice:
	"""
	Class to communicate with the EPICS serial port record 
	"""

	def __init__(self,pvstring,spare1=None,spare2=None):
#		self.cacli=empty.empty()
		self.pvstring=pvstring
		self.setProperty('BAUD',9600)
		self.setProperty('DBIT',8) 
		self.setProperty('SBIT',1) 
#		self.setProperty('PRTY',"None")
		self.setProperty('OEOS',"\\n") #test if it works?
		self.setProperty('IEOS',"\\n")
#		self.setProperty('TMOD',""\\n"")
		self.spare1 =spare1
		self.spare2 =spare2
		print "Init script completed"
		 	
	def setProperty(self,name,value):
		exec('self.'+name+'=CAClient("'+self.pvstring+'.'+name+'")')
#		print 'self.'+name+'=CAClient("'+self.pvstring+'.'+name+'")'
		exec('self.'+name+'.configure()')
#		print 'self.'+name+'.caput("'+str(value)+'")'
		exec('self.'+name+'.caput("'+str(value)+'")')
		exec('self.'+name+'.clearup()')
		
	def getProperty(self,name):
		exec('self.'+name+'=CAClient('+self.cacli+'.'+name+')')
		exec('self.'+name+'.configure()')		
		exec('x=self.'+name+'.caget()')
		return x #@UndefinedVariable
		
	def sendString(self,string):
		commandstring='self.AOUT=CAClient("'+self.pvstring+'.AOUT")'
		exec(commandstring)
		self.AOUT.configure()
		self.AOUT.caput(string)
		self.AOUT.clearup()
	
	def getString(self):
		commandstring='self.TINP=CAClient("'+self.pvstring+'.TINP")'
		exec(commandstring)
		self.TINP.configure()
		stringa=self.TINP.caget()
		self.TINP.clearup() 
		return stringa

	def setIO(self,x):	 
		commandstring='self.TMOD=CAClient("'+self.pvstring+'.TMOD")'
		exec(commandstring)
		self.TMOD.configure()
		self.TMOD.caput(x)
		self.TMOD.clearup()

	