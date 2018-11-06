from time import sleep;
import math;
from gda.device.scannable import ScannableMotionBase;
from gda.epics import CAClient;

import __main__ as gdamain

#The Class for creating a Scaler channel monitor directly from EPICS PV
#For 8512 Scaler Card used in I06 only. This scaler card is not supported by EPICS scaler record
class TemperatureControllerClass(ScannableMotionBase):
	def __init__(self, name, strTempSetPV,strTempSetReadBackPV, strTemp1GetPV, strTemp2GetPV):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames(['T1', 'T2']);
		self.setOutputFormat(["%6.3f", "%6.3f", "%6.3f"]);

#		self.Units=[strUnit];
		self.setLevel(7);
#		self.setOutputFormat(["%20.12f"]);

		self.currentTemp = [0, 0];
		self.demondTemp=0;
		
		#Default delay is 10 minutes = 600 seconds
		self.waitTime = 600;
		self.waitEnough = True;
		self.errorTolerance=1;

		self.chSetTemp=CAClient(strTempSetPV);
		self.chSetTemp.configure();
		self.chSetTempRB=CAClient(strTempSetReadBackPV);
		self.chSetTempRB.configure();

		self.chGetTemp1=CAClient(strTemp1GetPV);
		self.chGetTemp1.configure();
		self.chGetTemp2=CAClient(strTemp2GetPV);
		self.chGetTemp2.configure();
		
	def setDelay(self, newWait):
		self.waitTime = newWait;

	def setError(self, newError):
		self.errorTolerance = newError;

	def setTemp(self, x):
		self.demondTemp = x;
		if self.chSetTemp.isConfigured():
			self.chSetTemp.caput(x)
		else:
			self.chSetTemp.configure()
			self.chSetTemp.caput(x)
			self.chSetTemp.clearup()
		self.waitEnough=False;
		
	def getTemp(self):
		if self.chSetTempRB.isConfigured():
			p0=self.chSetTempRB.caget()
		else:
			self.chSetTempRB.configure()
			p0=self.chSetTempRB.caget()
			self.chSetTempRB.clearup()
		
		if self.chGetTemp1.isConfigured():
			p1=self.chGetTemp1.caget()
		else:
			self.chGetTemp1.configure()
			p1=self.chGetTemp1.caget()
			self.chGetTemp1.clearup()

		if self.chGetTemp2.isConfigured():
			p2=self.chGetTemp2.caget()
		else:
			self.chGetTemp2.configure()
			p2=self.chGetTemp2.caget()
			self.chGetTemp2.clearup()
		
		self.demondTemp=float(float(p0));
		self.currentTemp=[float(p1), float(p2)];
		return [self.demondTemp, self.currentTemp[0], self.currentTemp[1]];

	def waitTillReady(self):
		if self.waitEnough:
			return;
		#wait until T1 is ready
		nToast=3;
		while nToast>0:
			self.getTemp();
			if math.fabs(self.currentTemp[0]-self.demondTemp) > self.errorTolerance:
				print 'T1 is not ready yet, wait...';
				sleep(10);
			else:
				print 'T1 is checked and seems OK.';
				sleep(10);
				nToast -= 1;

		#Wait the waitTime for T2
		print 'Wait ' + str(self.waitTime) +' seconds for T2';
		sleep(self.waitTime);
		self.waitEnough = True;
		print 'T2 wake up';

	def checkReady(self):
		return self.waitEnough;

	#Pseudo Device Implementations
	def atScanStart(self):
		if not self.chSetTemp.isConfigured():
			self.chSetTemp.configure();
		if not self.chSetTempRB.isConfigured():
			self.chSetTempRB.configure();

		if not self.chGetTemp1.isConfigured():
			self.chGetTemp1.configure();
		if not self.chGetTemp2.isConfigured():
			self.chGetTemp2.configure();

	def atScanEnd(self):
		if self.chSetTemp.isConfigured():
			self.chSetTemp.clearup()
		if self.chSetTempRB.isConfigured():
			self.chSetTempRB.clearup()

		if self.chGetTemp1.isConfigured():
			self.chGetTemp1.clearup()
		if self.chGetTemp2.isConfigured():
			self.chGetTemp2.clearup()

	def getPosition(self):
		return self.getTemp();
	
	def asynchronousMoveTo(self,newPos):
		self.setTemp(newPos);
		self.waitTillReady();

	def isBusy(self):
		if self.checkReady():
			result = False;
		else:
			result = True;
		return result;

	def toString(self):
		ss=self.getName() + " [tem, tem1, tem2]: " + str(self.getPosition());
		return ss;


class AsymmetryDeviceClass(ScannableMotionBase):
	def __init__(self, name, deviceFunName):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames(['asymmetry1', 'asymmetry2', 'asymmetry3', 'asymmetry4']);
		self.setOutputFormat(["%6.5f", "%6.5f", "%6.5f", "%6.5f", "%6.5f"]);
		self.setLevel(7);
		self.asymmetry=[0,0,0,0];
		self.average = 0;
		self.deviceFunName = deviceFunName;
		
	def funAsymmetry(self):
		#return eval(self.deviceFun + "("+ str(x1) + " , " + str(x2) + ")");
		y=vars(gdamain)[self.deviceFunName]();
		return y;
	
	def calAsymmetry(self):
		for i in range(4):
			self.asymmetry[i] = self.funAsymmetry();
			
		self.average=sum(self.asymmetry)/4;
	
	def getAsymmetry(self):
		return self.funAsymmetry();
	
	#ScannableMotionBase Implementation
	def atScanStart(self):
		return;

	def atScanEnd(self):
		return;
    
	def toString(self):
		ss=self.getName() + ": [average, asymmetry1, asymmetry2, asymmetry3, asymmetry4]: " + str(self.getPosition());
		return ss;

	def getPosition(self):
		self.calAsymmetry();
		return [self.average, self.asymmetry[0], self.asymmetry[1], self.asymmetry[2], self.asymmetry[3]];

	def asynchronousMoveTo(self,newPos):
		self.calAsymmetry();
		return;

	def isBusy(self):
		return False;

#Usage:
#from Diamond.PseudoDevices.AsymmetryDevices import TemperatureControllerClass;
#from Diamond.PseudoDevices.AsymmetryDevices import AsymmetryDeviceClass;

#pvTempSetReadBack = 'BL06J-EA-ITC-01:READ:S_TEMP'
#pvTempSet='BL06J-EA-ITC-01:SET:TEMP';
#pvTemp1='BL06J-EA-ITC-01:READ:TEMP1';
#pvTemp2 = 'BL06J-EA-ITC-01:READ:TEMP2';

#tc=TemperatureControllerClass('tc', pvTempSet, pvTempSetReadBack, pvTemp1, pvTemp2);
#asym1=AsymmetryDeviceClass('asym1', 'getAsymmetry');

#tc.setDelay(10);
#tc.setError(0.1);
