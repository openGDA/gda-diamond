from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep

import time
class EpicsIonpClass(ScannableMotionBase):
	'''Create PD for Epics Ion Pump
	send 1 to turn on, 0 to turn off	
	'''
	def __init__(self, name, pvstartstring, pvstatusstring,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames([name+'_onoff'])
		self.setExtraNames([name+'_status'])
		self.setOutputFormat(['%.0f','%.0f'])
		self.setLevel(5)
		self.incli=CAClient(pvstartstring)
		self.incli.configure()
		self.outcli=CAClient(pvstatusstring)
		self.outcli.configure()

	def getPosition(self):
		try:
			if self.outcli.caget()=='4':
				onoff=1
			else:
				onoff=0
			return [onoff, float(self.outcli.caget())]
		except:
			print "Error returning position"
			return 0

	def asynchronousMoveTo(self,new_position):
		try:
			self.incli.caput(not(new_position))
		except:
			print "error moving to position"

	def isBusy(self):
		return 0
	


class AllPumpsOnPD(ScannableMotionBase):
	'''Create PD to check all ion pumps and turn on
	send 1 to turn on
	'''
	def __init__(self, name, pdlist,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.pdlist=pdlist
		self.setInputNames([name])
		self.setExtraNames([])
		self.setOutputFormat(['%.0f'])
		self.setLevel(5)

	def getPosition(self):
		for pump in self.pdlist:
			if pump()[0]	<0.5:
				return 0
				break
		return 1						


	def asynchronousMoveTo(self,new_position):
		if new_position==1:
			try:
				for pump in self.pdlist:		
					if pump()[0]	<0.5:	#pump is off
						pump(1);	#turn on
			except:
				print "error moving to position"
		else:
			print "=== Invalid input argument: should be 1"

	def keep_on(self):
		print "=== Start monitoring ion pump(s) at "+time.ctime()
		for i in range(9999):
			if self.getPosition()==0:
				for tries in range(10):
					print "=== Trying to start ion pump(s) at "+time.ctime()
					self.asynchronousMoveTo(1)
					sleep(10)
					if self.getPosition()==0:
						print "=== Failed to start ion pump(s) at "+time.ctime()	
					else:
						print "=== Ion pumps all on at "+time.ctime()
						break	
					sleep(300)
				if self.getPosition()==0:
					print "=== Giving up trying to turn pumps on at "+time.ctime()
					break
			else:
				sleep(300)

	def isBusy(self):
		return 0
