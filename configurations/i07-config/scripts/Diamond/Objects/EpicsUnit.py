
from time import sleep;

from gda.epics import CAClient;

class EpicsUnitDeviceClass(object):
	def __init__(self, name, rootPV):
		self.name = name;
		self.delay=1;
		self.setupEpics(rootPV);

	def __del__(self):
		#To clear all the Epics channels that starts with ch
		for ch in self.__dict__.keys():
			if ch.startswith('ch'):
				theChannel = self.__dict__[ch];
#				theChannel = self.__dict__.get(ch);
				self.cleanChannel(theChannel);
				print "clear channel: " + ch;
	
	def setupEpics(self, rootPV):
		pass;
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();
	
	def setDelay(self, newDelay):
		self.delay = newDelay;

	def caget(self, channel):
		try:
			if not channel.isConfigured():
				channel.configure();

			return channel.caget()
		except:
			print "Error getting position"

	def caput(self, channel, newPosition, timeout=None):
		try:
			if not channel.isConfigured():
				channel.configure()
				
			if timeout is None:
				channel.caput(newPosition);
			else:
				channel.caput(newPosition, timeout);
		except:
			print "Error setting position"
		sleep(self.delay);

	def getEpicsPositioner(self, channel, dict):
		value = int( self.caget(channel) );
		return dict[value];

	def setEpicsPositioner(self, channel, dict, newValue):
		keys = dict.keys();
		values=dict.values();

		if newValue in keys:
			out=newValue;
		elif newValue in values:
			out=values.index(newValue);
		else:
			print 'Wrong parameter, please use one of ' + str(keys) + ' or ' + str(values);
			return;
		
		self.caput(channel, out);

	def __call__(self):
		self.info();

	def info(self):
		print 'An EpicsUnitDeviceClass';
		pass;

#The Class for creating a Object that can do Epics caput and caget on the EPICS Cyberstar Fast Scintillation detector
class EpicsCyberstarScintillationDeviceClass(EpicsUnitDeviceClass):
	DISABLE = {	0:'Enable',
				1:'Disable' };
	
	SATURATION  = { 0:'Not saturated',
					1:'Saturated' };

	PEAKINGTIME = {	0:'1000 ns', 
					1:'300 ns', 
					2:'100 ns', 
					3:'50 ns' };
	
	def __init__(self, name, rootPV):
		EpicsUnitDeviceClass.__init__(self, name, rootPV);
		
	"""
	rootPV:    				BL07I-EA-CYBER-01
	DisablePV: 				BL07I-EA-CYBER-01:DISABLE
	ResetPV:   				BL07I-EA-CYBER-01:RESET
	Gain Demand and Value:  BL07I-EA-CYBER-01:GAIN:DMD, BL07I-EA-CYBER-01:GAIN:RBV
	SCA Lower Level: 		BL07I-EA-CYBER-01:SCA-LOWER:DMD, BL07I-EA-CYBER-01:SCA-LOWER:RBV
	Scan Higher Level:		BL07I-EA-CYBER-01:SCA-UPPER:DMD, BL07I-EA-CYBER-01:SCA-UPPER:RBV
	Peaking Time: 			BL07I-EA-CYBER-01:PEAKTIME:DMD
	Saturation Status:		BL07I-EA-CYBER-01:SATURATION
	"""	
	def setupEpics(self, rootPV):
		
		self.chDisable=CAClient(rootPV + ":DISABLE");  self.configChannel(self.chDisable);
		self.chReset=CAClient(rootPV + ":RESET");  self.configChannel(self.chReset);

		self.chSetGain=CAClient(rootPV + ":GAIN:DMD");  self.configChannel(self.chSetGain);
		self.chGetGain=CAClient(rootPV + ":GAIN:RBV");  self.configChannel(self.chGetGain);

		self.chSetLowerLevel=CAClient(rootPV + ":SCA-LOWER:DMD");  self.configChannel(self.chSetLowerLevel);
		self.chGetLowerLevel=CAClient(rootPV + ":SCA-LOWER:RBV");  self.configChannel(self.chGetLowerLevel);

		self.chSetHigherLevel=CAClient(rootPV + ":SCA-UPPER:DMD");  self.configChannel(self.chSetHigherLevel);
		self.chGetHigherLevel=CAClient(rootPV + ":SCA-UPPER:RBV");  self.configChannel(self.chGetHigherLevel);

		self.chPeakTime=CAClient(rootPV + ":PEAKTIME:DMD");  self.configChannel(self.chPeakTime);
		self.chSaturation=CAClient(rootPV + ":SATURATION");  self.configChannel(self.chSaturation);
	
	def enable(self):
		self.caput(self.chDisable, 0);
		sleep(1);
		value = int( self.caget(self.chDisable) );
		print 'Status: ' + str( EpicsCyberstarScintillationDeviceClass.DISABLE[value] );
		
	def disable(self):
		self.caput(self.chDisable, 1);
		sleep(1);
		value = int( self.caget(self.chDisable) );
		print 'Status: ' + str( EpicsCyberstarScintillationDeviceClass.DISABLE[value] );

	def setGain(self, newGain):
		self.caput(self.chSetGain, newGain);
		
	def getGain(self):
		value = float( self.caget(self.chGetGain) ) 
		return value;
		
	def setLowerLevel(self, newLevel):
		self.caput(self.chSetLowerLevel, newLevel);

	def getLowerLevel(self):
		value =  float( self.caget(self.chGetLowerLevel) );
		return value;

	def setHigherLevel(self, newLevel):
		self.caput(self.chSetHigherLevel, newLevel);

	def getHigherLevel(self):
		value = float( self.caget(self.chGetHigherLevel) );
		return value;

	def setPeakingTime(self, newValue):
		self.setEpicsPositioner(self.chPeakTime, EpicsCyberstarScintillationDeviceClass.PEAKINGTIME, newValue);
	def getPeakingTime(self):
		return self.getEpicsPositioner(self.chPeakTime, EpicsCyberstarScintillationDeviceClass.PEAKINGTIME);

	def getSaturationStatus(self):
		value = int( self.caget(self.chSaturation) ) 
		return EpicsCyberstarScintillationDeviceClass.SATURATION[value];

	def reset(self):
		self.caput(self.chReset, 1);
	
	
	def info(self):
		print 'Cyberstar Fast Scintillation Detector:';
		print 'Gain: ' + str( self.getGain() );
		print 'SCA Lower lavel: ' + str( self.getLowerLevel() );
		print 'SCA Upper level: ' + str( self.getHigherLevel() );
		print 'Peaking Time: ' + str( self.getPeakingTime() );
		print 'Saturation: ' + str( self.getSaturationStatus() );



#The Class for creating a Object that can do Epics caput and caget on the EPICS APD-ACE Processing Unit
class EpicsApeAceDeviceClass(EpicsUnitDeviceClass):
	DISABLE = {	0:'Enable',
				1:'Disable' };
	
	TIMESHAPING = {	0:'5 ns', 
					1:'10 ns', 
					2:'20 ns', 
					3:'30 ns' };

	MODE = {0:'INT', 
			1:'WIN' };

	BIAS = {0:'Off',
			1:'On' };
	
	def __init__(self, name, rootPV):
		EpicsUnitDeviceClass.__init__(self, name, rootPV);
		
	"""
	rootPV:    				BL07I-EA-APD-01
	
	DisablePV: 				BL07I-EA-APD-01:DISABLE

	Max Current:     		BL07I-EA-APD-01:MAXCURR:DMD, BL07I-EA-APD-01:MAXCURR:RBV
	Max Temp: 				BL07I-EA-APD-01:MAXTEMP:DMD, BL07I-EA-APD-01:MAXTEMP:RBV
	
	
	High Voltage:			BL07I-EA-APD-01:HVMON
	StartPV:   				BL07I-EA-APD-01:STARTCOUNT
	StopPV:                 BL07I-EA-APD-01:STOPCOUNT

	MaxCurrent Demand and Value: BL07I-EA-APD-01:MAXCURR:DMD, BL07I-EA-APD-01:MAXCURR:RBV
	MaxTemp Demand and Value: 	 BL07I-EA-APD-01:MAXTEMP:DMD, BL07I-EA-APD-01:MAXTEMP:RBV

	TimeShapingPV:          BL07I-EA-APD-01:SCA-OUT:DMD
	ModePV:                 BL07I-EA-APD-01:SCA:MODE:DMD
	BiasControlPV:          BL07I-EA-APD-01:BIAS:CTRL
	
	Bias Volgate:     		BL07I-EA-APD-01:BIAS:DMD, BL07I-EA-APD-01:BIAS:RBV
	LowLevel Threshold:: 	BL07I-EA-APD-01:LLTH:DMD, BL07I-EA-APD-01:LLTH:RBV	
	Win Threshold:		    BL07I-EA-APD-01:WINTH:DMD, BL07I-EA-APD-01:WINTH:RBV;

	Integration Time: 		BL07I-EA-APD-01:INTTIME
	Count repetitions:		BL07I-EA-APD-01:NREP
	"""	
	def setupEpics(self, rootPV):

		self.chDisable=CAClient(rootPV + ":DISABLE");  self.configChannel(self.chDisable);
	
		self.chSetMaxCurrent=CAClient(rootPV + ":MAXCURR:DMD");  self.configChannel(self.chSetMaxCurrent);
		self.chGetMaxCurrent=CAClient(rootPV + ":MAXCURR:RBV");  self.configChannel(self.chGetMaxCurrent);
		
		self.chSetMaxtTemp=CAClient(rootPV + ":MAXTEMP:DMD");  self.configChannel(self.chSetMaxtTemp);
		self.chGetMaxtTemp=CAClient(rootPV + ":MAXTEMP:RBV");  self.configChannel(self.chGetMaxtTemp);
		
		self.chStart=CAClient(rootPV + ":STARTCOUNT");  self.configChannel(self.chStart);
		self.chStop=CAClient(rootPV + ":STOPCOUNT");  self.configChannel(self.chStop);
		self.chHighVoltage=CAClient(rootPV + ":HVMON");  self.configChannel(self.chHighVoltage);

		self.chTimeShapping=CAClient(rootPV + ":SCA-OUT:DMD");  self.configChannel(self.chTimeShapping);
		self.chMode=CAClient(rootPV + ":SCA:MODE:DMD");  self.configChannel(self.chMode);
		self.chBiasControl=CAClient(rootPV + ":BIAS:CTRL");  self.configChannel(self.chBiasControl);

		self.chSetBiasVoltage=CAClient(rootPV + ":BIAS:DMD");  self.configChannel(self.chSetBiasVoltage);
		self.chGetBiasVoltage=CAClient(rootPV + ":BIAS:RBV");  self.configChannel(self.chGetBiasVoltage);

		self.chSetLowerLevelThreshold=CAClient(rootPV + ":LLTH:DMD");  self.configChannel(self.chSetLowerLevelThreshold);
		self.chGetLowerLevelThreshold=CAClient(rootPV + ":LLTH:RBV");  self.configChannel(self.chGetLowerLevelThreshold);

		self.chSetWinThreshold=CAClient(rootPV + ":WINTH:DMD");  self.configChannel(self.chSetWinThreshold);
		self.chGetWinThreshold=CAClient(rootPV + ":WINTH:RBV");  self.configChannel(self.chGetWinThreshold);

		self.chIntegrationTime=CAClient(rootPV + ":INTTIME");  self.configChannel(self.chIntegrationTime);
		self.chCountRepetitions=CAClient(rootPV + ":NREP");  self.configChannel(self.chCountRepetitions);


	def start(self):
		self.caput(self.chStart, 1);
		
	def stop(self):
		self.caput(self.chStop, 1);
	
	def getHighVoltage(self):
		value = float( self.caget(self.chHighVoltage) )
		return value;

	def enable(self):
		self.caput(self.chDisable, 0);
		sleep(1);
		value = int( self.caget(self.chDisable) )
		print 'Status: ' + str( EpicsApeAceDeviceClass.DISABLE[value] );
		
	def disable(self):
		self.caput(self.chDisable, 1);
		sleep(1);
		value = int( self.caget(self.chDisable) )
		print 'Status: ' + str( EpicsApeAceDeviceClass.DISABLE[value] );

	def setMaxCurrent(self, newValue):
		self.caput(self.chSetMaxCurrent, newValue);
	def getMaxCurrent(self):
		value = float( self.caget(self.chGetMaxCurrent) ) 
		return value;

	def setMaxTemp(self, newValue):
		self.caput(self.chSetMaxtTemp, newValue);
	def getMaxTemp(self):
		value = float( self.caget(self.chGetMaxtTemp) ) 
		return value;

	def setScaTimeShaping(self, newValue):
		self.setEpicsPositioner(self.chTimeShapping, EpicsApeAceDeviceClass.TIMESHAPING, newValue);
	def getScaTimeShaping(self):
		return self.getEpicsPositioner(self.chTimeShapping, EpicsApeAceDeviceClass.TIMESHAPING);
		
	def setScaMode(self, newValue):
		self.setEpicsPositioner(self.chMode, EpicsApeAceDeviceClass.MODE, newValue);
	def getScaMode(self):
		return self.getEpicsPositioner(self.chMode, EpicsApeAceDeviceClass.MODE);

	def setBiasControl(self, newValue):
		self.setEpicsPositioner(self.chBiasControl, EpicsApeAceDeviceClass.BIAS, newValue);
	def getBiasControl(self):
		return self.getEpicsPositioner(self.chBiasControl, EpicsApeAceDeviceClass.BIAS);

	def setBiasVoltage(self, newValue):
		self.caput(self.chSetBiasVoltage, newValue);
	def getBiasVoltage(self):
		value = float( self.caget(self.chGetBiasVoltage) );
		return value;

	def setLowLevelThreshold(self, newValue):
		self.caput(self.chSetLowerLevelThreshold, newValue);
	def getLowLevelThreshold(self):
		value = float( self.caget(self.chGetLowerLevelThreshold) );
		return value;
	
	def setWinThreshold(self, newValue):
		self.caput(self.chSetWinThreshold, newValue);
	def getWinThreshold(self):
		value = float( self.caget(self.chGetWinThreshold) );
		return value;

	def setIntegrationTime(self, newValue):
		self.caput(self.chIntegrationTime, newValue);
	def getIntegrationTime(self):
		value = self.caget(self.chIntegrationTime);
		return value;

	def setCountRepetitions(self, newValue):
		self.caput(self.chCountRepetitions, newValue);
	def getCountRepetitions(self):
		value = int( self.caget(self.chCountRepetitions) );
		return value;
	def info(self):
		print 'APD-ACE Pulse Processing Unit:';
		
		print 'Max current: ' + str( self.getMaxCurrent() );
		print 'Max temp: ' + str( self.getMaxTemp() );
		
		print 'SCA time shaping: ' + str( self.getScaTimeShaping() );
		print 'SCA mode: ' + str( self.getScaMode() );
		print 'Bias control: ' + str( self.getBiasControl() );
		
		print 'Bias voltage: ' + str( self.getBiasVoltage() );
		print 'Low level threshold: ' + str( self.getLowLevelThreshold() );
		print 'Win threshold: ' + str( self.getWinThreshold() );
		
		print 'Integration time: ' + str( self.getIntegrationTime() );
		print 'Count repetitions: ' + str( self.getCountRepetitions() );
		
		print 'High volgate: ' + str( self.getHighVoltage() );


#Example:
#from Diamond.Objects.EpicsUnit import EpicsApeAceDeviceClass;
#from Diamond.Objects.EpicsUnit import EpicsCyberstarScintillationDeviceClass;

#cyberstar=EpicsCyberstarScintillationDeviceClass('cyberstar', 'BL07I-EA-CYBER-01');
#alias("cyberstar");

#apd=EpicsApeAceDeviceClass('apd', 'BL07I-EA-APD-01');
#alias("apd");


