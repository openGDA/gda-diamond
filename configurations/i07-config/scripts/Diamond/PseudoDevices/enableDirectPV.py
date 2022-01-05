from gda.epics import CAClient
from java import lang
from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from time import sleep

#The Class for creating a Monitor directly from EPICS PV
class MonitorEpicsPVClass(ScannableMotionBase):
	def __init__(self, name, strPV, strUnit, strFormat):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[strUnit]
		self.setOutputFormat([strFormat])
		self.setLevel(3)
		self.cli=CAClient(strPV)

	def atScanStart(self):
		if not self.cli.isConfigured():
			self.cli.configure()

	def getPosition(self):
		if self.cli.isConfigured():
			return float(self.cli.caget())
		else:
			self.cli.configure()
			return float(self.cli.caget())

	def isBusy(self):
		return 0
	
	def atScanEnd(self):
		if self.cli.isConfigured():
			self.cli.clearup()

#The Class for creating a Scaler directly from EPICS PV
class ScalerEpicsPVClass:
	def __init__(self, name, strPV, time):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
#		self.setOutputFormat(['%d'])
		self.setLevel(3)
		self.chTP=CAClient(strPV+'.TP')
		self.chCNT=CAClient(strPV+'.CNT')
		self.chFREQ=CAClient(strPV+'.FREQ')
		
		for n in range(64):
			self.chScalerValue[n]=CAClient(strPV+'.S' + n)
			#self.chPreset[n]= CAClient(strPV+'.PR' + n)

	def atScanStart(self):
		if not self.cli.isConfigured():
			self.cli.configure()

	def getPosition(self):
		return float(0)

	def asynchronousMoveTo(self,new_position):
		np = new_position;
		try:
			if self.chCNT.isConfigured():
				self.chCNT.caput(np)
			else:
				self.chCNT.configure()
				self.chCNT.caput(np)
				self.incli.clearup()	
		except Exception, e :
			print "error in asynchronousMoveTo"
			print e
			
	def isBusy(self):
		return 0
	
	def atScanEnd(self):
		if self.cli.isConfigured():
			self.cli.clearup()

	def setCollectionTime(self, time):
		if not self.chTP.isConfigured():
			self.chTP.configure()
		self.chTP.caput(time);



#The Class for creating a Scaler Channel Monitor directly from EPICS PV
class ScalerChannelMonitorEpicsPVClass(ScannableMotionBase):
	def __init__(self, name, strPV, strCh, time):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
#		self.Units=[strUnit]
#		self.setOutputFormat(['%d'])
		self.setLevel(3)
		self.chTP=CAClient(strPV+'.TP')
		self.chCNT=CAClient(strPV+'.CNT')
		self.chFREQ=CAClient(strPV+'.FREQ')
		self.chPRn=CAClient(strPV+'.PR' + strCh)
		self.chSn=CAClient(strPV+'.S' + strCh)

	def atScanStart(self):
		if not self.chTP.isConfigured():
			self.chTP.configure()
		if not self.chCNT.isConfigured():
			self.chCNT.configure()
		if not self.chFREQ.isConfigured():
			self.chFREQ.configure()
		if not self.chPRn.isConfigured():
			self.chPRn.configure()
		if not self.chSn.isConfigured():
			self.chSn.configure()

	def getPresetTime(self):
		#get time preset
		if self.chTP.isConfigured():
			self.tp = self.chTP.caget()
		else:
			self.chTP.configure()
			self.tp = self.chTP.caget()
			self.chTP.clearup()
			
		return self.tp

	def setPresetTime(self, float):
		#get time preset
		if self.chTP.isConfigured():
			tp = self.chTP.caget()
		else:
			self.chTP.configure()
			tp = self.chTP.caget()
			self.chTP.clearup()
			
		self.tp = self.getTP()
		
	def getPosition(self):
		self.tp = self.getPresetTime()
		
		self.startCounting();

		while self.isBusy():
			Thread.sleep(tp);
			
		self.startCounting();
		
		while self.isBusy():
			Thread.sleep(tp);
			
		output = self.getCount();
		return output;
	

	def getCount(self):
		if self.chSn.isConfigured():
			output = self.chSn.caget()
		else:
			self.chSn.configure()
			output = self.chSn.caget()
			self.chSn.clearup()
		return long(output)

	def startCounting(self):
		self.status = '1'
		if self.chCNT.isConfigured():
			self.chCNT.caput(self.stauts) ##start counting
		else:
			self.chCNT.configure()
			self.chCNT.caput(self.stauts) ##start counting
			self.chCNT.clearup()	

	def isBusy(self):
		try:
			if self.chCNT.isConfigured():
				self.stauts = self.chCNT.caget()
			else:
				self.chCNT.configure()
				self.stauts = self.chCNT.caget()
				self.chCNT.clearup()	
			
			if self.stauts == '1': #still counting, busy
				return 1
			elif self.stauts == '0': # count finished. not busy
				return 0 
			else: #strange condition, caget some wrong status
				raise ScalerException("Wrong Scaler CNT")	
				return 1
		except ScalerException, e:
			print "error in ScalerChannelMonitorEpicsPVClass.isBusy()."
			print e
			print self.status
		except Exception, e:
			print "What ever exception raised in ScalerChannelMonitorEpicsPVClass.isBusy()."
			print e
			print self.status
		

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
		if(delayTime >0):
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
		


#Access the CA42 directly via PV: BL06I-DI-IAMP-04:PHD2:I
#currentMonitor = MonitorEpicsPVClass('currentMonitor', 'BL06I-DI-IAMP-04:PHD2:I', 'uA', '%.10f')

#Access the Motor directly via PV: BL06I-DI-IAMP-04:PHD2:I
#s1ctrSet = ScannableEpicsPVClass('s1ctrSet','BL16I-AL-SLITS-01:X:CENTER', 'mm', '%.4f')

#scan s1ctrSet -5 5 0.1 currentMonitor

#del s1ctrSet, currentMonitor





























