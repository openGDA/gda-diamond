#A GDA Pseudo Device that invokes the moke3d Java magnet power software controller over TCP/IP

from gda.device.scannable import ScannableMotionBase

from time import sleep
import random
from gdascripts.messages import handle_messages;
import __main__ as gdamain

def update(controller, msg, exceptionType=None, exception=None, traceback=None, Raise=False):
	handle_messages.log(controller, msg, exceptionType, exception, traceback, Raise)

#The Class for creating a device to calculate the XXX at two energy level
class FlipperClass(ScannableMotionBase):
	def __init__(self, name, magnetName, energyName, startEnergy, endEnergy, counterName1, counterName2, counterName3, integrationTime):
		self.setName(name);
		self.setInputNames([magnetName]);
		self.setExtraNames([energyName+'A', energyName+'B', 'detector1_A','detector1_B',  'detector2_A','detector2_B', 'detector3_A','detector3_B', 'ridio', 'rifio']);
		self.setOutputFormat(["%8.4f", "%7.3f", "%7.3f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f"]);
		self.setLevel(7);

		self.field = None;
		self.startEnergy=None;
		self.endEnergy = None;
		self.countTime = None;

		self.setMagnet(magnetName);
		self.setEnergy(energyName, startEnergy, endEnergy);
		self.setCounters(counterName1, counterName2, counterName3, integrationTime);
		
		self.countsA = [0, 0, 0];
		self.countsB = [0, 0, 0];

	def ratioFunction(self, counts):
		offset = 0;
		if counts[1] <= 0.001:
			offset = 0.001
			
		myidio = 1.0 * counts[0]/(counts[1]+offset);
		myifio = 1.0 * counts[2]/(counts[1]+offset);
		return [myidio, myifio];
		
	def setMagnet(self, magnetName):
		self.magnet = vars(gdamain)[magnetName];
		self.field = self.magnet.getPosition();
		self.setInputNames([magnetName]);
		return;

	def setEnergy(self, energyName, startEnergy, endEnergy):
		self.energy = vars(gdamain)[energyName];
		self.startEnergy = startEnergy;
		self.endEnergy = endEnergy;
		return;

	def setCounters(self, counterName1, counterName2, counterName3, integrationTime):
		self.counter1 = vars(gdamain)[counterName1];
		self.counter2 = vars(gdamain)[counterName2];
		self.counter3 = vars(gdamain)[counterName3];
		self.countTime = integrationTime;
		return;

	def countOnce(self):
		self.counter1.setCollectionTime(self.countTime);
		self.counter1.collectData();
		while self.counter1.isBusy():
			sleep(0.1);

		return [self.counter1.getPosition(), self.counter2.getPosition(), self.counter3.getPosition()];
#		return [100*random.random(),100*random.random(),100*random.random()];

#ScannableMotionBase Implementation
	def atScanStart(self):
		return;

	def atScanEnd(self):
		return;

	def toString(self):
		p=self.getPosition();
		ss = 'ridio: '+ self.getOutputFormat()[9] %p[9] + ',  rifio: '+ self.getOutputFormat()[10] %p[10];
		return ss;

	def getPosition(self):
		field = self.magnet.getPosition();
		[idioa, ifioa] = self.ratioFunction(self.countsA);
		[idiob, ifiob] = self.ratioFunction(self.countsB);

		divideByZeroHack = 0;
		if idioa <=0.001:
			update(None,"FlipperClass.getPosition - idioa <=0.001")
			divideByZeroHack = 0.001;

		[ridio, rifio] = [idiob/(idioa+divideByZeroHack), ifiob/(ifioa+divideByZeroHack)];
		
		return [field, self.startEnergy, self.endEnergy, self.countsA[0], self.countsB[0], self.countsA[1], self.countsB[1], self.countsA[2], self.countsB[2], ridio, rifio];

	def asynchronousMoveTo(self,newPos):
		print 'move magnet...';
		self.magnet.moveTo(newPos);

		print 'move energy to starting point';
		self.energy.moveTo(self.startEnergy);
		print 'counting';
		self.countsA = self.countOnce();
		
		print 'move energy to end point';
		self.energy.moveTo(self.endEnergy);
		print 'counting';
		self.countsB = self.countOnce();
		
		return;

	def isBusy(self):
		sleep(1);
		return False;



#print "Note: Use object name 'hyst2' for flipping magenet";
#hyst2 = FlipperClass('hyst2', 'magz', 'rpenergy', 700, 705, 'ca61sr', 'ca62sr', 'ca63sr', 1);
#hyst2.setMagnet('magnet.magz');
#hyst2.setEnergy('rpenergy', startEnergy=700, endEnergy=705);
#hyst2.setCounters(counterName1='ca61sr', counterName2='ca62sr', counterName3='ca63sr', integrationTime=1);



