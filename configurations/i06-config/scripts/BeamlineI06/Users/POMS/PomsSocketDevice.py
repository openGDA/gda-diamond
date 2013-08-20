#A GDA Pseudo Device that invokes the moke3d Java magnet power software controller over TCP/IP

from time import sleep

from gda.device.scannable import PseudoDevice

import __main__ as gdamain

from Diamond.Comm.SocketDevice import SocketDeviceClass

#The Class for creating a socket-based Psuedo Device to control the magnet
class PomsSockteDeviceClass(PseudoDevice):
	def __init__(self, name, hostName, hostPort):
		self.setName(name);
		self.setInputNames(['field', 'theta', 'phi']);
		self.setOutputFormat(["%10.4f", "%10.2f", "%10.2f"]);
		#self.setExtraNames(['field']);
		self.Units=['Tesla','Deg','Deg'];
		self.setLevel(7);
		self.field=None;
		self.theta=None;
		self.phi=None;
		
		#How long the POMs will wait before reset itself in milli-second
		self.resetTime = 600000;
		
		self.pom=SocketDeviceClass(hostName, hostPort);
			
	def setResetTime(self, newTime):
		self.resetTime = newTime;
		print 'New reset time is: ' + str(self.resetTime);
		
	def setupServer(self, hostName, hostPort):
		self.pom=SocketDeviceClass(hostName, hostPort);

	def hello(self):
		print self.pom.sendAndReply('Hello\n\r');

	def getPomPosition(self):
		reply = self.pom.sendAndReply('FILT');
		rlist=reply.strip(' \n\r').split(' ',1);
		if rlist[0] != 'FILTD':
			print "Error: " + reply;
			rf = 999;
		else:
			rf=int(float(rlist[1]));
		return rf;
		
	#PseudoDevice Implementation
	def toString(self):
		ss=self.getName() + " [field, theta, phi]: " + str(self.getPosition());
		return ss;

	def getPosition(self):
		return [self.field, self.theta, self.phi];
	
	def asynchronousMoveTo(self,newPos):
		print newPos;
		#To check if theta and phi will be changed:
		if self.theta != newPos[1] or self.phi != newPos[2]:
			cmd='setFieldDirection %(v1)10.2f %(v2)10.2f\n\r' %{'v1': newPos[1], 'v2': newPos[2]};
			reply = self.pom.sendAndReply(cmd);
			rlist=reply.strip(' \n\r').split(' ',1);
			if rlist[0] == 'ERROR:':
				print "The moke3d command setFieldDirection failed with reply" + reply;
			else:
				print "Angle set correctly";
				self.theta = newPos[1];
				self.phi = newPos[2];
		else:
			print 'No change of angle';
		sleep(0.5);

		#Always call setField <field> <timeout> as the field may have been zerod after timeout for safety reason
		#cmd='setField %(v1)10.4f 600000\n\r' %{'v1': newPos[0]};
		cmd='setField %(field)10.4f %(timeout)d\n\r' %{'field': newPos[0], 'timeout': self.resetTime};
		reply = self.pom.sendAndReply(cmd);
		rlist=reply.strip(' \n\r').split(' ',1);
		if rlist[0] == 'ERROR:':
			print "The moke3d command setField FAILED with reply" + reply;
		else:
			print "Field set correctly";
			self.field = newPos[0];

		sleep(0.5);
		return;

	def isBusy(self):
		sleep(1);
		return False;
		

#The Class for creating a flipper based on the POMS magnet control 
class FlipperDeviceClass(PseudoDevice):
	def __init__(self, name, nameMagnet, nameCounterTimerA, nameCounterTimerB, nameCounterTimerC):
		self.setName(name);
		self.setInputNames(['field', 'theta1', 'theta2', 'phi1', 'phi2', 'countTime', 'zeroRestTime']);
		self.setExtraNames(['CountA1', 'CountA2', 'CountB1', 'CountB2', 'CountC1', 'CountC2']);
		self.setOutputFormat(["%6.4f", "%6.3f", "%6.3f", "%6.3f", "%6.3f","%6.3f", "%6.3f", "%20.12f", "%20.12f", "%20.12f", "%20.12f", "%20.12f", "%20.12f"]);
		self.setLevel(7);
		self.magnet = vars(gdamain)[nameMagnet];
		self.counterA = vars(gdamain)[nameCounterTimerA];
		self.counterB = vars(gdamain)[nameCounterTimerB];
		self.counterC = vars(gdamain)[nameCounterTimerC];
		self.field=0;
		self.theta1=0;
		self.phi1=0;
		self.theta2=0;
		self.phi2=360;
		self.countTime=1;
		self.zeroRestTime=1;
		self.count=[0, 0, 0, 0, 0, 0];
		
	def setMagnet(self, nameMagnet):
		self.magnet = vars(gdamain)[nameMagnet];
		return;

	def setCounter(self, nameCounterTimerA, nameCounterTimerB, nameCounterTimerC):
		self.counterA = vars(gdamain)[nameCounterTimerA];
		self.counterB = vars(gdamain)[nameCounterTimerB];
		self.counterC = vars(gdamain)[nameCounterTimerC];
		return;
	
	#PseudoDevice Implementation
	def atScanStart(self):
		return;

	def atScanEnd(self):
		return;
	
	def toString(self):
		ss=self.getName() + ": [field, theta1, theta2, phi1, phi2, countTime, zeroRestTime, countA1, countA2, countB1, countB2, countC1, countC2]: " + str(self.getPosition());
		#ss=self.getName() + ": " + str(self.count);
		return ss;

	def getPosition(self):
		return [self.field, self.theta1, self.theta2, self.phi1, self.phi2, self.countTime, self.zeroRestTime, self.count[0], self.count[1], self.count[2], self.count[3], self.count[4], self.count[5]];
	
	def asynchronousMoveTo(self,newPos):
		self.field=newPos[0];
		self.theta1=newPos[1];
		self.theta2=newPos[2];
		self.phi1=newPos[3];
		self.phi2=newPos[4];
		self.countTime=newPos[5];
		self.zeroRestTime=newPos[6];
		
		self.magnet.moveTo([self.field, self.theta1, self.phi1]);
		c3=self.countOnce();
		self.count[0] = c3[0];
		self.count[2] = c3[1];
		self.count[4] = c3[2];
		print 'zero rest for ' + str(self.zeroRestTime) + ' seconds ...';
		self.magnet.moveTo([0,0,0]);
		sleep(self.zeroRestTime);
		self.magnet.moveTo([self.field, self.theta2, self.phi2]);
		c3=self.countOnce();
		self.count[1]=c3[0];
		self.count[3]=c3[1];
		self.count[5]=c3[2];
		return;
	
	def countOnce(self):
#		return [100*random.random(),100*random.random(),100*random.random()];
		self.counterA.setCollectionTime(self.countTime);
		self.counterA.collectData();
		while self.counterA.isBusy():
			sleep(0.1);

		return [self.counterA.getPosition(), self.counterB.getPosition(), self.counterC.getPosition()];

	def isBusy(self):
		sleep(1);
		return False;


print "Note: Use object name 'vmag' for the POMS magenet control";
#mag = PomsSockteDeviceClass('mag','diamrl5068.diamond.ac.uk', 2729 );
#mag = PomsSockteDeviceClass('mag','172.23.16.10', 4042 );
vmag = PomsSockteDeviceClass('vmag','172.23.106.195', 4042 );

print "Note: Use object name 'vflipper' for flipping magenet on POMS";
vflipper = FlipperDeviceClass('vflipper', 'vmag', 'ca31sr', 'ca32sr', 'ca33sr');

# Remote access to the POMS PC from DLS Science Network
#rdesktop -g 1024x768 172.23.16.10

# Remote access to the POMS PC from DLS Beamline Network
#rdesktop -g 1024x768 172.23.106.195



