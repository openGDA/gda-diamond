#A GDA Pseudo Device that invokes the moke3d Java magnet power software controller over TCP/IP

from gda.device.scannable import ScannableMotionBase;
from gda.device.Detector import BUSY;
from org.eclipse.january.dataset import DatasetFactory
# XXX Chosen to ignore old datset because it would be  incompatible with core scripts

from time import sleep

import __main__ as gdamain

#
class FlippingDeviceClass(ScannableMotionBase):
	'''
	A 2D scan device which scans one device X and at each x, scan the second device Y. 
	At each point y, use detectors to collect data and pass a data set to process.
	Usage:
		f1 = FlippingDeviceClass('f1', "scannerName", "flipperName", flipPositions=[10, 20], detectorNames, integrationTime, [Algorism01Processor()]);
	To change the devices:
		f1.setScanner("testMotor2");
		f1.setFlipper("testMotor1", [-20, 20]);
		f1.setDetectors(['dummyCounter','dummyCounter1', 'dummyCounter2'], integrationTime=1);
		f1.setProcessors([Algorism01Processor()]);
    
	'''
	def __init__(self, name, scannerName, flipperName, flipPositions, detectorNames, integrationTime, processors=[]):
		self.setName(name);
#		self.setLevel(self.detector.getLevel() + 1);

		self.scanner=None;
		self.flipper = None;
		self.flipPositions=[];
		self.flipPositionsReadback=[];
		self.detectors = [];
		self.countTime = None;
		self.processors = processors;
		
		self.setScanner(scannerName);
		self.setFlipper(flipperName, flipPositions);
		self.setDetectors(detectorNames, integrationTime);
		
		self.readouts = [];
		self.dataset = None;

		self.scannableSetup();
		
	def scannableSetup(self):
		self.setInputNames( [self.scanner.getName()] );
		
		extraNames = [];
		outputFormat = ['%f'];
		i=0;
		for p in self.flipPositions:
			i+=1;
			extraNames.append(self.flipper.getName() + '_pos_'+str(i));
			outputFormat.append('%f');
			for d in self.detectors:
				extraNames.append(d.getName());
				outputFormat.append('%f');
			
		if self.processors != None:
			for processor in self.processors:
				for label in processor.labelList:
					extraNames.append(self.name + '_' + label)
					outputFormat.append( '%f' );

		self.setExtraNames(extraNames);
		self.setOutputFormat(outputFormat);
		
		
	def setScanner(self, scannerName):
		self.scanner = vars(gdamain)[scannerName];
		self.setInputNames([scannerName]);
		self.scannableSetup();
		return;

	def setFlipper(self, flipperName, flipPositions):
		self.flipper = vars(gdamain)[flipperName];
		self.flipPositions = flipPositions;
		self.scannableSetup();
		return;

	def setDetectors(self, detectorNames, integrationTime):
		self.detectors = [];
		for detName in detectorNames:
			self.detectors.append(vars(gdamain)[detName]);
			
		self.countTime = integrationTime;
		self.scannableSetup();
		return;

	def setProcessors(self, processors):
		self.processors = processors
		self.scannableSetup();


	def isDetectorsBusy(self):
		for det in self.detectors:
#TODO: 			
#			if det.getStatus() == BUSY:
			if det.isBusy():
				return True;
		return False;
		
	def countOnce(self):
		detector0 = self.detectors[0];
		
		detector0.setCollectionTime(self.countTime);
		detector0.collectData();
		while detector0.isBusy():
			sleep(0.1);

		readout=[];
		for det in self.detectors:
			readout.append(det.readout());
		return readout;

	def getResult(self, processor, dataset):
		result = [];

		if dataset is None:
			print "Warning: None dataset";
			return result;
		
		twodDataSetResult = processor.process(dataset, 0, 0);
		d = twodDataSetResult.resultsDict
		for key in processor.labelList:
			result.append(d[key])
		return result

	def setResult(self, pos):
		self.result = {}
		for key, val in zip(list(self.getInputNames()) + list(self.getExtraNames()), pos):
			self.result[key] = val


#ScannableMotionBase Implementation
	def atScanStart(self):
		return;

	def atScanEnd(self):
		return;

	def asynchronousMoveTo(self,newPos):
		'''
		Moving the scanner to the newPos,
		Moving the flipper to position 0, then read out all detectors: [d00, d01, ... , d0n]
		Moving the flipper to position 1, then read out all detectors: [d10, d11, ... , d1n]
		...
		Moving the flipper to position m, then read out all detectors: [dm0, dm1, ... , dmn]
		
		Create a DataSet that represents the about matirx for analysis 
		'''
		
		print 'move scanning device...';
		self.scanner.moveTo(newPos);
		
		self.readouts = [];
		self.flipPositionsReadback = [];
		for flipPos in self.flipPositions:
			print 'move ' + self.flipper.getName() + ' to ' + str(flipPos);
			self.flipper.moveTo(flipPos);
			self.flipPositionsReadback.append(self.flipper.getPosition());
			print 'counting';
			readoutp=self.countOnce();
			self.readouts.append(readoutp);
		self.dataset=DatasetFactory.createFromObject(self.readouts) #ds is a new DataSet with dimension [numberOfFlipPositions, NumberOfDetectors];
		return;

	def getPosition(self):
		if self.dataset is None:
			print "Dataset is none!"
			return None;

		result = [self.scanner.getPosition()];
		
		i=0;
		for pr in self.readouts:
#			result.append(self.flipPositions[i]); #flipper demand positions
			result.append(self.flipPositionsReadback[i]); #flipper readback positions
			for r in pr:
				result.append(r);#detector readout at that flipper position
			i+=1;

		if self.processors != None:
			for processor in self.processors:
				result += list(self.getResult(processor, self.dataset));
			
		self.setResult(result);
		return result;

	def toString(self):
		p=self.getPosition();
		return str(p);

	def isBusy(self):
		if self.scanner.isBusy() or self.flipper.isBusy() or self.isDetectorsBusy():
			return True;
		else:
			return False;

##################################################
from gdascripts.analysis.datasetprocessor.twod.TwodDataSetProcessor import TwodDataSetProcessor

class Algorism01Processor(TwodDataSetProcessor):
	def __init__(self, name='Algorism01Processor',
				 labelList=('val', 'v0', 'v1'),
				 keyxlabel='v0', 
				 keyylabel='v1', 
				 formatString='Value %f, %f, %f (val, v0, v1)'
				 ):
		TwodDataSetProcessor.__init__(self, name, labelList, keyxlabel, keyylabel, formatString)
	
	def _process(self, ds, dsxaxis, dsyaxis):
		dsysize, dsxsize = ds.dimensions;
		
		ds00=max( 0.00001, float(ds[0,0]) );
		ds01=max( 0.00001, float(ds[0,1]) );
		ds10=max( 0.00001, float(ds[1,0]) );
		ds11=max( 0.00001, float(ds[1,1]) );

		
		v0 = ds00/ds01;
		v1 = ds10/ds11;
		val = (v0-v1)/(v0+v1);
		
		return (val, v0, v1);


#Usage:
#from Diamond.PseudoDevices.FlippingDevice import FlippingDeviceClass, Algorism01Processor;

#scannerName = "testMotor1";
#flipperName = "testMotor2";
#detectorNames = ["dummyCounter", "dummyCounter1"]
#integrationTime = 0.5
#f1 = FlippingDeviceClass('f1', scannerName, flipperName, [-20, 20], detectorNames, integrationTime, [Algorism01Processor()]);

#f2 = FlippingDeviceClass('f2', scannerName, flipperName, [-20, 20], detectorNames, integrationTime, [Algorism01Processor()]);
#f2.setScanner("testMotor2");
#f2.setFlipper("testMotor1", [-5,0,1.2,3.3,5.1, 5]);
#f2.setDetectors(['dummyCounter','dummyCounter1', 'dummyCounter2'], integrationTime=0.1);

#scan f1 0 10 0.5
#scan f2 0 100, 5

