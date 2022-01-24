#A GDA Pseudo Device that can flip magnetic fields


from gda.device.scannable import ScannableMotionBase

from time import sleep
import random

import __main__ as gdamain

from Diamond.PseudoDevices.ID_Polarisation import ID_PolarisationClass;

from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

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
		Id, I0, If = counts[0], counts[1], counts[2];
		if I0 <= 0.001:
			I0 += 0.001;
			
		idi0 = float(Id)/I0;
		ifi0 = float(If)/I0;
		
		return [idi0, ifi0];
		
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

	def countMany(self, howmany):
		cnt_list=[self.countOnce() for i in range(howmany)];
		c_sum=map(sum, zip( *cnt_list ) )
		return c_sum

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

		offset1 = offset2 = 0;
		if idioa <=0.001:
			logger.simpleLog("FlipperClass.getPosition - idioa <=0.001");
			offset1 = 0.001;
			
		if ifioa <=0.001:
			logger.simpleLog("FlipperClass.getPosition - ifioa <=0.001");
			offset2 = 0.001;

		[ridio, rifio] = [idiob/(idioa+offset1), ifiob/(ifioa+offset2)];
		
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


class DichroicFlipperClass(FlipperClass):

	def __init__(self, name, magnetName, energyName, startEnergy, endEnergy, polarisationName, polarisation1, polarisation2, counterName1, counterName2, counterName3, integrationTime):

		FlipperClass.__init__(self, name, magnetName, energyName, startEnergy, endEnergy, counterName1, counterName2, counterName3, integrationTime);

#		self.setExtraNames([energyName+'A', energyName+'B', 'detector1_A','detector1_B',  'detector2_A','detector2_B', 'detector3_A','detector3_B', 'ridio', 'rifio']);
		self.setExtraNames([energyName+'A', energyName+'B', 'detector1_A','detector1_B',  'detector2_A','detector2_B', 'detector3_A','detector3_B', 'detector1_AA', 'detector1_BB', 'detector2_AA','detector2_BB', 'detector3_AA','detector3_BB', 'ridio1', 'rifio1', 'ridio2', 'rifio2', 'ridioDiff', 'rifioDiff']);
#		self.setOutputFormat(["%8.4f", "%7.3f", "%7.3f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f"]);
		self.setOutputFormat(["%8.4f", "%7.3f", "%7.3f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f", "%20.6f"]);

		self.pol1=None;
		self.pol2 = None;
		self.setPolarisation(polarisationName, polarisation1, polarisation2);

		self.countsAA = [0, 0, 0];
		self.countsBB = [0, 0, 0];

	def setPolarisation(self, polarisationName, pol1, pol2):
		self.polarisation = vars(gdamain)[polarisationName];
		idpValues = ID_PolarisationClass.POLARISATIONS.values();
		if pol1 in idpValues and pol2 in idpValues:
			self.pol1 = pol1;
			self.pol2 = pol2;
		else:
			raise NameError("Wrong polarisation Positions")
		
	def toString(self):
		p=self.getPosition();
		ss = 'ridio1: '+ self.getOutputFormat()[15] %p[15] + ',  rifio1: '+ self.getOutputFormat()[16] %p[16] + 'ridio2: '+ self.getOutputFormat()[17] %p[17] + ',  rifio2: '+ self.getOutputFormat()[18] %p[18] + 'ridioDiff: '+ self.getOutputFormat()[19] %p[19] + ',  rifioDiff: '+ self.getOutputFormat()[20] %p[20];
		return ss;

	def getPosition(self):
		field = self.magnet.getPosition();
		[idioa, ifioa] = self.ratioFunction(self.countsA);
		[idiob, ifiob] = self.ratioFunction(self.countsB);

		offset1 = offset2 = 0;
		if idioa <=0.001:
			logger.simpleLog("FlipperClass.getPosition - idioa <=0.001");
			offset1 = 0.001;
			
		if ifioa <=0.001:
			logger.simpleLog("FlipperClass.getPosition - ifioa <=0.001");
			offset2 = 0.001;

		[ridio1, rifio1] = [idiob/(idioa+offset1), ifiob/(ifioa+offset2)];

		[idioa, ifioa] = self.ratioFunction(self.countsAA);
		[idiob, ifiob] = self.ratioFunction(self.countsBB);

		offset1 = offset2 = 0;
		if idioa <=0.001:
			logger.simpleLog("FlipperClass.getPosition - idioa <=0.001");
			offset1 = 0.001;
			
		if ifioa <=0.001:
			logger.simpleLog("FlipperClass.getPosition - ifioa <=0.001");
			offset2 = 0.001;

		[ridio2, rifio2] = [idiob/(idioa+offset1), ifiob/(ifioa+offset2)];

		ridioDiff=ridio1-ridio2;
		rifioDiff=rifio1-rifio2;
		
		return [field, self.startEnergy, self.endEnergy, self.countsA[0], self.countsB[0], self.countsA[1], self.countsB[1], self.countsA[2], self.countsB[2], self.countsAA[0], self.countsBB[0], self.countsAA[1], self.countsBB[1], self.countsAA[2], self.countsBB[2], ridio1, rifio1, ridio2, rifio2, ridioDiff, rifioDiff];

	def countTwice(self, countsHolderA, countsHolderB):
		print 'move energy to starting point';
		self.energy.moveTo(self.startEnergy);
		print 'counting at energy level: ' + str(self.energy.getPosition());
		countsHolderA = self.countOnce();
		
		print 'move energy to end point';
		self.energy.moveTo(self.endEnergy);
		print 'counting at energy level: ' + str(self.energy.getPosition());
		countsHolderB = self.countOnce();
	

	def asynchronousMoveTo(self,newPos):
		print 'move magnet...';
		self.magnet.moveTo(newPos);

		currentPol = self.polarisation.getPosition();
		
		if currentPol != self.pol2:
			print 'change polarisation to first position';
			self.polarisation.moveTo(self.pol1);
			self.countTwice(self.countsA, self.countsB);
			
			print 'change polarisation to second position';
			self.polarisation.moveTo(self.pol2);
			self.countTwice(self.countsAA, self.countsBB);
		else:#To save time, do the second position first to avoid the time consuming ID polarisation changing.
			print 'change polarisation to second position';
			self.polarisation.moveTo(self.pol2);
			self.countTwice(self.countsAA, self.countsBB);
			
			print 'change polarisation to first position';
			self.polarisation.moveTo(self.pol1);
			self.countTwice(self.countsA, self.countsB);
		return;


#from Diamond.PseudoDevices.Flipper import FlipperClass, DichroicFlipperClass

#print "Note: Use object name 'hyst' for the hysteresis measurement with flipping magnet";
#hyst = FlipperClass('hyst', 'magz', 'rpenergy', 700, 705, 'ca61sr', 'ca62sr', 'ca63sr', 1);
#hyst.setMagnet('magnet.magz');
#hyst.setEnergy('rpenergy', startEnergy=700, endEnergy=705);
#hyst.setCounters(counterName1='ca61sr', counterName2='ca62sr', counterName3='ca63sr', integrationTime=1);


#print "Note: Use object name 'dhyst' for the hysteresis measurement with dichroitic flipping magnet";
#dhyst = DichroicFlipperClass('dhyst', 'magz', 'denergy', 770, 777, 'iddpol', 'PosCirc', 'NegCirc' , 'ca61sr', 'ca62sr', 'ca63sr', 1);
#dhyst.setMagnet('magnet.magz');
#dhyst.setEnergy('denergy', startEnergy=700, endEnergy=750);
#dhyst.setCounters(counterName1='ca61sr', counterName2='ca62sr', counterName3='ca63sr', integrationTime=1);
#dhyst.setPolarisation('iddpol', pol1='PosCirc', pol2='NegCirc');
