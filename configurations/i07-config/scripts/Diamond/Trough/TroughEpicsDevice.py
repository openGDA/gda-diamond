
from time import sleep;
import math

from gda.epics import CAClient;
from gda.device.scannable import ScannableBase;
from gda.device import DeviceBase

import __main__ as gdamain


#The Class for creating a RS232 port based device to control the Nima Langmuir-Blodgett Trough
class NimaLangmuirBlodgettTroughDeviceClass(object):
	NLBT_CONTROL_MODE = {"SPEED"   : 0,
						 "PRESSURE": 1,
						 "AREA"	: 2 };


	def __init__(self, name, rootPV):
		self.name = name;
		self.setupEpics(rootPV);

		self.mode = 2;
		self.speed = 30.0;
		self.pressure = None;
		self.area = None;
		self.temperature = None;
		self.time = None;
		self.pressureB = None;
		self.areaB = None;
		self.spot = None;
		
		
		self.minArea=0;
		self.maxArea=900;
		self.minSpeed=5;
		self.maxSpeed=100;
		
		self.running=False;

	def __del__(self):
		self.cleanChannel(self.chStart);
		self.cleanChannel(self.chStop);
		self.cleanChannel(self.chMode);
		self.cleanChannel(self.chAreaTarget);
		self.cleanChannel(self.chPiTarget);
		self.cleanChannel(self.chSpeedTarget);
		
		self.cleanChannel(self.chTemp);
		self.cleanChannel(self.chTime);
		self.cleanChannel(self.chPiA);
		self.cleanChannel(self.chPiB);
		self.cleanChannel(self.chArea);
		self.cleanChannel(self.chAreaB);
		self.cleanChannel(self.chSpot);
		

	def setupEpics(self, rootPV):
#		Epics PVs for control the Trough:
		self.chStart=CAClient(rootPV + ":Start");  self.configChannel(self.chStart);
		self.chStop=CAClient(rootPV + ":Stop");  self.configChannel(self.chStop);
		self.chMode=CAClient(rootPV + ":Mode"); self.configChannel(self.chMode);
		self.chAreaTarget=CAClient(rootPV + ":AreaTarget");   self.configChannel(self.chAreaTarget);
		self.chPiTarget=CAClient(rootPV + ":PiTarget");   self.configChannel(self.chPiTarget);
		self.chSpeedTarget=CAClient(rootPV + ":SpeedTarget");   self.configChannel(self.chSpeedTarget);

#		Epics PVs for read back the Trough:
		self.chTemp=CAClient(rootPV + ":Temp");   self.configChannel(self.chTemp);
		self.chTime=CAClient(rootPV + ":Time");   self.configChannel(self.chTime);
		self.chPiA=CAClient(rootPV + ":PiA");   self.configChannel(self.chPiA);
		self.chPiB=CAClient(rootPV + ":PiB");   self.configChannel(self.chPiB);
		self.chArea=CAClient(rootPV + ":Area");   self.configChannel(self.chArea);
		self.chAreaB=CAClient(rootPV + ":AreaB");   self.configChannel(self.chAreaB);
		self.chSpot=CAClient(rootPV + ":Spot");   self.configChannel(self.chSpot);

		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();
		
	def isRunning(self):
		return self.running;
	
	def setAreaLimits(self, low, high):
		self.minArea, self.maxArea = low, high;

	def getAreaLimits(self):
		return [self.minArea, self.maxArea];
	
	def setSpeedLimits(self, low, high):
		self.minSpeed, self.maxSpeed = low, high;

	def getSpeedLimits(self):
		return [self.minSpeed, self.maxSpeed];

	def getMode(self):
		self.mode = int( float(self.chMode.caget()) );
		print "Trough Mode: " + self.NLBT_CONTROL_MODE.keys()[self.NLBT_CONTROL_MODE.values().index( self.mode )]
		return self.mode;
		
	def setMode(self, newMode):
		if newMode in self.NLBT_CONTROL_MODE.values():
			self.mode = newMode;
		elif newMode.upper() in self.NLBT_CONTROL_MODE.keys():
			self.mode =self.NLBT_CONTROL_MODE[ newMode.upper() ];
		else:
			print "Please use the right mode: 'speed/pressure/area' or 0/1/2. ";
			return;
		
		self.chMode.caput(self.mode);
		sleep(1);

	def setArea(self, newValue):
		self.chAreaTarget.caput(newValue);
		sleep(1);
		
	def getArea(self):
		self.area=float( self.chArea.caget() );
		return self.area;
		
	def setPressure(self, newValue):
		self.chPiTarget.caput(newValue);
		sleep(1);

	def getPressure(self):
		self.pressure=float( self.chPiA.caget() );
		return self.pressure;
		
	def setSpeed(self, newValue):
		self.speed = newValue;
		self.chSpeedTarget.caput(self.speed);
		sleep(1);
		
	def getSpeed(self):
		self.speed = float( self.chSpeedTarget.caget() );
		return self.speed;

	def getTemperature(self):
		self.temperature=float( self.chTemp.caget() );
		return self.temperature;

	def update(self):
		self.area       =float( self.chArea.caget()  );
		self.temperature=float( self.chTemp.caget()  );
		self.pressure   =float( self.chPiA.caget()   );
#		self.pressureB  =float( self.chPiB.caget()   );
		self.time       =float( self.chTime.caget()  );
		self.areaB      =float( self.chAreaB.caget() );
#		self.spot       =float( self.chSpot.caget()  );

		return [self.area, self.pressure, self.speed, self.areaB, self.temperature, self.time];

	def readValues(self):
		return self.update();

	def start(self):
		if self.running:
			return;
		self.chStart.caput(1);
		sleep(0.2);
		self.chStart.caput(0);
		sleep(0.1);
		self.running = True;
		
	def stop(self):
		self.chStop.caput(1);
		sleep(0.2);
		self.chStop.caput(0);
		sleep(0.1);
		self.running = False;
		

	def asynchronousAreaMoveTo(self,newArea):
		self.setMode(NimaLangmuirBlodgettTroughDeviceClass.NLBT_CONTROL_MODE['AREA']);
		self.setArea(newArea);
		if not self.isRunning():
			self.start();

	def synchronousAreaMoveTo(self,newArea):
		self.asynchronousAreaMoveTo(newArea);
		while self.getStatus() is not True:
				sleep(5);


class TroughAreaDevice(ScannableBase):
	def __init__(self, name, trough):
		self.setName(name);
		self.setInputNames(["Area"]);
		self.setExtraNames(["Pressure", "Temperature"]);
		self.setOutputFormat(["%8.4f", "%8.4f", "%8.4f"]);
		self.setLevel(7);
		self.trough = trough;
		
		self.targetPosition=None;
		self.deadband = 1.0;

	#Scannable Implementation
	def getPosition(self):
		self.trough.update();
		return [self.trough.area, self.trough.pressure, self.trough.temperature];

	def asynchronousMoveTo(self,newPos):
		self.trough.setMode('AREA');
		self.targetPosition=newPos;
		self.trough.asynchronousAreaMoveTo(newPos);

	def isBusy(self):
		onTarget = abs(self.targetPosition - self.trough.getArea()) <= self.deadband;

		if onTarget or (not self.trough.running):
			return False;		
		else:
			return True;

	def stop(self):
		self.trough.stop();

	def reset(self):
		self.trough.stop();
		

class TroughPressureDevice(ScannableBase):
	def __init__(self, name, trough):
		self.setName(name);
		self.setInputNames(["Pressure"]);
		self.setExtraNames([]);
		self.setOutputFormat(["%8.4f"]);
		self.setLevel(7);
		self.trough = trough;
		
		self.targetPosition=None;

	def getPosition(self):
		self.trough.update()
		return self.trough.pressure;

	def asynchronousMoveTo(self,newPos):
		self.targetPosition=newPos;
		self.trough.setMode('PRESSURE');
		self.trough.setPressure(newPos);
		if not self.trough.isRunning():
			self.trough.start();

	def stop(self):
		self.trough.stop();

	def isBusy(self):
		sleep(1)
		return not self.trough.getStatus()
	


class TroughSpeedDevice(ScannableBase):
	def __init__(self, name, trough):
		self.setName(name);
		self.setInputNames(["Speed"]);
		self.setExtraNames([]);
		self.setOutputFormat(["%8.4f"]);
		self.setLevel(7);
		self.trough = trough;
		
	def getPosition(self):
		self.trough.getSpeed()
		return self.trough.speed;

	def asynchronousMoveTo(self,newPos):
		self.trough.setMode(NimaLangmuirBlodgettTroughDeviceClass.NLBT_CONTROL_MODE['SPEED']);
		self.trough.setSpeed(newPos);

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

