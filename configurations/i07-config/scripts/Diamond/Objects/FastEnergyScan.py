from time import sleep
from java import lang
#from gda.device.scannable import ScannableBase
#from gda.device import Scannable
from gda.epics import CAClient
from gda.data import NumTracker
from gda.jython import InterfaceProvider
#import gda

from gda.analysis import Plotter


import scisoftpy as dnp

# #The Class for creating a Constant Velocity Scan object directly from EPICS PV
# #Motor status pvs
# pvScanReady01       = 'BL06I-MO-FSCAN-01:PGM:HOME.RVAL'
# pvScanReady02       = 'BL06I-MO-FSCAN-01:PGM:MODE.RVAL'
# pvScanReady03       = 'BL06I-MO-FSCAN-01:ID:ENABLE.RVAL'
# pvScanReady04       = 'BL06I-MO-FSCAN-01:DATA:OK.RVAL'
# 
# #setup PVs
# pvStartEnergy       = 'BL06I-MO-FSCAN-01:EV:START'
# pvEndEnergy        = 'BL06I-MO-FSCAN-01:EV:FINISH'
# pvScanTime         = 'BL06I-MO-FSCAN-01:TIME'
# #pvNumberOfPoints= 'BL06I-MO-FSCAN-01:NELM'
# pvNumberOfPoints= 'BL06I-MO-FSCAN-01:NPULSES'
# pvBuildButton       = 'BL06I-MO-FSCAN-01:BUILD'
# pvStartButton        = 'BL06I-MO-FSCAN-01:START'
# pvReadyState       = 'BL06I-MO-FSCAN-01:RUN:STATE'
# 
# #waveform PVs
# #pvDataChannel01 = 'BL06I-DI-8512-02:CH1DATA'
# #pvDataChannel02 = 'BL06I-DI-8512-02:CH2DATA'
# #pvDataChannel03 = 'BL06I-DI-8512-02:CH3DATA'
# #pvDataChannel04 = 'BL06I-DI-8512-02:CH4DATA'
# #pvEnergyIDGAP  = 'BL06I-DI-8512-02:CH5DATA'
# #pvEnergyPGM     = 'BL06I-DI-8512-02:CH6DATA'
# #pvElementCounter='BL06I-DI-8512-02:ELEMENTCOUNTER'
# 
# pvDataChannel01 = 'BL06I-MO-FSCAN-01:CH1DATA'
# pvDataChannel02 = 'BL06I-MO-FSCAN-01:CH2DATA'
# pvDataChannel03 = 'BL06I-MO-FSCAN-01:CH3DATA'
# pvDataChannel04 = 'BL06I-MO-FSCAN-01:CH4DATA'
# pvEnergyIDGAP  = 'BL06I-MO-FSCAN-01:CH5DATA'
# pvEnergyPGM     = 'BL06I-MO-FSCAN-01:CH6DATA'
# pvElementCounter='BL06I-MO-FSCAN-01:ELEMENTCOUNTER'

class FastEnergyScanClass:
	def __init__(self):
		self.startEnergy=CAClient(pvStartEnergy);
		self.endEnergy=CAClient(pvEndEnergy);
		self.scanTime=CAClient(pvScanTime);
		self.numberOfPoints=CAClient(pvNumberOfPoints);
		self.startButton=CAClient(pvStartButton);
		self.status=CAClient(pvReadyState);

		self.buildButton=CAClient(pvBuildButton);

		self.elementCounter=CAClient(pvElementCounter);

		self.channel01=CAClient(pvDataChannel01);
		self.channel02=CAClient(pvDataChannel02);
		self.channel03=CAClient(pvDataChannel03);
		self.channel04=CAClient(pvDataChannel04);
		self.energyPGM=CAClient(pvEnergyPGM);
		self.energyIDGAP=CAClient(pvEnergyIDGAP);

		self.scanReady01 = CAClient(pvScanReady01);
		self.scanReady02 = CAClient(pvScanReady02);
		self.scanReady03 = CAClient(pvScanReady03);
		self.scanReady04 = CAClient(pvScanReady04);
		
		self.scanStatus='Idle';
		self.arrayHead=0;

		self.se=400;
		self.ee=700;

	def atScanStart(self):
		self.scanStatus='Idle';
		self.arrayHead=0;
		if not self.startEnergy.isConfigured():
			self.startEnergy.configure()
		if not self.endEnergy.isConfigured():
			self.endEnergy.configure()
		if not self.scanTime.isConfigured():
			self.scanTime.configure()
		if not self.numberOfPoints.isConfigured():
			self.numberOfPoints.configure()
		if not self.startButton.isConfigured():
			self.startButton.configure()
		if not self.buildButton.isConfigured():
			self.buildButton.configure()
		if not self.status.isConfigured():
			self.status.configure()

		if not self.elementCounter.isConfigured():
			self.elementCounter.configure()

		if not self.channel01.isConfigured():
			self.channel01.configure()
		if not self.channel02.isConfigured():
			self.channel02.configure()
		if not self.channel03.isConfigured():
			self.channel03.configure()
		if not self.channel04.isConfigured():
			self.channel04.configure()
		if not self.energyPGM.isConfigured():
			self.energyPGM.configure()
		if not self.energyIDGAP.isConfigured():
			self.energyIDGAP.configure()

		if not self.scanReady01.isConfigured():
			self.scanReady01.configure()
		if not self.scanReady02.isConfigured():
			self.scanReady02.configure()
		if not self.scanReady03.isConfigured():
			self.scanReady03.configure()
		if not self.scanReady04.isConfigured():
			self.scanReady04.configure()


	def atScanEnd(self):
		self.scanStatus='Idle';
		self.arrayHead=0;
		if self.startEnergy.isConfigured():
			self.startEnergy.clearup()
		if self.endEnergy.isConfigured():
			self.endEnergy.clearup()
		if self.scanTime.isConfigured():
			self.scanTime.clearup()
		if self.numberOfPoints.isConfigured():
			self.numberOfPoints.clearup()
		if self.startButton.isConfigured():
			self.startButton.clearup()
		if self.buildButton.isConfigured():
			self.buildButton.clearup()
		if self.status.isConfigured():
			self.status.clearup()

		if self.elementCounter.isConfigured():
			self.elementCounter.clearup()

		if self.channel01.isConfigured():
			self.channel01.clearup()
		if self.channel02.isConfigured():
			self.channel02.clearup()
		if self.channel03.isConfigured():
			self.channel03.clearup()
		if self.channel04.isConfigured():
			self.channel04.clearup()
		if self.energyPGM.isConfigured():
			self.energyPGM.clearup()
		if self.energyIDGAP.isConfigured():
			self.energyIDGAP.clearup()

		if self.scanReady01.isConfigured():
			self.scanReady01.clearup()
		if self.scanReady02.isConfigured():
			self.scanReady02.clearup()
		if self.scanReady03.isConfigured():
			self.scanReady03.clearup()
		if self.scanReady04.isConfigured():
			self.scanReady04.clearup()

	#To check the PGM and ID motors are ready for the fast scan
	def checkMotorReady(self):
		c1= int(float(self.scanReady01.caget()));
		c2= int(float(self.scanReady02.caget()));
		c3= int(float(self.scanReady03.caget()));
		c4= int(float(self.scanReady04.caget()));
		return (c1 == 0 and c2 == 0 and c3 == 0 and c4 == 0);

	def setEnergyRange(self, startEnergy, endEnergy):
		self.se=startEnergy;
		self.ee=endEnergy;
		self.startEnergy.caput(startEnergy-3)
		self.endEnergy.caput(endEnergy+3)

	def setTime(self, scanTime, pointTime):
		numberOfPoints = scanTime/pointTime;
		self.scanTime.caput(scanTime)
		self.numberOfPoints.caput(numberOfPoints)

	#trigger the fast scan
	def start(self):
		self.startButton.caput(1)

	#trigger the fast scan
	def build(self):
		self.buildButton.caput('Busy') # click the build button


	def isBuilt(self):
		strStatus = self.getStatus();
		if strStatus == 'Scan ready': #Finished building
			return True
		else:
			return False;

	#Total 6 status from Epics, plus internal Idle status
	##	"Scan complete"
	##	"Scan aborted"
	#	"Moving PGM to midpoint"
	#	"Calculating parameters"
	##	"Moving IDD and PGM to start position"
	## "Scan ready"
	##	"Starting scan move"
	#	"Scanning"
	##	"Scan complete"
	#	"Idle"
	def getStatus(self):
		newScanStatus = self.status.caget();
		if newScanStatus != self.scanStatus: # scan status changed
			self.scanStatus = newScanStatus;
			print self.scanStatus;
		return self.scanStatus;
				
	def isBusy(self):
		strStatus = self.getStatus();
		if strStatus == 'Scan complete':
			print 'fast energy scan finished.'
			return False;
		else:
			return True;

	def isScanning(self):
		strStatus = self.getStatus();
		if strStatus == 'Scanning'  or strStatus == 'Starting scan move':
			return True;
		else:
			return False;

	#To get the number of valid data from the waveform
	def getDataNumbers(self):
		strLength = self.elementCounter.caget()
		return int(float(strLength));

	def saveData(self):
		numberOfPoints = self.getDataNumbers();
		#self.printData(numberOfPoints);
		self.saveSRSData(numberOfPoints);

	def saveSRSData(self, numberOfPoints):
		srsHeader=[" &SRS\n", " SRSRUN=null,SRSDAT=null,SRSTIM=null,\n", " SRSSTN='null',SRSPRJ='null    ',SRSEXP='null    ',\n", " SRSTLE='                                                            ',\n", " SRSCN1='        ',SRSCN2='        ',SRSCN3='        ',\n", " &END\n"];

		try:
			runs=NumTracker("tmp")
			nextNum = runs.getCurrentFileNumber()
			#nextNum = runs.incrementNumber()
			path = InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir")
			fileName = path + "/" + str(nextNum+1) + ".dat"
			print fileName
			fh=open(fileName, 'w');

			#SRS Header
			for i in range(len(srsHeader)):
				fh.write(srsHeader[i]);

			titleLine='%(v1)s \t %(v2)s \t %(v3)s \t %(v4)s \t %(v5)s \t %(v6)s \n' %{'v1': 'PGM Energy', 'v2': 'ID GAP Energy', 'v3': 'Channel 1', 'v4': 'Channel 2','v5': 'Channel 3','v6': 'Channel 4'};
			fh.write(titleLine);

			arrayEnergyPGM=self.energyPGM.cagetArrayDouble();
			arrayEnergyIDGAP=self.energyIDGAP.cagetArrayDouble();
			arrayChannel01=self.channel01.cagetArrayDouble();
			arrayChannel02=self.channel02.cagetArrayDouble();
			arrayChannel03=self.channel03.cagetArrayDouble();
			arrayChannel04=self.channel04.cagetArrayDouble();
			
			for i in range( numberOfPoints):
				if arrayEnergyPGM[i] < self.se:
					continue;
				if arrayEnergyPGM[i] > self.ee:
					continue;
				#print i, arrayEnergyPGM[i], arrayEnergyIDGAP[i], arrayChannel01[i], arrayChannel02[i], arrayChannel03[i], arrayChannel04[i];
				newLine='%(v1).8f \t %(v2).8f \t %(v3).8f \t %(v4).8f \t %(v5).8f \t %(v6).8f \n' %{'v1': arrayEnergyPGM[i], 'v2': arrayEnergyIDGAP[i], 'v3': arrayChannel01[i], 'v4': arrayChannel02[i],'v5': arrayChannel03[i],'v6': arrayChannel04[i]};
				fh.write(newLine);
			fh.close();
			runs.incrementNumber();
		except:
			print "ERROR: Could not save data into file."

	def printData(self, numberOfPoints):
		arrayEnergyPGM=self.energyPGM.cagetArrayDouble();
		arrayEnergyIDGAP=self.energyIDGAP.cagetArrayDouble();
		arrayChannel01=self.channel01.cagetArrayDouble();
		arrayChannel02=self.channel02.cagetArrayDouble();
		arrayChannel03=self.channel03.cagetArrayDouble();
		arrayChannel04=self.channel04.cagetArrayDouble();

		for i in range( numberOfPoints ):
			print i, arrayEnergyPGM[i], arrayEnergyIDGAP[i], arrayChannel01[i], arrayChannel02[i], arrayChannel03[i], arrayChannel04[i];

	def plotWholeData(self, numberOfPoints):
		arrayEnergyPGM=self.energyPGM.cagetArrayDouble();
		arrayEnergyIDGAP=self.energyIDGAP.cagetArrayDouble();
		arrayChannel01=self.channel01.cagetArrayDouble();
		arrayChannel02=self.channel02.cagetArrayDouble();
		arrayChannel03=self.channel03.cagetArrayDouble();
		arrayChannel04=self.channel04.cagetArrayDouble();
		
		dataSetPGM=dnp.array([numberOfPoints]);

		for i in range( numberOfPoints ):
			dataSetPGM.set(arrayEnergyPGM[i], i);

		# Removed as won't work with RCP client. Talk to Mark Basham if need be.
		# dvp=Plotter();
		# dvp.plotOver("Fast Scan Panel", dataSetPGM.getIndexDataSet(), dataSetPGM);

	def plotData(self):
		newHead=self.getDataNumbers();
		if self.arrayHead >=newHead:
			print "No new data added for plotting";
			return;
		self.arrayHead = newHead;

		#to get new data
		arrayEnergyPGM=self.energyPGM.cagetArrayDouble();
		arrayEnergyIDGAP=self.energyIDGAP.cagetArrayDouble();
		arrayChannel01=self.channel01.cagetArrayDouble();
		arrayChannel02=self.channel02.cagetArrayDouble();
		arrayChannel03=self.channel03.cagetArrayDouble();
		arrayChannel04=self.channel04.cagetArrayDouble();

		dataSetEnergyPGM=dnp.zeros([newHead]);
		dataSetEnergyPGM.setName("PGM Energy");
		
		dataSetEnergyIDGAP=dnp.zeros([newHead]);
		dataSetEnergyIDGAP.setName("ID Gap Energy")
		
		dataSetChannel01=dnp.zeros([newHead]); 
		dataSetChannel01.setName("Channel 1");
		
		dataSetChannel02=dnp.zeros([newHead]); 
		dataSetChannel02.setName("Channel 2");
		
		dataSetChannel03=dnp.zeros([newHead]);
		dataSetChannel03.setName("Channel 3");
		
		dataSetChannel04=dnp.zeros([newHead]);
		dataSetChannel04.setName("Channel 4");
		
		for i in range(0, newHead):
			#print i, arrayEnergyPGM[i], arrayEnergyIDGAP[i], arrayChannel01[i], arrayChannel02[i], arrayChannel03[i], arrayChannel04[i];
			dataSetEnergyPGM[i] = arrayEnergyPGM[i]
			dataSetEnergyIDGAP[i] = arrayEnergyIDGAP[i]
			dataSetChannel01[i] = arrayChannel01[i]
			dataSetChannel02[i] = arrayChannel02[i]
			dataSetChannel03[i] = arrayChannel03[i]
			dataSetChannel04[i] = arrayChannel04[i]
			#print i, arrayEnergyPGM[i], arrayEnergyIDGAP[i], arrayChannel01[i], arrayChannel02[i], arrayChannel03[i], arrayChannel04[i];

		dvp=Plotter();
		indexDataSet=dataSetEnergyPGM.getIndexDataSet()
		#dvp.plot("Data Vector", indexDataSet, [dataSetChannel01, dataSetChannel02, dataSetChannel03, dataSetChannel04]);
		dvp.plot("Fast Scan Panel", dataSetEnergyPGM, [dataSetChannel01, dataSetChannel02, dataSetChannel03, dataSetChannel04]);


#lpr -P b.i06.cc1.col.1 -o InputSlot=Auto -o Resolution=600dpi -o PageSize=A4 -o Duplex=DuplexNoTumble
	
	
