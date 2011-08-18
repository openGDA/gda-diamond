from gda.epics import CAClient 
from java import lang
from gda.device.scannable import ScannableBase
from gda.device import Scannable
from time import sleep
from gda.device.scannable import PseudoDevice

class DisplayEpicsPVClass2I18(PseudoDevice):
	'''Create PD to display single EPICS PV'''
	def __init__(self, name, pvstring, pvtimer,pvreset,unitstring, formatstring):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.cli=CAClient(pvstring)
		self.chTP=CAClient(pvtimer)
		self.chCNT=CAClient(pvreset)

	def atStart(self):
		if not self.chTP.isConfigured():
			self.chTP.configure()
		if not self.chCNT.isConfigured():
			self.chCNT.configure()
		if not self.cli.isConfigured():
			self.cli.configure()

	#Scannable Implementations
	def getPosition(self):
		return self.getCount();
	
	def asynchronousMoveTo(self,newPos):
		self.setCollectionTime(newPos);
		self.collectData();

	def isBusy(self):
		return 0

	def atEnd(self):
		if self.chTP.isConfigured():
			self.chTP.clearup()
		if self.chCNT.isConfigured():
			self.chCNT.clearup()
		if self.cli.isConfigured():
			self.cli.clearup()

	#Scaler 8512  implementations		
	def getTimePreset(self):
		if self.chTP.isConfigured():
			newtp = self.chTP.caget()
		else:
			self.chTP.configure()
			newtp = float(self.chTP.caget())
			self.chTP.clearup()
		self.tp = newtp
		return self.tp

	#Set the Time Preset and start counting automatically
	def setTimePreset(self, newTime):
		self.tp = newTime
		newtp = newTime;
		if self.chTP.isConfigured():
			tp = self.chTP.caput(newtp)
		else:
			self.chTP.configure()
			tp = self.chTP.caput(newtp)
			self.chTP.clearup()

	def getCount(self):
		if self.cli.isConfigured():
			output = self.cli.caget()
		else:
			self.cli.configure()
			output = self.cli.caget()
			self.cli.clearup()
		return float(output)


	#Detector implementations
	
	#Tells the detector to begin to collect a set of data, then returns immediately.
	#public void collectData() throws DeviceException;
	#Set the Time Preset and start counting automatically
	def collectData(self):
		#self.setTimePreset(self.tp)
		if self.chCNT.isConfigured():
			tp = self.chCNT.caput(1)
		else:
			self.chCNT.configure()
			tp = self.chCNT.caput(1)
			self.chCNT.clearup()

	#Tells the detector how long to collect for during a call of the collectData() method.
	#public void setCollectionTime(double time) throws DeviceException;
	def setCollectionTime(self, newTime):
		self.setTimePreset(newTime)
		
	#Returns the latest data collected.
	#public Object readout() throws DeviceException;
	def getCollectionTime(self):
		nc=self.getTimePreset()
		return nc

	#Returns the current collecting state of the device.
	# return ACTIVE (1) if the detector has not finished the requested operation(s), 
	#        IDLE(0) if in an completely idle state and 
	#        STANDBY(2) if temporarily suspended.
	#public int getStatus() throws DeviceException;
	def getStatus(self):
		if self.chCNT.isConfigured():
			self.stauts = self.chCNT.caget()
		else:
			self.chCNT.configure()
			self.stauts = self.chCNT.caget()
			self.chCNT.clearup()	
		if self.stauts == '0': #still counting, Busy
			return 0
		else:
			return 1


class DisplayEpicsPVClassI18(PseudoDevice):
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
 
class SingleEpicsPositionerClassI18(ScannableBase):
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
		try:
			if self.outcli.isConfigured():
				return float(self.outcli.caget())
			else:
				self.outcli.configure()
				return float(self.outcli.caget())
		except:
			print 'Error getting position'

	def asynchronousMoveTo(self,new_position):
		try:
			if self.incli.isConfigured():
				self.incli.caput(new_position)
			else:
				self.incli.configure()
				self.incli.caput(new_position)
				self.incli.clearup()
		except:
			print 'Error in moveTo'

	def isBusy(self):
		if self.statecli.isConfigured():
			self.status=self.statecli.caget()
		else:
			self.statecli.configure()
			self.status=self.statecli.caget()
			#print self.status
			self.statecli.clearup()
		if self.status=='1':
			return 0
		elif self.status=='0':
			return 1

	def atEnd(self):
		if self.incli.isConfigured():
			self.incli.clearup()
		if self.outcli.isConfigured():
			self.outcli.clearup()
		if self.statecli.isConfigured():
			self.statecli.clearup()
		if self.stopcli.isConfigured():
			self.stopcli.clearup()

	
	def stop(self):
		print "calling stop"
		self.stopcli.configure()
		self.stopcli.caput(1)
		self.stopcli.clearup()


class SingleEpicsPositionerNoStatusClassI18(SingleEpicsPositionerClass):
	"Class for PD devices without status "

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,new_position):
		try:
			self.new_position=new_position	# need this attribute for some other classes
			self.incli.configure()
			self.statecli.configure()
			self.incli.caput(new_position)
			self.statecli.caput('0')
			self.incli.clearup()
			self.statecli.clearup()
			sleep(0.5)
		except:
			print "error moving to position"

