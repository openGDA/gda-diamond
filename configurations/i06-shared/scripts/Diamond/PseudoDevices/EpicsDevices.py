from gda.epics import CAClient;
from gda.device.scannable import ScannableMotionBase;

from time import sleep, time

class EpicsDevicStatus(object):
	DEVICE_STATUS_IDLE, DEVICE_STATUS_BUSY, DEVICE_STATUS_PAUSED, DEVICE_STATUS_STANDBY, DEVICE_STATUS_FAULT, DEVICE_STATUS_MONITORING = range(6);
	

#The Class for creating a Monitor directly from EPICS PV
class EpicsMonitorClass(ScannableMotionBase):
	def __init__(self, name, strPV, strUnit, strFormat):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[strUnit];
		self.setOutputFormat([strFormat])
		self.setLevel(7)
		self.cli=CAClient(strPV);
		self.cli.configure();

	def atScanStart(self):
		if not self.cli.isConfigured():
			self.cli.configure()

	def getPosition(self):
		try:
			if self.cli.isConfigured():
				return float(self.cli.caget());
			else:
				self.cli.configure();
				return float(self.cli.caget());
		except:
			print "Error getting position"

	def asynchronousMoveTo(self, new_position):
		pass;

	def isBusy(self):
		return False

#The Class for creating a Monitor directly from EPICS PV
class EpicsLazyMonitorClass(ScannableMotionBase):
	def __init__(self, name, strPV, strUnit, strFormat):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[strUnit];
		self.setOutputFormat([strFormat])
		self.setLevel(7)
		self.cli=CAClient(strPV);
		self.cli.configure();
		self.value=None;
		

	def atScanStart(self):
		try:
			if not self.cli.isConfigured():
				self.cli.configure();
				
			self.value = float(self.cli.caget());
			
		except:
			print "Error getting Epics position"

	def atScanEnd(self):
		self.value = None;

	def getPosition(self):
		return self.value;

	def asynchronousMoveTo(self, new_position):
		pass;

	def isBusy(self):
		return False

#The Class for creating a Pseudo Device that can do Epics caput
class EpicsSetterClass(ScannableMotionBase):
	def __init__(self, name, pvSetter, pvStatus, strUnit, strFormat, timeout=None):
		self.setName(name);
		self.chSetter = CAClient(pvSetter);
		self.chSetter.configure();
		if pvStatus is not None:
			self.chStatus = CAClient(pvStatus);
			self.chStatus.configure();
		else:
			self.chStatus = None;
			
		self.Units=[strUnit];
		self.setOutputFormat([strFormat]);
		
		self.delay=1;
		self.timeout = timeout;
		self._moved = 0
	
	def setDelay(self, newDelay):
		self.delay = newDelay;
	
	def setTimeout(self, newTimeout):
		self.timeout = newTimeout;
			
	def getPosition(self):
		try:
			if self.chSetter.isConfigured():
				return float(self.chSetter.caget())
			else:
				self.chSetter.configure();
				return float(self.chSetter.caget());
		except:
			print "Error getting position"

	def asynchronousMoveTo(self, new_position):
		self.currentposition = new_position
		try:
			if self.chSetter.isConfigured():
				if self.timeout is None:
					self.chSetter.caput(new_position);
				else:
					self.chSetter.caput(new_position, self.timeout);
			else:
				self.chSetter.configure()
				if self.timeout is None:
					self.chSetter.caput(new_position);
				else:
					self.chSetter.caput(new_position, self.timeout);
		except:
			print "Error setting position"

		self._moved = time()

	def getStatus(self):
		status=0;
		try:
			if self.chStatus.isConfigured():
				status = int(float(self.chStatus.caget()));
			else:
				self.chStatus.configure()
				status= int(float(self.chStatus.caget()));
		except:
			print "Error getting status"
		if status == 1:
			return EpicsDevicStatus.DEVICE_STATUS_IDLE;
		if status ==0:
			return EpicsDevicStatus.DEVICE_STATUS_BUSY;


	def isBusy(self):
		if self.chStatus is None:#No status pv provided, so no status feedback necessary
			if self._moved == 0: return False
			if time() < (self._moved + self.delay * 1000):
				return True
			else:
				self._moved = 0 #so we can't "become busy" again by changing the delay
				return False
		if self.getStatus() == EpicsDevicStatus.DEVICE_STATUS_IDLE:#It's done
			return False;
		else:
			return True;

#The Class for creating a Pseudo Device that can do Epics caput and caget
class EpicsDeviceClass(ScannableMotionBase):
	def __init__(self, name, pvSet, pvGet, pvStatus, strUnit, strFormat, timeout=None):
		self.setName(name);
		self.setInputNames([name]);
		self.Units=[strUnit];
		self.setOutputFormat([strFormat]);
		
		self.delay=1;
		self.timeout = timeout;

		self.setupEpics(pvSet, pvGet, pvStatus);

	def __del__(self):
		self.cleanChannel(self.chSet);
		self.cleanChannel(self.chGet);
		if self.chStatus:
			self.cleanChannel(self.chStatus);
	
	def setupEpics(self, pvSet, pvGet, pvStatus):
#		Epics PVs for checking fast scan readiness:
		self.chSet=CAClient(pvSet);  self.configChannel(self.chSet);
		self.chGet=CAClient(pvGet);  self.configChannel(self.chGet);

		if pvStatus:
			self.chStatus = CAClient(pvStatus);	self.configChannel(self.chStatus);
		else:
			self.chStatus = None;
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();
	
	def setDelay(self, newDelay):
		self.delay = newDelay;
	
	def setTimeout(self, newTimeout):
		self.timeout = newTimeout;

	def caget(self):
		try:
			result = float(self.chGet.caget())
		except:
			print "Error getting position"
		return result;

	def caput(self, new_position):
		try:
			if self.timeout is None:
				self.chSet.caput(new_position);
			else:
				self.chSet.caput(new_position, self.timeout);
		except:
			print "Error setting position"
			
	def getPosition(self):
		return self.caget();

	def asynchronousMoveTo(self, new_position):
		self.currentposition = new_position;
		self.caput(new_position);

		sleep(self.delay);

	def getStatus(self):
		status=0;
		try:
			if self.chStatus:
				status = int(float(self.chStatus.caget()));
		except:
			print "Error getting status"
		if status == 1:
			return EpicsDevicStatus.DEVICE_STATUS_IDLE;
		if status ==0:
			return EpicsDevicStatus.DEVICE_STATUS_BUSY;


	def isBusy(self):
		if self.chStatus is None:#No status pv provided, so no status feedback necessary
			return False;
		
		if self.getStatus() == EpicsDevicStatus.DEVICE_STATUS_IDLE:#It's done
			return False;
		else:
			return True;

#	def toFormattedString(self):
#		return self.name + " : " + str( self.getPosition() );
	
#Monitor Example:
#sampleMonitor=EpicsMonitorClass('sampleMonitor', 'BL07I-AL-SLITS-03:INTEN', 'uA', '%.10f');

#Setter Example
#sampleSetter1=EpicsSetterClass('sampleSetter1', 'BL07I-AL-SLITS-03:INTEN', 'BL07I-AL-SLITS-03:INTEN', 'V', '%.5f', timeout=None);
#sampleSetter2=EpicsSetterClass('sampleSetter2', 'BL07I-AL-SLITS-03:INTEN', 'BL07I-AL-SLITS-03:STATUS', 'V', '%.5f', timeout=20);

#pvVoltageSet = "BL07I-EA-TCTRL-01:SP:VOLTAGE"
#pvVoltageGet1 = "BL07I-EA-TCTRL-01:SENS1:VOLTAGE:RBV"
#temp10=EpicsDeviceClass('temp10', pvVoltageSet, pvVoltageGet1, None, 'V', '%.5f', timeout=None);

