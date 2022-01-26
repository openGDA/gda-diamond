
from time import sleep;
import math

from gda.epics import CAClient;
from gda.device.scannable import ScannableBase;
from gda.device import DeviceBase

import __main__ as gdamain

class TroughAreaDevice(ScannableBase):
	def __init__(self, name, trough):
		self.setName(name);
		self.setInputNames(["Area"]);
		self.setExtraNames(["Pressure", "Temperature", "Ang2_molecule"]);
		self.setOutputFormat(["%8.4f", "%8.4f", "%8.4f", "%8.4f"]);
		self.setLevel(7);
		self.trough = trough;
		
		self.targetPosition=None;
		self.onTarget = True;
		self.deadband = 1.0;
		
		
		self.molMass = 312.0;
		self.concentration=1.004; # mg/ml
		self.volume = 10.0; # ul
		
		self.numberOfMolecules=0;

	def reset(self):
		self.targetPosition=self.trough.getArea();
		self.onTarget = True;
		self.deadband = 1.0;
		
	def setDeadband(self, newDeadband):
		self.deadband = newDeadband;

	def getDeadband(self):
		return self.deadband;
	
	def setMolecularProperties(self, molMass, concentration, volume ):
		self.molMass = molMass; #g/mol
		self.concentration=concentration # mg/ml
		self.volume = volume; # ul

	def getMolecularProperties(self):
		ulUnit=unichr(0x03bc).encode('utf-8')+'l';
		apmUnit=unichr(0x212b).encode('utf-8')+'2';
		print "Molecular Properties:";
		print "Mol Mass: %.2f %s, Concentration: %.2f %s, Volume: %.2f %s" %(self.molMass, 'g/mol', self,concentration, 'mg/ml', self.volume, ulUnit);
		#print "Area per molecule: %.2f %s" %(self.getAearPerMolecule(), apmUnit);
		
	
	def getNumberOfMolecules(self):
		'''	To get the number of molecules dropped on surface '''
		# in mol number
		result=(self.volume*1.0e-6)*self.concentration/self.molMass;
		return result*6.022214e23;#Convert mol to actual number using the Avogadro constant
		
	def getAearPerMolecule(self, areaInCm2=None):
		'''To get the Area in square Angstrom on per molecule '''
		if areaInCm2 is None:
			self.trough.update();
			areaInCm2=self.trough.area;
			
		n=self.getNumberOfMolecules();
		result = (areaInCm2*1.0e-4/1.0e-20)/n;
		return result;
		

	#Scannable Implementation
	def getPosition(self):
		self.trough.update();
		aearPerMolecule=self.getAearPerMolecule(self.trough.area);
		return [self.trough.area, self.trough.pressure, self.trough.temperature, aearPerMolecule];

	def asynchronousMoveTo(self,newPos):
		self.trough.setMode('AREA');
		self.targetPosition=newPos;
		self.onTarget = False;
		self.trough.asynchronousAreaMoveTo(newPos);

#		self.waitUntilDone();

	def waitUntilDone(self):
		while( not self.onTarget ):
			self.onTarget = abs(self.targetPosition - self.trough.getArea()) <= self.deadband;
			sleep(1)

	def isBusy(self):
		if self.onTarget or (not self.trough.running):
			return False;

		#New position was set or was busy before, re-check
		self.onTarget = abs(self.targetPosition - self.trough.getArea()) <= self.deadband;

		if self.onTarget or (not self.trough.running):
			return False;		
		else:
			return True;

	def stop(self):
#		self.trough.stop();
		self.onTarget=True;
		

class TroughPressureDevice(ScannableBase):
	def __init__(self, name, trough):
		self.setName(name);
		self.setInputNames(["Pressure"]);
		self.setExtraNames([]);
		self.setOutputFormat(["%8.4f"]);
		self.setLevel(7);
		self.trough = trough;
		
		self.targetPosition=None;
		self.onTarget = True;
		self.deadband = 0.1;

	def reset(self):
		self.targetPosition=self.trough.getPressure();
		self.onTarget = True;
		self.deadband = 0.1;

	def setDeadband(self, newDeadband):
		self.deadband = newDeadband;

	def getDeadband(self):
		return self.deadband;

	def getPosition(self):
		self.trough.update()
		return self.trough.pressure;

	def asynchronousMoveTo(self,newPos):
		self.targetPosition=newPos;
		self.onTarget = False;
		self.trough.setMode('PRESSURE');
		self.trough.setPressure(newPos);
		if not self.trough.isRunning():
			self.trough.start();
			
		self.waitUntilDone();

	def waitUntilDone(self):
		while( not self.onTarget ):
			self.onTarget = abs(self.targetPosition - self.trough.getPressure()) <= self.deadband;
			sleep(1)

	def stop(self):
#		self.trough.stop();
		self.onTarget=True;

	def isBusy(self):
		return False;
	


class TroughSpeedDevice(ScannableBase):
	def __init__(self, name, troughAreaDevice):
		self.setName(name);
		self.setInputNames(["Speed"]);
		self.setExtraNames([]);
		self.setOutputFormat(["%8.4f"]);
		self.setLevel(7);
		self.troughAreaDevice=troughAreaDevice;
		self.trough = self.troughAreaDevice.trough;
		
	def getPosition(self):
		return self.trough.getSpeed();

	def asynchronousMoveTo(self,newPos):
		currentArea=self.trough.getArea();
		self.trough.setMode(self.trough.NLBT_CONTROL_MODE['SPEED']);
		self.trough.setSpeed(newPos);
		
		self.troughAreaDevice.moveTo(currentArea);

	def isBusy(self):
		return False;

  
#GDA RS232 communication
#c=Finder.find("com1")
#sc=Finder.find("sc1")

#sc.setCommandTerminator('')
#sc.setReplyTerminator('\r')
#sc.configure()
#c.flush()

#port2=GdaRS232DeviceClass(sc)

#EPICS RS232 communication
#rootPV = "BL07I-EA-USER-01:ASYN2"
#portName='ty_50_2'
#baudRate=EpicsAsynRS232DeviceClass.BAUDRATE['9600'];
#dataBits=EpicsAsynRS232DeviceClass.DATABITS['8']
#parity=EpicsAsynRS232DeviceClass.PARITY['None']
#flowControl=EpicsAsynRS232DeviceClass.FLOWCONTROL['None']
#timeout=2;

#port1 = EpicsAsynRS232DeviceClass(rootPV);
#port1.setPort(portName, baudRate, dataBits, parity, flowControl, timeout);

##port1.setOutputTerminator('\r');
#port1.setInputTerminator('\r')
#port1.flush()

##Trough over EPICS RS232
#trough = NimaLangmuirBlodgettTroughDeviceClass('trough', port1);
#Trough over GDA RS232
#trough = NimaLangmuirBlodgettTroughDeviceClass('trough', port2);


#troughArea = TroughAreaDevice("troughArea", trough);
#troughSpeed = TroughSpeedDevice("troughSpeed", trough);
#troughPressure = TroughPressureDevice("troughPressure", trough);

#trough.setSpeedLimits(10, 500);
#trough.setAreaLimits(0, 500);

