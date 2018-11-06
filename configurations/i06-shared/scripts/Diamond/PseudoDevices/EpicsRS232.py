from time import sleep
from java import lang
from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from gda.epics import CAClient
from gda.factory import Finder

#The Class for creating a Pseudo device to listen to RS232 via Epica PVs
#For 8512 Scaler Card used in I06 only. This scaler card is not supported by EPICS scaler record
class EpicsRS232PVClass(ScannableMotionBase):
	def __init__(self, name, pvSend, pvReceive, pvMode, pvProc, pvTimeOut):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
#		self.Units=[strUnit];
		self.setLevel(7);
#		self.setOutputFormat(["%20.12f"]);
		self.chSend=CAClient(pvSend);
		self.chSend.configure();

		self.chReceive=CAClient(pvReceive);
		self.chReceive.configure();

		self.chMode=CAClient(pvMode);
		self.chMode.configure();

		self.chProc=CAClient(pvProc);
		self.chProc.configure();

		self.chTimeOut=CAClient(pvTimeOut);
		self.chTimeOut.configure();
		
		self.lastingTime=60;
        self.cs=Finder.getInstance().find("command_server");
        
        self.resultSentout=False;

	def atScanStart(self):
		print 'Flush the port';
		self.flush();
		

	#Scannable Implementations
	def getPosition(self):
		return self.lastingTime;
	
	def asynchronousMoveTo(self,newPos):
		self.lastingTime = newPos;
		self.flush();
	  	self.str0 = self.chReceive.caget();
	  	self.resultSentout=False;
		print 'Ready to take command';
		
		i=0;
		message="Ready.";
		while True:
			i=i+1;
			self.chMode.caput("Write/Read");
			sleep(0.2);
		  	self.chSend.caput(message)
		  	sleep(2);
		  	self.str1 = self.chReceive.caget();
		  	print str(i) +': str0= ' + self.str0 +'     str1=' + self.str1;
		  	if self.str0 != self.str1:
		  	   self.str0 = self.str1;
		  	   print 'new command coming'; 
		  	   if self.str1 =='ok' and self.resultSentout ==True:
		  	   	message='Ready.';
		  	   	self.resultSentout = False;
		  	   	continue;
		  	   elif self.str1 =='ok' and self.resultSentout == False:
		  	   	continue;
		  	   result = self.interpret(self.str1);
		  	   message='Result:' + str(result);
			   #self.chSend.caput(message);
			   self.resultSentout = True;
		print 'End of monitoring.';

	def isBusy(self):
		return False;

	def atScanEnd(self):
		print 'At Scan End';

 	def toString(self):
		ss=self.getName() + " will monitor the port for " + str(self.getPosition()) + ' seconds.';
		return ss;

	def interpret(self, strGdaCommand):
		print 'Execution of GDA command: ' + strGdaCommand;
		result = self.cs.evaluateCommand(strGdaCommand);
		return result;

	def flush(self):
		#reset
		self.chMode.caput("Flush");
		self.chProc.caput(1);#press the proc button to receive
		sleep(5);
		
	def setTimeOut(self, timeout):
		#reset
		self.chTimeOut.caput(timeout);
		sleep(0.5);


pvSend       = 'BL06J-EA-USER-01:ASYN.AOUT'
pvReceive  = 'BL06J-EA-USER-01:ASYN.TINP'
pvMode  = 'BL06J-EA-USER-01:ASYN.TMOD'
pvProc  = 'BL06J-EA-USER-01:ASYN.PROC'
pvTimeOut = 'BL06J-EA-USER-01:ASYN.TMOT'

pps1 = EpicsRS232PVClass('pps1', pvSend, pvReceive, pvMode, pvProc, pvTimeOut);

