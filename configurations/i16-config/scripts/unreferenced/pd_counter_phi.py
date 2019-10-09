from pd_time import tictoc

from gda.epics import CAClient 
from gda.device.scannable import PseudoDevice

from time import sleep
from javashell import shellexecute
import misc_functions


class pd_counter_phi(PseudoDevice):
	'''
	Create PD for single EPICS positioner
	dev=SingleEpicsPositionerClass(name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, help=None, command=None)
	'''
	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring, elp=None, command=None):
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
		self.setLevel(6)

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
			self.optflag 


	def getPosition(self):
		try:
			#print 'Returned position sring: '+self.outcli.caget()
			return float(self.outcli.caget())
		except:
			print self.name + ": error returning position (SingleEpicsPositionerClass)"
			return 0


	def setlink(self,link,offset=0):	
		self.motortocounter=link
		self.myoffset=offset
		




	def asynchronousMoveTo(self,new_position=0):	
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
			self.incli.caput(new_position-self.motortocounter.getPosition()+self.myoffset)
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



counterphi=pd_counter_phi('counterphi','BL16I-MO-XPS3-01:P1.VAL','BL16I-MO-XPS3-01:P1.RBV','BL16I-MO-XPS3-01:P1.DMOV','BL16I-MO-XPS3-01:P1.STOP','deg','%.4f')
