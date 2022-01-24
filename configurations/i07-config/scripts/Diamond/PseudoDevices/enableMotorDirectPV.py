from gda.epics import CAClient
from java import lang
from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from time import sleep

#The Class for creating a scannable Motor directly from EPICS PV
class ScannableMotorEpicsPVClass(ScannableMotionBase):
	def __init__(self, name, strPV, strUnit, strFormat):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([name]);
		self.Units=[strUnit]
		self.setOutputFormat([strFormat])
		self.setLevel(3)
		self.incli=CAClient(strPV+'.VAL')
		self.outcli=CAClient(strPV+'.RBV')
		self.statecli=CAClient(strPV+'.DMOV')
		self.stopcli=CAClient(strPV+'.STOP')
		self.delayTime = 0;

	def setDelay(self, newDelay):
		self.delayTime = newDelay;

	def atScanStart(self):
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
				return float(self.outcli.caget())
			else:
				self.outcli.configure()
				
				output = self.outcli.caget()
				if output == None:
					raise Exception, "null pointer exception in getPosition"
				self.outcli.clearup()
				return float(output)
		except Exception,e :
			print "error in getPosition", e.getMessage(), e, e.class, output
			raise e

	def asynchronousMoveTo(self,new_position):
		output_move = 99
		if(self.delayTime >0):
			Thread.sleep(delayTime);
			
		try:
			if self.incli.isConfigured():
				self.incli.caput(new_position)
			else:
				self.incli.configure()
				self.incli.caput(new_position)
				self.incli.clearup()	
		except Exception,e :
			print "error in moveTo", e.getMessage(), e, e.class, output_move
			raise e
	

	def isBusy(self):
		try:
			if self.statecli.isConfigured():
				self.status=self.statecli.caget()
			else:
				self.statecli.configure()
				self.status=self.statecli.caget()
				self.statecli.clearup()	
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
			print "error in isBusy", e.getMessage(), e, e.class
			print self.status
			raise e

	def stop(self):
		if self.outcli.isConfigured():
			self.stopcli.caput(1)
		else:
			self.stopcli.configure()
			self.stopcli.caput(1)
			self.stopcli.clearup()

	def atScanEnd(self):
		if self.incli.isConfigured():
			self.incli.clearup()
		if  self.outcli.isConfigured():
			self.outcli.clearup()
		if self.statecli.isConfigured():
			self.statecli.clearup()
		if self.stopcli.isConfigured():
			self.stopcli.clearup()
		
#Access the Motor directly via PV: BL06I-DI-IAMP-04:PHD2:I
#s1ctrSet = ScannableMotorEpicsPVClass('s1ctrSet','BL16I-AL-SLITS-01:X:CENTER', 'mm', '%.4f')
