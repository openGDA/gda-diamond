from gda.device.scannable import PseudoDevice
from time import sleep
import java, sys, time, traceback
from pd_epics import DisplayEpicsPVClass

class WaitForBeamPDClass(PseudoDevice):
	'''
	PD to wait for beam during scan
	Returns 1 if beam OK
	If beam lost then wait for beam and return 0 to indicate a beam trip
	Fill cryocooler if necessary
	self.min is the attribute containing the min value
	self.sleeptime is the time to wait between samples
	if self.command_string is a valid command string then it is executed while waiting for the beam
	'''
	def __init__(self, name,pd_to_monitor, minval):
		self.setName(name);
		self.setInputNames([])
		self.pd=pd_to_monitor
		self.setExtraNames(['beamOK']);
		self.Units=[]
		self.setOutputFormat(['%.0f'])
		self.setLevel(6)
		self.min=minval
		self.lastcheck=1
		self.sleeptime=30

	def getPosition(self):
		#print "WaitForBeamPDClass.getPosition() called"
		while 1:
			if self.pd()>self.min:
				if self.lastcheck==1:
					return 1
				else:
					self.lastcheck=1
					print '===  Beam back on: '+time.ctime()
					return 0
			else:
				self.lastcheck=0
				print '===  Waiting for beam on: '+time.ctime()
#				if cryolevel()<60:
#					dofill()
#					print '=== Filling Cryocooler vessel'
#					sleep(self.sleeptime)
				#next two lines replace previous section and allow more flexibillity. change back if problem
				eval(self.command_string)
				sleep(self.sleeptime)

	def isBusy(self):
		return 0	

	def atScanStart(self):
		print '===Beam checking is enabled: '+self.pd.getName()+' must exceed '+str(self.min)
		self.lastcheck=1

class TimeToMachineInjectionClass(DisplayEpicsPVClass):
	'''
	PD to return time till next injection (seconds)
	Returns 99999 if not in top-up mode
	Returns 88888 on any other error (such as failing to read the PV) - TODO: Remove this workaround
	Parameters as per DisplayEpicsPVClass
	'''
	'''Create PD to display single EPICS PV'''

	def getPosition(self):
		try:
			self.timetoinjection=float(self.cli.caget())
		except java.lang.IllegalStateException, e:
			# Error when injection disabled?
			print "Problem in %s.getPosition() timetoinjection was %f raising Exception" % (self.getName(), self.timetoinjection)
			self.logger.error("{}.getPosition() IllegalStateException while getting timetoinjection (was {}): ", self.getName(), self.timetoinjection, e)
			raise Exception("Problem in %s.getPosition():" % self.getName() ,e)
		except:
			print "Problem in %s.getPosition() timetoinjection was %f returning 88888" % (self.getName(), self.timetoinjection)
			self.logger.error("{}.getPosition() exception while getting timetoinjection (was {} now 88888):\n {}",
							self.getName(), self.timetoinjection, ''.join(traceback.format_exception(*sys.exc_info())))
			self.timetoinjection=88888

		if self.timetoinjection>=0:
			return self.timetoinjection
		else:
			return 99999


class WaitForInjectionPDClass(PseudoDevice):
	'''
	PD to wait for beam injection during top-up mode
	dev=WaitForInjectionPDClass(name, time_to_injectio_PV, due_time(sec), waitfor_time(sec) )
	waits if injection is due within min_time (self.due)
	'''
	def __init__(self, name,pd_to_monitor, due, waitfor):
		self.setName(name);
		self.setInputNames([])
		self.pd=pd_to_monitor
#		self.setExtraNames(['Injection']);
		self.Units=[]
#		self.setOutputFormat(['%.0f'])
		self.setOutputFormat([])
		self.setLevel(6)
		self.due=due
		self.waitfor=waitfor
		self.message_displayed=0

	def getPosition(self):
		#print "WaitForBeamPDClass.getPosition() called"		
		if self.pd()>self.due:
			return
		else:
			while 1:
				if self.pd()>self.due:
					self.message_displayed=0
					sleep(self.waitfor)
					return
				else:
					if self.message_displayed==0:
						print '===  Waiting for injection on: '+time.ctime()
						self.message_displayed=1
					sleep(.5)

	def isBusy(self):
		return 0	

	def atScanStart(self):
		print '===Injection mode pausing is enabled: '+self.pd.getName()+' must exceed '+str(self.due) 

class WaitForInjectionPDClass2(PseudoDevice):
	'''
	PD to wait for beam injection during top-up mode
	dev=WaitForInjectionPDClass(name, time_to_injectio_PV, due_time(sec), waitfor_time(sec) )
	waits if injection is due within min_time (self.due)
	This version gives the min time before injection (allow_time)
	'''
	def __init__(self, name,pd_to_monitor, due, waitfor):
		self.setName(name);
		self.setInputNames([])
		self.pd=pd_to_monitor
		self.setExtraNames(['allow_time']);
		self.Units=[]
		self.setOutputFormat(['%.1f'])
		self.setOutputFormat([])
		self.setLevel(6)
		self.due=due
		self.waitfor=waitfor
		self.message_displayed=0

	def getPosition(self):
		#print "WaitForBeamPDClass.getPosition() called"		
		if self.pd()>self.due:
			return self.due
		else:
			while 1:
				if self.pd()>self.due:
					self.message_displayed=0
					sleep(self.waitfor)
					return self.due
				else:
					if self.message_displayed==0:
						print '===  Waiting for injection on: '+time.ctime()
						self.message_displayed=1
					sleep(.5)

	def isBusy(self):
		return 0	

	def atScanStart(self):
		print '===Injection mode pausing is enabled: '+self.pd.getName()+' must exceed '+str(self.due) 
