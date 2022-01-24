from time import sleep
from java import lang
from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from gda.epics import CAClient

#The Class for creating a Scaler channel monitor directly from EPICS PV
#For 8512 Scaler Card used in I06 only. This scaler card is not supported by EPICS scaler record
class PositionerPVClass(ScannableMotionBase):
	def __init__(self, name, strPV):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
#		self.Units=[strUnit];
		self.setLevel(7);
		self.setOutputFormat(["%20.12f"]);
		self.ch=CAClient(strPV);

#		self.setTimePreset(time)

	def atScanStart(self):
		if not self.ch.isConfigured():
			self.ch.configure()

	#Scannable Implementations
	def getPosition(self):
		return self.getCount();
	
	def asynchronousMoveTo(self,newPos):
		self.setCollectionTime(newPos);
		self.collectData();

	def isBusy(self):
		return False;

	def atScanEnd(self):
		if self.ch.isConfigured():
			self.chTP.clearup()

	def getCount(self):
		if self.chSn.isConfigured():
			output = self.chSn.caget()
		else:
			self.chSn.configure()
			output = self.chSn.caget()
			self.chSn.clearup()
		return float(output)

 	def toString(self):
		ss=self.getName() + " :  " + str(self.getPosition());
		return ss;

