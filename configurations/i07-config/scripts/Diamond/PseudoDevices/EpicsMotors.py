from time import sleep


from gda.epics import CAClient
from gda.device.scannable import ScannableMotionBase

from gov.aps.jca.event import PutEvent;
from gov.aps.jca.event import PutListener;
from gov.aps.jca import CAStatus;


#The Class for creating a scannable Motor directly from EPICS PV
#The motor status is reflected in the DMOV flag
class EpicsMotorClass(ScannableMotionBase):
	MOTOR_STATUS_UPPERLIMIT, MOTOR_STATUS_LOWERLIMIT, MOTOR_STATUS_FAULT, MOTOR_STATUS_READY, MOTOR_STATUS_BUSY, MOTOR_STATUS_UNKNOWN, MOTOR_STATUS_SOFTLIMITVIOLATION = range(7);
	def __init__(self, name, pvRootMotor, strFormat):
		self.setName(name);
		self.setInputNames([name]);
#		self.setExtraNames([]);
		self.setOutputFormat([strFormat]);
		self.setLevel(7);
		
		self.chVAL=CAClient(pvRootMotor+'.VAL');
		self.chRBV=CAClient(pvRootMotor+'.RBV');
		self.chDMOV=CAClient(pvRootMotor+'.DMOV');
		self.chSTOP=CAClient(pvRootMotor+'.STOP');
		self.chHLM=CAClient(pvRootMotor+'.HLM');
		self.chLLM=CAClient(pvRootMotor+'.LLM');
		self.chUNIT=CAClient(pvRootMotor+'.EGU');

		self.chOFF=CAClient(pvRootMotor+'.OFF');

		self.chVAL.configure();
		self.chRBV.configure();
		self.chDMOV.configure();
		self.chSTOP.configure();
		self.chHLM.configure();
		self.chLLM.configure();
		self.chUNIT.configure();
		self.chOFF.configure();
		self.status = EpicsMotorClass.MOTOR_STATUS_READY;
		self.dmov = None;
		
	def __del__(self):
		self.cleanChannel(self.chVAL);
		self.cleanChannel(self.chDMOV);
		self.cleanChannel(self.chRBV);
		self.cleanChannel(self.chSTOP);
		self.cleanChannel(self.chHLM);
		self.cleanChannel(self.chLLM);
		self.cleanChannel(self.chUNIT);
		self.cleanChannel(self.chOFF);

	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();
		
	def atScanStart(self):
		self.configChannel(self.chVAL);
		self.configChannel(self.chDMOV);
		self.configChannel(self.chRBV);
		self.configChannel(self.chSTOP);
		self.configChannel(self.chHLM);
		self.configChannel(self.chLLM);
		self.configChannel(self.chUNIT);
		self.configChannel(self.chOFF);

	def getLimits(self):
		hlm = float( self.chHLM.caget() );
		llm = float( self.chLLM.caget() );
		return [hlm, llm];

	def getUnit(self):
		unit = self.chUNIT.caget();
		return unit;

	def getOffset(self):
		return float(self.chOFF.caget());

	def setOffset(self, new_offset):
		self.chOFF.caput(new_offset);

	def getPosition(self):
		return float(self.chRBV.caget());

	def asynchronousMoveTo(self,new_position):
		self.chVAL.caput(new_position)
	
	def isBusy(self):
		self.dmov=int(float(self.chDMOV.caget()));
		if self.dmov == 1:
			self.status = EpicsMotorClass.MOTOR_STATUS_READY;
			return False;
		elif self.dmov == 0:
			self.status = EpicsMotorClass.MOTOR_STATUS_BUSY;
			return True;
		else:
			print 'Error: Unexpected DMOV: '+self.dmov;
			self.status = EpicsMotorClass.MOTOR_STATUS_UNKNOWN;
			return True;

	def stop(self):
		print self.getName() + ": Panic Stop Called"
		self.chSTOP.caput(1);

	def toString(self):
		ss=self.getName() + " : " + str(self.getPosition()) + " " + self.getUnit() + " (" + str(self.getLimits()[1]) + " : "+ str(self.getLimits()[0]) + ")";
		return ss;

	def toFormattedString(self):
		return self.toString();
    
#The Class for creating a scannable Motor directly from EPICS PV
#The motor status is reflected in the DMOV flag
class EpicsCallbackMotorClass(EpicsMotorClass):
	#CA Put Callback listener that handles the callback event
	class CaputCallbackListenerClass(PutListener):
		def __init__ (self, motor):
			self.motor = motor;
			
		def putCompleted(self, event):
			if event.getStatus() != CAStatus.NORMAL:
				print 'Motor move failed!'
				print 'Failed source: ' + event.getSource().getName();
				print 'Failed stuatus: ' + event.getStatus();
			else:
#				print 'The motor calls back';
				self.motor.status = EpicsMotorClass.MOTOR_STATUS_READY;
			return;

		def getStatus(self):
				return self.motor.status;
			
	
	def __init__(self, name, pvRootMotor, strFormat):
		try:
			EpicsMotorClass.__init__(self, name, pvRootMotor, strFormat);
#			super(EpicsMotorClass, self).__init__(name, pvRootMotor, strUnit, strFormat);
		except AttributeError:
			pass;

		self.putListener = EpicsCallbackMotorClass.CaputCallbackListenerClass(self);

	def asynchronousMoveTo(self,new_position):
		self.status = EpicsMotorClass.MOTOR_STATUS_BUSY;
		self.chVAL.getController().caput(self.chVAL.getChannel(), new_position, self.putListener);

	def isBusy(self):
		if self.status == EpicsMotorClass.MOTOR_STATUS_BUSY:
			return True;
		if self.status == EpicsMotorClass.MOTOR_STATUS_READY:
			return False;
		else:
			print 'Error: Unexpected Motor Status: ' + self.status;
			return True;
		

#A Class for accessing the User Offset field of EPICS Motor
class EpicsMotorOffsetClass(EpicsMotorClass):
	def __init__(self, name, pvRootMotor, strFormat):
		try:
			EpicsMotorClass.__init__(self, name, pvRootMotor, strFormat);
#			super(EpicsMotorClass, self).__init__(name, pvRootMotor, strUnit, strFormat);
		except AttributeError:
			pass;

	def getPosition(self):
		return self.getOffset();

	def asynchronousMoveTo(self,new_position):
		self.setOffset(new_position);
		sleep(1);

	def isBusy(self):
		return False;

	def toString(self):
		ss=self.getName() + ": User Offset: " + str(self.getPosition())	 + " " + self.getUnit();
		return ss;

#pvMotor1 = 'BL06J-DI-IONC-01:Y';
#emotor1 = EpicsMotorClass('emotor1',pvMotor1, '%.4f');

#pvMotor2 = 'BL06J-DI-IONC-01:Y';
#emotor2 = EpicsCallbackMotorClass('emotor2',pvMotor2, '%.4f');

