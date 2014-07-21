from gda.device import Scannable
from gda.device.scannable import ScannableBase
from gda.epics import CAClient
from java import lang
from java.lang import Thread
from time import sleep

delayTime = 1
 
class DisplayEpicsPVClass(ScannableBase):
	'''Create PD to display single EPICS PV'''
	def __init__(self, name, pvstring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.cli=CAClient(pvstring)

	def atStart(self):
		if not self.cli.isConfigured():
			self.cli.configure()

	def getPosition(self):
		if self.cli.isConfigured():
			return float(self.cli.caget())
		else:
			self.cli.configure()
			return float(self.cli.caget())
			self.cli.clearup()

	def isBusy(self):
		return 0
	
	def atEnd(self):
		if self.cli.isConfigured():
			self.cli.clearup()

#Access the CA42 directly via PV: BL06I-DI-IAMP-04:PHD2:I
#currentMonitor = DisplayEpicsPVClass('currentMonitor', 'BL06I-DI-IAMP-04:PHD2:I', 'uA', '%.10f')


class SingleEpicsPositionerClass(ScannableBase):
	'''Create PD for single EPICS positioner'''
	def __init__(self, name, pvinstring, pvoutstring, pvstatestring, pvstopstring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([name]);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.incli=CAClient(pvinstring)
		self.outcli=CAClient(pvoutstring)
		self.statecli=CAClient(pvstatestring)
		self.stopcli=CAClient(pvstopstring)

	def atStart(self):
		if not self.incli.isConfigured():
			self.incli.configure()
		if not self.outcli.isConfigured():
			self.outcli.configure()
		if not self.statecli.isConfigured():
			self.statecli.configure()
		if not self.stopcli.isConfigured():
			self.stopcli.configure()

	def getPosition(self):
		output = 99
		try:
			if self.outcli.isConfigured():
#			if not isinstance(self.outcli.caget(),type(None)):
#			print self.outcli.caget()
				return float(self.outcli.caget())
			else:
				self.outcli.configure()
				
				output = self.outcli.caget()
				if output == None:
					raise Exception, "null pointer exception in getPosition"
				self.outcli.clearup()
				return float(output)
		except Exception,e :
			print "error in getPosition", e.getMessage(), e, output
			raise e

	def asynchronousMoveTo(self,new_position):
		output_move = 99
		Thread.sleep(delayTime);
		try:
			if self.incli.isConfigured():
				self.incli.caput(new_position)
			else:
				self.incli.configure()
				self.incli.caput(new_position)
				self.incli.clearup()	
		except Exception,e :
			print "error in moveTo", e.getMessage(), e, output_move
			raise e
	

	def isBusy(self):
		#print "calling isBusy"
		try:
			if self.statecli.isConfigured():
				self.status=self.statecli.caget()
			else:
				self.statecli.configure()
				self.status=self.statecli.caget()
				self.statecli.clearup()	
#		print "status: "+self.status	
			if self.status ==None:
				print  "null pointer exception in isBusy"
				raise Exception, "null pointer exception in isBusy"	
			elif self.status=='1':
				return 0
			elif self.status=='0':
				return 1
			elif type(self.status)==type(None):
				return 1
				print "return type is >>> none"
			else:
				print 'Error: Unexpected state: '+self.status
#			raise
		except Exception, e:
			print "error in isBusy", e.getMessage(), e
			print self.status
			raise e

	def stop(self):
		if self.outcli.isConfigured():
			self.stopcli.caput(1)
		else:
			self.stopcli.configure()
			self.stopcli.caput(1)
			self.stopcli.clearup()

	def atEnd(self):
		if self.incli.isConfigured():
			self.incli.clearup()
		if  self.outcli.isConfigured():
			self.outcli.clearup()
		if self.statecli.isConfigured():
			self.statecli.clearup()
		if self.stopcli.isConfigured():
			self.stopcli.clearup()
		
#s1ctrSet = SingleEpicsPositionerClass('s1ctrSet','BL16I-AL-SLITS-01:X:CENTER.VAL','BL16I-AL-SLITS-01:X:CENTER.RBV','BL16I-AL-SLITS-01:X:CENTER.DMOV','BL16I-AL-SLITS-01:X:CENTER.STOP','mm','%.2f')


#scan s1ctrSet -5 5 0.1 currentMonitor

#del s1ctrSet, currentMonitor





























