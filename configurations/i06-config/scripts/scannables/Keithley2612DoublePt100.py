"""
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from time import sleep

#IMPORTANT: use \n terminator for ASYN:3 (2612SourceMeter)
#set the keithley rs232 paramater in the same way as on EPICS (defauls is 9600, 8, 1, none, none)
#use a null modem cable and a LF terminator
#Create Pseudo Device for Keithley2612A System Source Meter controlled over Epics Patch Panel
class Keithley2612DoublePt100(ScannableMotionBase):
	def __init__(self, name, channel, pvIn, pvOut):
		self.setName(name);
		self.setInputNames(['R_'+name])
		self.setExtraNames(['R_Diff_'+name])
		self.setOutputFormat(['%3.3f','%3.3f']);
		#self.setUnits(['V']);
		self.setLevel(6+channel);
		self.channel = channel;
		self.strFunctionSet = ['smua.source.func','smub.source.func']
		self.strFunctionGet = ['print(smua.source.func)','print(smub.source.func)']
		self.strVoltageSet = ['smua.source.levelv','smub.source.levelv'] ;
		self.strVoltageGet = ['print(smua.source.levelv)','print(smub.source.levelv)'] ;
		self.strCurrentSet = ['smua.source.leveli','smub.source.leveli'] ;
		self.strCurrentGet = ['print(smua.measure.i())','print(smub.measure.i())'] ;
		self.strVoltageSet = ['smua.source.levelv','smub.source.levelv'] ;
		self.strResistanceGet = ['print(smua.measure.r())','print(smub.measure.r())'] ;
		self.strSourceSet = ['smua.source.output','smub.source.output'];
		self.strVoltRangeSet = ['smua.source.rangev','smub.source.rangev']
		self.chIn=CAClient(pvIn);
		self.chIn.configure();
		self.chOut=CAClient(pvOut);
		self.chOut.configure();
		self.currentPosition = [0, 0]
		self.iambusy = 0

	def send(self, strCom):
		print "Out command: ", strCom;
		self.chOut.caput(strCom);
		sleep(0.2);
		v=self.chIn.caget();
		print "In String", v;
		return;

	def turnOn(self):
		strOut = self.strSourceSet[self.channel] + '=1';
		self.chOut.caput(strOut);
		print(strOut)
		sleep(1)
		self.chOut.caput(self.strResistanceGet[self.channel]);
		sleep(0.2);
		#send(

	def turnOff(self):
		strOut = self.strSourceSet[self.channel] + '=0';
		self.chOut.caput(strOut);  
		sleep(1)

	def getFunction(self):
		self.chOut.caput(self.strFunctionGet[self.channel])
		#print(self.strFunctionGet[self.channel])
		sleep(0.2)
		f=self.chIn.caget()
		return int(float(f))

	def getVoltage(self):
		self.chOut.caput(self.strVoltageGet[self.channel]);
		sleep(0.2);
		v=self.chIn.caget();
		#float(v.split('\\',2)[0])
		return float(v);

	def getResistance(self):
		self.chOut.caput(self.strResistanceGet[self.channel]);
		sleep(0.2);
		#print(self.strResistanceGet[self.channel])
		res=self.chIn.caget(); 
		#float(res.split('\\',2)[0])
		return float(res);

	def getCurrent(self):
		self.chOut.caput(self.strCurrentGet[self.channel]);
		sleep(0.2)
		curr=self.chIn.caget();	
		#float(curr.split('\\',2)[0]);	
		return float(curr)

	def setVoltage(self, v):
		strOut = self.strVoltageSet[self.channel] + '=' + str(round(v,5));
		sleep(0.5)
		print "Out String: " + strOut;
		self.chOut.caput(strOut);
		return;

	def setCurrent(self, i):
		strOut = self.strCurrentSet[self.channel] + '=' + str(round(i,5));
		#print "Out String: " + strOut;
		self.chOut.caput(strOut);
		sleep(0.5)
		self.chOut.caput(self.strResistanceGet[self.channel]);
		sleep(0.2);
		return;

	def setFunction(self,i):
		# i = 0, current source, i=1, voltage source 
		strOut = self.strFunctionSet[self.channel]+'='+str(i);
		#print "Out String: " + strOut;
		self.chOut.caput(strOut);
		return;

	#PseudoDevice Implementation
	def atScanStart(self):
		self.turnOff()
		return;

	def atScanEnd(self):
		self.turnOff()
		return;
	
	def toString(self):
		ss=self.getName() + ": Keithley 2600A Resistance readback: " + str(self.getPosition());
		return ss;

	def getPosition(self): 
		self.iambusy = 1
		self.turnOn()
		sleep(0.2); 
		current = float(self.getCurrent())
		rplus = self.getResistance()
		self.setCurrent(-current)
		sleep(0.2)
		rminus = self.getResistance()
		self.setCurrent(current)
		self.turnOff()
		#print rplus, rminus
		self.currentPosition = [(rminus+rplus)*0.5, (rminus-rplus)]
		self.iambusy = 0
		return self.currentPosition; 

	def asynchronousMoveTo(self, newVoltage):
		sleep(0.1)
		#   self.iambusy = 1
		#   self.turnOn()
		#  sleep(1)
		# current = float(self.getCurrent())
		# rplus = float(self.getResistance())
		# self.setCurrent(-current)
		# sleep(1)
		# rminus = float(self.getResistance())
		# self.setCurrent(current)
		# self.turnOff()
		# self.currentPosition = [(rminus+rplus)*0.5, (rminus-rplus)]
		# self.iambusy = 0
		return

	def isBusy(self):
		return self.iambusy
"""