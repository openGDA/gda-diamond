
from time import sleep;
import math

from gda.epics import CAClient;
from gda.device.scannable import ScannableMotionBase;
from gda.device import DeviceBase

import __main__ as gdamain

class GdaRS232DeviceClass(object):
	def __init__(self, serialController):
		self.serialController=serialController;

	def write(self, sendString):
		self.serialController.sendCommand(sendString);
		
	def read(self):
		reply = self.serialController.getReply()
		return reply;
	
	def writeAndRead(self, sendString):
		self.serialController.sendCommand(sendString);
		reply = self.serialController.getReply()
		return reply;
	

class EpicsAsynRS232DeviceClass(object):
	BAUDRATE = {'UNKNOWN':0,
			    '300' :   1,
			    '600':    2,
			    '1200':   3,
			    '2400':   4,
			    '4800':   5,
			    '9600':   6,
			    '19200':  7,
			    '38400':  8,
			    '57600':  9,
			    '115200':10,
			    '230400':11 }
	
	DATABITS = {'UNKNOWN':0,
			    '5' :     1,
			    '6':      2,
			    '7':      3,
			    '8':      4 }
	
	PARITY = {'UNKNOWN': 0,
			    'None' : 1,
			    'Even' : 2,
			    'Odd'  : 3 }
	
	FLOWCONTROL = {'UNKNOWN' : 0,
				   'None'    : 1,
				   'Hardware': 2 }

	TRANSFER_MODE = {'WriteRead':0,
					 'Write'    :1,
			         'Read'     :2,
			         'Flush'    :3,
			         'NonIO'    :4 }

	FORMAT = {'ASCII'  :0,
			  'Hybrid' :1,
	          'Binary' :2,
	          'Flush'  :3 }
	
	SEVERITY = {'NO_ALARM':0,
			    'MINOR'   :1,
	            'MAJOR'   :2,
	            'INVALID' :3 }
	
	
	def __init__(self, rootPV):
		self.setupEpics(rootPV);

		baudRate=EpicsAsynRS232DeviceClass.BAUDRATE['9600'];
		dataBits=EpicsAsynRS232DeviceClass.DATABITS['8'];
		parity=EpicsAsynRS232DeviceClass.PARITY['None'];
		flowControl=EpicsAsynRS232DeviceClass.FLOWCONTROL['None'];
		self.setPort(portName, baudRate, dataBits, parity, flowControl, 1);
		
	def __del__(self):
		self.cleanChannel(self.chPort)
		self.cleanChannel(self.chConnect)
		self.cleanChannel(self.chBaudRate)
		self.cleanChannel(self.chDataBits)
		self.cleanChannel(self.chParity)
		self.cleanChannel(self.chFlowControl)

		self.cleanChannel(self.chTimeout)
		self.cleanChannel(self.chTransfer)

		self.cleanChannel(self.chOutputFormat)
		self.cleanChannel(self.chOutputTerminator)
		self.cleanChannel(self.chOutputString)

		self.cleanChannel(self.chInputFormat)
		self.cleanChannel(self.chInputTerminator)
		self.cleanChannel(self.chInputString)

		self.cleanChannel(self.chErrorString)
		self.cleanChannel(self.chStatus)
		self.cleanChannel(self.chSeverity)

		self.cleanChannel(self.chScanMode)
		self.cleanChannel(self.chProcess)

	"""	
	Asyn Driver for RS232:
	
	Port: 			BL07I-EA-USER-01:ASYN1.PORT
	Connection: 	BL07I-EA-USER-01:ASYN1.PCNCT
	Baud Rate:		BL07I-EA-USER-01:ASYN1.BAUD
	Data Bits:		BL07I-EA-USER-01:ASYN1.DBIT
	Parity:			BL07I-EA-USER-01:ASYN1.PRTY
	Flow Control:	BL07I-EA-USER-01:ASYN1.FCTL
			
	Timeout:	BL07I-EA-USER-01:ASYN1.TMOT
	Transfer:	BL07I-EA-USER-01:ASYN1.TMOD
	
	Output Format:		BL07I-EA-USER-01:ASYN1.OFMT
	Output Terminator:	BL07I-EA-USER-01:ASYN1.OEOS
	Output String:		BL07I-EA-USER-01:ASYN1.AOUT
			
	Input Format:		BL07I-EA-USER-01:ASYN1.IFMT
	Input Terminator:	BL07I-EA-USER-01:ASYN1.IEOS
	Input String:		BL07I-EA-USER-01:ASYN1.TINP
			
	Error String:	BL07I-EA-USER-01:ASYN1.ERRS
	I/O Status:		BL07I-EA-USER-01:ASYN1.STAT
	I/O Severity:	BL07I-EA-USER-01:ASYN1.SEVR
	
	Scan Mode:		BL07I-EA-USER-01:ASYN1.SCAN
	Process:		BL07I-EA-USER-01:ASYN1.PROC	
	"""
	def setupEpics(self, rootPV):
		self.chPort=CAClient(rootPV + ".PORT");  self.configChannel(self.chPort);
		self.chConnect=CAClient(rootPV + ".PCNCT");  self.configChannel(self.chConnect);
		self.chBaudRate=CAClient(rootPV + ".BAUD");  self.configChannel(self.chBaudRate);
		self.chDataBits=CAClient(rootPV + ".DBIT");  self.configChannel(self.chDataBits);
		self.chParity=CAClient(rootPV + ".PRTY");  self.configChannel(self.chParity);
		self.chFlowControl=CAClient(rootPV + ".FCTL");  self.configChannel(self.chFlowControl);

		self.chTimeout=CAClient(rootPV + ".TMOT");  self.configChannel(self.chTimeout);
		self.chTransfer=CAClient(rootPV + ".TMOD");  self.configChannel(self.chTransfer);

		self.chOutputFormat=CAClient(rootPV + ".OFMT");  self.configChannel(self.ch);
		self.chOutputTerminator=CAClient(rootPV + ".OEOS");  self.configChannel(self.ch);
		self.chOutputString=CAClient(rootPV + ".AOUT");  self.configChannel(self.ch);

		self.chInputFormat=CAClient(rootPV + ".IFMT");  self.configChannel(self.chInputFormat);
		self.chInputTerminator=CAClient(rootPV + ".IEOS");  self.configChannel(self.chInputTerminator);
		self.chInputString=CAClient(rootPV + ".TINP");  self.configChannel(self.chInputString);

		self.chErrorString=CAClient(rootPV + ".ERRS");  self.configChannel(self.chErrorString);
		self.chStatus=CAClient(rootPV + ".STAT");  self.configChannel(self.chStatus);
		self.chSeverity=CAClient(rootPV + ".SEVR");  self.configChannel(self.chSeverity);

		self.chScanMode=CAClient(rootPV + ".SCAN");  self.configChannel(self.chScanMode);
		self.chProcess=CAClient(rootPV + ".PROC");  self.configChannel(self.chProcess);
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();
		
	def setTimeOut(self, timeout):
		self.chTimeOut.caput(timeout);
		sleep(0.5);
		
	def toCheck(self):
		severity = self.chSeverity.caget();
		if severity == self.SEVERITY["NO_ALARM"]:
			return True;
		else:
			errorString = self.chErrorString.caget();
			raise RuntimeError("Severity Error:" + errorString)

	def setPort(self, portName, baudRate, dataBits, parity, flowControl, timeout):
		self.chPort.caput(portName);
		self.chBaudRate.caput(baudRate);
		self.chDataBits.caput(dataBits);
		self.chParity.caput(parity);
		self.chFlowControl.caput(flowControl);
		self.chTimeOut.caput(timeout);
		
		self.flush();
		self.toCheck();
		
	def setOutputTerminator(self, terminator):
		self.chOutputTerminator.caput(terminator);
		
	def setInputTerminator(self, terminator):
		self.inputTerminator.caput(terminator);
		
	def setScanMode(self, newScanMode):
		self.chScanMode.caput(newScanMode);

	def flush(self):
		self.chTransfer.caput( self.TRANSFER_MODE['Flush'] );
		self.chProcess.caput(1);
		sleep(0.5);

	def write(self, sendString):
		self.chTransfer.caput( self.TRANSFER_MODE['Write'] );
		self.chOutputString.caput(sendString);
		self.chProcess.caput(1);
		sleep(0.5);
		self.toCheck();
			
		
	def read(self):
		self.chTransfer.caput( self.TRANSFER_MODE['Read'] );
		reply=self.chInputString.caget();
		self.toCheck();
		return reply;
		
	def writeAndRead(self, sendString):
		self.chTransfer.caput( self.TRANSFER_MODE['WriteRead'] );
		self.chOutputString.caput(sendString);
		self.chProcess.caput(1);
		sleep(0.5);
		
		reply=self.chInputString.caget();
		self.toCheck();
		return reply;
		

rootPV = "BL07I-EA-USER-01:ASYN1"
portName='ty_50_1'
baudRate=EpicsAsynRS232DeviceClass.BAUDRATE['9600'];
dataBits=EpicsAsynRS232DeviceClass.DATABITS['8']
parity=EpicsAsynRS232DeviceClass.PARITY['None']
flowControl=EpicsAsynRS232DeviceClass.FLOWCONTROL['None']
timeout=5;

port1 = EpicsAsynRS232DeviceClass(rootPV);
port1.setPort(portName, baudRate, dataBits, parity, flowControl, timeout);


#The Class for creating a RS232 port based device to control the Nima Langmuir-Blodgett Trough
class NimaLangmuirBlodgettTroughDeviceClass(object):
	NLBT_CONTROL_MODE = {"SPEED"   : 0,
						 "PRESSURE": 1,
						 "AREA"    : 2 };
	
	def __init__(self, name, port):
		self.name = name;
#        self.setInputNames(['field', 'theta', 'phi']);
#        self.setOutputFormat(["%10.4f", "%10.2f", "%10.2f"]);
#		self.setExtraNames(['field']);
#        self.Units=['Telsa','Deg','Deg'];
#        self.setLevel(7);
		self.port=port;
		self.mode = None;
		self.speed = None;
		self.pressure = None;
		self.area = None;
		self.area2 = None;
		self.temperature = None;
		self.time = None;

		self.statevalue=None;
		self.attarget=None;
		
		self.running=False;
		
	def isRunning(self):
		return self.running;

	def setMode(self, newMode):
		if newMode in self.NLBT_CONTROL_MODE.values():
			self.mode = self.NLBT_CONTROL_MODE.keys()[ self.NLBT_CONTROL_MODE.values().index(newMode) ]
		elif newMode.upper() in self.NLBT_CONTROL_MODE.keys():
			self.mode = newMode.upper();
		else:
			print "Please use the right mode: 'speed/pressure/area' or 0/1/2. ";
			return;
		
		command="MODE "+str(self.NLBT_CONTROL_MODE[self.mode]);
		try:
			reply=self.port.writeAndRead(command);
			if reply != "OK":
				raise IOError("Wrong reply received!")
		except:
			raise IOError("Communication Error!")
		
		print "---> " + command;
		print "<---" + reply;

	def setArea(self, newValue):
		command="AREA "+str(newValue);
		try:
			reply=self.port.writeAndRead(command);
			if reply != "OK":
				raise IOError("Wrong reply received!")
		except:
			raise IOError("Communication Error!")

		print "---> " + command;
		print "<---" + reply;
		
	def setPressure(self, newValue):
		command="PRES "+str(newValue);
		try:
			reply=self.port.writeAndRead(command);
			if reply != "OK":
				raise IOError("Wrong reply received!")
		except:
			raise IOError("Communication Error!")

		print "---> " + command;
		print "<---" + reply;
		
	def setSpeed(self, newValue):
		command="SPEED "+str(newValue);
		try:
			reply=self.port.writeAndRead(command);
			if reply != "OK":
				raise IOError("Wrong reply received!")
		except:
			raise IOError("Communication Error!")
		
		print "---> " + command;
		print "<---" + reply;

	def readValues(self):
		command="READ";
		try:
			reply=self.port.writeAndRead(command);
			print "---> " + command;
			print "<---" + reply;
			values=reply.split(',');
			self.speed=float(values[0])
			self.pressure=float(values[1])
			self.area=float(values[2])
			self.area2=float(values[3])
			self.temperature=float(values[4])
			self.time=float(values[5]);
		except:
			raise IOError("Communication Error!")

		print "---> " + command;
		print "<---" + reply;
	
	def getStatus(self):
		command="STATUS";
		try:
			reply=self.port.writeAndRead(command);
			values=reply.split(',');
			self.statevalue=int(values[0])
			self.attarget=int(values[1])
		except:
			raise IOError("Communication Error!")
		print "---> " + command;
		print "<---" + reply;
		if self.statevalue ==1 & self.attarget == 1: #Under Remote control and at target 
			return True
		else:
			return False;
		
		
	def start(self):
		if self.running:
			return;
		
		command="START";
		try:
			reply=self.port.writeAndRead(command);
			if reply != "OK":
				raise IOError("Wrong reply received!")
		except:
			raise IOError("Communication Error!")

		self.running = True;
		
		print "---> " + command;
		print "<---" + reply;
		
	def stop(self):
		command="STOP";
		try:
			reply=self.port.writeAndRead(command);
			if reply != "OK":
				raise IOError("Wrong reply received!")
		except:
			raise IOError("Communication Error!")

		self.running = False;
		
		print "---> " + command;
		print "<---" + reply;



class TroughAreaDevice(ScannableMotionBase):
	def __init__(self, name, trough):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setOutputFormat(["%8.4f"]);
		self.setLevel(7);
		self.trough = trough;

	#ScannableMotionBase Implementation
	def getPosition(self):
		self.trough.readValues()
		return self.trough.area;

	def asynchronousMoveTo(self,newPos):
		self.trough.setMode(NimaLangmuirBlodgettTroughDeviceClass.NLBT_CONTROL_MODE['AREA']);
		self.trough.setArea(newPos);
		if not self.trough.isRunning():
			self.trough.start();

	def isBusy(self):
		return not self.trough.getStatus()
	
	def stop(self):
		self.trough.stop()


class TroughSpeedDevice(TroughAreaDevice):
	def __init__(self, name, trough):
		super.__init__(name, trough);
		
	def getPosition(self):
		self.trough.readValues()
		return self.trough.speed;

	def asynchronousMoveTo(self,newPos):
		self.trough.setMode(NimaLangmuirBlodgettTroughDeviceClass.NLBT_CONTROL_MODE['SPEED']);
		self.trough.setSpeed(newPos);
		if not self.trough.isRunning():
			self.trough.start();

class TroughPressureDevice(TroughAreaDevice):
	def __init__(self, name, trough):
		super.__init__(name, trough);
		
	def getPosition(self):
		self.trough.readValues()
		return self.trough.pressure;

	def asynchronousMoveTo(self,newPos):
		self.trough.setMode(NimaLangmuirBlodgettTroughDeviceClass.NLBT_CONTROL_MODE['PRESSURE']);
		self.trough.setPressure(newPos);
		if not self.trough.isRunning():
			self.trough.start();


#Trough over EPICS RS232
trough1 = NimaLangmuirBlodgettTroughDeviceClass('trough', port1);

#Trough over GDA RS232
sc=finder.find("sc");
port2=GdaRS232DeviceClass(sc)
trough2 = NimaLangmuirBlodgettTroughDeviceClass('trough', port2);


trough=trough1;

troughArea = TroughAreaDevice("troughArea", trough);
troughSpeed = TroughSpeedDevice("troughSpeed", trough);
troughPressure = TroughPressureDevice("troughPressure", trough);


