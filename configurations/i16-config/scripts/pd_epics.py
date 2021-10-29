from pd_time import tictoc

from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

from time import sleep
from javashell import shellexecute
from org.slf4j import LoggerFactory
import misc_functions

class DisplayEpicsPVClass(ScannableMotionBase):
	'''
	Create PD to display single EPICS PV
	dev=DisplayEpicsPVClass(name, pvstring, unitstring, formatstring)
	'''
	def __init__(self, name, pvstring, unitstring, formatstring):
		self.logger = LoggerFactory.getLogger("DisplayEpicsPVClass")
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(8)
		self.cli=CAClient(pvstring)
		print self.name + " connecting to: " + pvstring
		self.cli.configure()

	def getPosition(self):
#		self.cli.configure()
		return float(self.cli.caget())
#		self.cli.clearup()

	def isBusy(self):
		return 0



class SingleEpicsPositionerClass(ScannableMotionBase):
	'''
	Create PD for single EPICS positioner
	dev=SingleEpicsPositionerClass(name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, help=None, command=None)
	'''
	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, help=None, command=None):
		self.setName(name);
		if help is not None:
			print self.__doc__
			print type(self.__doc__)
			print help
			print type(help)
			self.__doc__+='\nHelp specific to '+self.name+':\n'+str(help)
		self.setInputNames([name])
		#self.setExtraNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)

		self.delay=.5
		self.has_returned_not_busy=0
		self.has_returned_busy=0
		self.timer=tictoc()
		#print 1
		self.incli=CAClient(pvinstring)
		self.incli.configure()
		#print 2
		self.outcli=CAClient(pvoutstring)
		self.outcli.configure()
		#print 3
		self.statecli=CAClient(pvstatestring)
		self.statecli.configure()
		#print 4
		self.stopcli=CAClient(pvstopstring)
		self.stopcli.configure()
		#print 5
		self.optflag=None
		self.command=command
		if command != None:
			self.optflag =0

	def getPosition(self):
		try:
			#print 'Returned position sring: '+self.outcli.caget()
			return float(self.outcli.caget())
		except:
			print self.name + ": error returning position (SingleEpicsPositionerClass)"
			return 0

	def asynchronousMoveTo(self,new_position):
		self.has_returned_not_busy=0
		self.has_returned_busy=0
		self.timer.reset()

		if self.optflag != None:
			if self.optflag == 0:
				self.shellcommand(self.command[0])
				sleep(1)
				self.optflag = 1
		try:
			#print '#start move'
			self.incli.caput(new_position)
			#sleep(0.5)
			
		except:
			print self.name + ": error moving to position (SingleEpicsPositionerClass)"

	def isBusy(self):
		try:
			if self.has_returned_not_busy:
				#print self.getName()+'#1'
				return 0
			else:
 				self.status_string=self.statecli.caget()
				self.status=not int(float(self.status_string)) 
				if self.status:
					self.has_returned_busy=1
					#print self.getName()+'#2'
					return 1
				else:
					if self.timer()>self.delay or self.has_returned_busy:
						self.has_returned_not_busy=1
						#print self.getName()+'#3'
						return 0
					else:
						#print self.getName()+'#4'
						return 1

		except:	
			print "Device: "+self.getName()+"  Problem with DMOV string: "+self.status_string+": Returning busy status"
			return 1
	
	def stop(self):
		print "calling stop"
		self.stopcli.caput(1)


	def shellcommand(self,command):
		shellexecute(command)

	def atScanStart(self):
		if self.optflag != None:
			if self.optflag == 0:
				self.shellcommand(self.command[0])
				self.optflag =1

	def atScanEnd(self):
		if self.optflag != None:
			if self.optflag == 1:
				self.shellcommand(self.command[0])
				self.optflag =0


class SingleEpicsPositionerNotDmovClass(SingleEpicsPositionerClass):
	'''
	Create PD for single EPICS positioner
	dev=SingleEpicsPositionerNotDmovClass(name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, help=None, command=None)
	As SingleEpicsPositionerClass but invertig status in case busy PV used instead of DMOV
	'''
	def isBusy(self):
		try:
			if self.has_returned_not_busy:
				#print self.getName()+'#1'
				return 0
			else:
 				self.status_string=self.statecli.caget()
				#self.status=not int(float(self.status_string)) 
				self.status=int(float(self.status_string)) 
				if self.status:
					self.has_returned_busy=1
					#print self.getName()+'#2'
					return 1
				else:
					if self.timer()>self.delay or self.has_returned_busy:
						self.has_returned_not_busy=1
						#print self.getName()+'#3'
						return 0
					else:
						#print self.getName()+'#4'
						return 1

		except:	
			print "Device: "+self.getName()+"  Problem with DMOV string: "+self.status_string+": Returning busy status"
			return 1


class SingleEpicsPositionerNotDmovClassDirtyPiezo(SingleEpicsPositionerClass):
	'''
	Create PD for single EPICS positioner
	dev=SingleEpicsPositionerNotDmovClass(name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, help=None, command=None)
	As SingleEpicsPositionerClass but invertig status in case busy PV used instead of DMOV
	======= Dirty fix for piezo
	'''
	def isBusy(self):
		misc_functions.caget('BL16I-MO-PIEZO-03:MMC:01:ACT:RBV.PROC')	# dirty fix for piezo ststus problem
		misc_functions.caget('BL16I-MO-PIEZO-03:MMC:02:ACT:RBV.PROC')	# dirty fix for piezo ststus problem
		try:
			if self.has_returned_not_busy:
				#print self.getName()+'#1'
				return 0
			else:
 				self.status_string=self.statecli.caget()
				#self.status=not int(float(self.status_string)) 
				self.status=int(float(self.status_string)) 
				if self.status:
					self.has_returned_busy=1
					#print self.getName()+'#2'
					return 1
				else:
					if self.timer()>self.delay or self.has_returned_busy:
						self.has_returned_not_busy=1
						#print self.getName()+'#3'
						return 0
					else:
						#print self.getName()+'#4'
						return 1

		except:	
			print "Device: "+self.getName()+"  Problem with DMOV string: "+self.status_string+": Returning busy status"
			return 1


		
class SingleEpicsPositionerNoStatusClass(SingleEpicsPositionerClass):
	'''
	Class for PD devices without status
	same parameters as SingleEpicsPositionerClass but status not used. Must give a valid PV for status to avoid error during configure
	'''

	def isBusy(self):
		return 0

#####these methods commented out by spc 14/9/08 - didn't understand what they were for but might need them if something stops working
#	def asynchronousMoveTo(self,new_position):
#		try:
#			self.new_position=new_position	# need this attribute for some other classes
#			self.incli.configure()
#			self.statecli.configure()
#			self.incli.caput(new_position)
#			self.statecli.caput('0')
#			self.incli.clearup()
#			self.statecli.clearup()
#			sleep(0.5)
#		except:
#			print "error moving to position"


#sleeptime added as key word spc 14/9/08 to remove default 0.5 sec sleep time. Include sleep time at initialization if this causes a problem
class SingleEpicsPositionerSetAndGetOnlyClass(ScannableMotionBase):
	'''
	Create PD for single EPICS positioner which respond only to set and get i.e. no status or stop
	dev=SingleEpicsPositionerSetAndGetOnlyClass(name, pvinstring, pvoutstring, unitstring, formatstring,help=None,sleeptime=0)
	waits for sleeptime (sec) after sending new parameter
	'''
	def __init__(self, name, pvinstring, pvoutstring, unitstring, formatstring,help=None,sleeptime=0):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.incli=CAClient(pvinstring)
		self.incli.configure()
		self.outcli=CAClient(pvoutstring)
		self.outcli.configure()
		self.sleeptime=sleeptime
		
	def getPosition(self):
		try:
			#print 'Returned position sring: '+self.outcli.caget()
			return float(self.outcli.caget())
		except:
			print "Error returning position"
			return 0

	def asynchronousMoveTo(self,new_position):
		try:
			self.incli.caput(new_position)
			sleep(self.sleeptime)
		except:
			print "error moving to position"

	def isBusy(self):
		return 0

class SingleEpicsPositionerNoStatusClass2(SingleEpicsPositionerNoStatusClass):
	'''
	EPICS device that obtains a status from the actual position vs command position
	same parameters as SingleEpicsPositionerNoStatusClass but uses deadband attribute which must be set after initialization
	'''
	def isBusy(self):
		try:
			if abs(self.new_position-self())<self.deadband:
				return 0
			else:
				return 1
		except:
			print 'Warning - can''t get isBusy status. Perhaps new_position or deadband attrubutes not set?'
			return 0


class Epics_Shutter(ScannableMotionBase):
	'''Create PD for single EPICS shutter'''
	def __init__(self, name, pvstring):
		self.setName(name);
		self.setInputNames([name])
		self.setOutputFormat(['%.0f'])
		self.setLevel(3)
		self.pvstring=pvstring
		self.cli=CAClient(self.pvstring)
		self.cli.configure()

	def getPosition(self):

		self.state=self.cli.caget()
		if self.state=='0':
			print "Shutter open"
			return 1
		elif self.state=='1':
			print "Shutter closed"
			return 0
		elif self.state=='2':
			print "Shutter closed waiting for Reset"
			return 0
		else:
			print "Unknown state:",self.state
			raise

	def asynchronousMoveTo(self,new_position):
		if new_position>0.5:
			self.cli.caput('Reset')
			sleep(.5)
			self.cli.caput('Open')
		else:
			self.cli.caput('Close')
	def isBusy(self):
		return 0


class epics_binary_pos_neg(SingleEpicsPositionerSetAndGetOnlyClass):
	'''

	'''
	def bin_to_posneg(self, bin):
		if bin:
			posneg=+1
		else:
			posneg=-1
		return posneg

	def posneg_to_bin(self, posneg):
		if posneg>0:
			bin=True
		else:
			bin=False
		return bin
	
	def getPosition(self):
		try:
			#print 'Returned position sring: '+self.outcli.caget()
			return self.bin_to_posneg(float(self.outcli.caget()))
		except:
			print "Error returning position"
			return 0

	def asynchronousMoveTo(self,new_position):
		try:
			self.incli.caput(self.posneg_to_bin(new_position))
			#sleep(self.sleeptime)
		except:
			print "error moving to position"
