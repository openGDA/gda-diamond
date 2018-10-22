
from time import sleep;
from Diamond.Utility.LookupTables import InterpolatedArray;
from Diamond.PseudoDevices.EpicsDevices import EpicsDeviceClass;
	
class VoltageTemperatureControllerClass(EpicsDeviceClass):
	def __init__(self, name, tvTable, pvSet, pvGet, pvStatus, strUnit, strFormat, timeout=None):
		EpicsDeviceClass.__init__(self, name, pvSet, pvGet, pvStatus, strUnit, strFormat, timeout);

		self.tvTable = tvTable;
		self.vtTable = tvTable.reverseTable();
		
		self.targetTemperature = None;
		self.deadband = 100.0;
		self.delay = 5;
		

	def setDeadband(self, deadband):
		self.deadband = deadband;
		
	def getDeadband(self):
		return self.deadband;
	
	def v2t(self, v):
		t=self.vtTable[v];
		print "Voltage = " + str(v) + " ---> Temperature = "+ str(t);
		return t;
		
	def t2v(self, t):
		v=self.tvTable[t];
		print "Temperature = " + str(t) + " ---> Voltage = "+ str(v);
		return v;
	
	def getPosition(self):
		voltage=EpicsDeviceClass.getPosition(self);
		temperature = self.vtTable[voltage];
		return temperature;

	def asynchronousMoveTo(self, new_temperature):
		self.targetTemperature = new_temperature;
		self.setTemperature(self.targetTemperature);
		sleep(self.delay);

	def setTemperature(self, new_temperature):
		new_voltage = self.tvTable[new_temperature];
		try:
			if self.timeout is None:
				self.chSet.caput(new_voltage);
			else:
				self.chSet.caput(new_voltage, self.timeout);
		except:
			print "Error setting voltage"

	def getTemperature(self):
		return self.getPosition();

	def isBusy(self):
		ct = self.getTemperature();
		if (ct >= self.targetTemperature-self.deadband) and (ct <= self.targetTemperature+self.deadband):#No status pv provided, so no status feedback necessary
			return False;
		else:
			return True;
		
	def toString(self):
		ct = self.getTemperature();
		cv = self.tvTable[ct];
		return "Current Temperature: " + str(ct) + "K, (Voltage: " + str(cv)+ " V, Deadband: +-" + str(self.deadband) + "K)";


################################################
#Usage:
#The Temperature-Voltage Lookup Table:
#            (T , V)
tvPoints = ( (13, 0.013123), 
		     (14, 0.01468),
		     (15, 0.016536),
		     (16, 0.018811),
		     (17, 0.021505),
		     (18, 0.024676),

		     (760, 9.859558),
		     (770, 9.930093),
		     (780, 9.999723),
		     
		     (800, 10.000),
		     (900, 11.000),
		     (999, 12.000)
		   );

tvTable = InterpolatedArray(tvPoints);

pvVoltageSet = "BL07I-EA-TCTRL-01:SP:VOLTAGE"
pvVoltageGet1 = "BL07I-EA-TCTRL-01:SENS1:VOLTAGE:RBV"
exec("temp10=None");
temp10=VoltageTemperatureControllerClass('temp10', tvTable, pvVoltageSet, pvVoltageGet1, None, 'K', '%.5f', timeout=None);
