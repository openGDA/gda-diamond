from pd_time import tictoc

from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase

from time import sleep
from javashell import shellexecute
import misc_functions




class SingleEpicsPositionerClassSticky(ScannableMotionBase):
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
			tolerance=20
			counter=0
			while abs(new_position-self.getPosition()) >tolerance and counter<10: 
				self.incli.caput(new_position)
				w(.5)
				counter+=1


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


Aziz=SingleEpicsPositionerClassSticky('Aziz','BL16I-MO-ANC-01:P2.VAL','BL16I-MO-ANC-01:P2.RBV','BL16I-MO-ANC-01:P2.DMOV ','BL16I-MO-ANC-01:P2.STOP ','mm','%.4f')
Azix=SingleEpicsPositionerClassSticky('Azix','BL16I-MO-ANC-01:P3.VAL','BL16I-MO-ANC-01:P3.RBV','BL16I-MO-ANC-01:P3.DMOV ','BL16I-MO-ANC-01:P3.STOP ','mm','%.4f')




