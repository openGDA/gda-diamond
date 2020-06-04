
from gda.device.scannable import ScannableMotionBase;
from gda.device import Detector;

from gda.analysis.io import JPEGLoader, TIFFImageLoader
from gda.analysis import ScanFileHolder
from org.eclipse.january.dataset import Dataset
from uk.ac.diamond.scisoft.analysis.dataset.function import MakeMask;
from gda.analysis import RCPPlotter;

import os;


#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();


GDA_FILELOADERS={
			'TIF':TIFFImageLoader,
			'TIFF':TIFFImageLoader,
			'JPG':JPEGLoader,
			'JPEG':JPEGLoader,
			}

class DetectorAnalyserClass(ScannableMotionBase):

	def __init__(self, name, detector, processors=[], panelName="Area Detector", iFileLoader=None):
		self.detector = detector;
		self.processors = processors;
		self.panel = panelName;
		self.iFileLoader = iFileLoader;
		
		self.filename= None;
		self.data = ScanFileHolder();
		self.dataset = None;
		self.mask = None;
		self.result = None;

		self.passive = False;
		self.alive = False;
		
		self.scannableSetup(name);

	def scannableSetup(self, name):
		self.setName(name);
		self.inputNames = [self.detector.getName() + 'Wrapper_' + name];

		extraNames = ['file'];
		outputFormat = ['%f','%s'];
		if self.processors != None:
			for processor in self.processors:
				for label in processor.labelList:
					extraNames.append(self.name + '_' + label)
					outputFormat.append( '%f' );

		self.extraNames = extraNames;
		self.outputFormat = outputFormat;
		
		self.level = self.detector.getLevel() + 1;

	def setPassive(self, newPassive = True):
		"""
		Set the detector analyser to be Passive or Active
		Device Passive means this analyser will not drive its detector but only works with the latest detector data.
		Device NoPassive/Active means this analyser will drive its detector to get new data and then works with the new acquisition.
		"""
		self.passive = newPassive;

	def setAlive(self, newAlive=True):
		self.alive = newAlive;
			
	def loadDataFromFile(self, fileName, fileLoader):
		if fileLoader is None:
			fileLoader = GDA_FILELOADERS[os.path.splitext(fileName)[-1].upper()];

	#	print "loadIntoSfh loading: %s using %s" % (fileName, str(iFileLoader))
		print fileName
		self.data.load(fileLoader(fileName));

		return self.data;


	def loadDataset(self, fileName = None, fileLoader = None):
		self.dataset = None;
		
		if fileLoader == None:
			fileLoader = self.iFileLoader;
		
		if fileName != None:#Get data from file directly
			self.data = self.loadDataFromFile(fileName, fileLoader);
			if self.data is not None:
				self.filename = fileName;
#				self.dataset = self.data[0];
				self.dataset = self.data.getAxis(0);
		else: #Get data from detector
			if self.detector.createsOwnFiles():
				fn=self.detector.readout();
				self.data = self.loadDataFromFile(fn, fileLoader);
				if self.data is not None:
					self.filename = fn;
#					self.dataset = self.data[0];
					self.dataset = self.data.getAxis(0);
			else:
				self.filename = None;
				ds = self.detector.readout();
				if isinstance(ds, Dataset):
					self.dataset = ds;
				else:
					self.dataset = None;
					raise Exception('For none file generating detector, a DataSet is needed for analysis.');

		#Apply mask if available:
		self.dataset = self.applyMask(self.mask, self.dataset);
		return self.dataset;
			
	def loadFile(self, fileName = None, fileLoader = None):
		return self.loadDataset(fileName, fileLoader);

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

	def getMask(self):
		return self.mask;

	def removeMask(self):
		self.mask = None;
	
	def createMask(self, low, high, dataset=None):
		if dataset is None:
			if self.dataset is None:
				print "No reference dataset to mask";
				return;
			else:
				dataset = self.dataset;
				
		maskMaker=MakeMask(low, high);
#		arrayListDataset = ArrayList(dataset.exec(maskMaker));
#		self.mask=DataSet(arrayListDataset.get(0));

		self.mask = maskMaker.value(dataset).get(0).cast(Dataset.FLOAT64)
		return self.mask;

	def applyMask(self, mask=None, dataset=None):
		if dataset is None:
			if self.dataset is None:
				print "No dataset to mask";
				return;
			else:
				dataset = self.dataset;

		if mask is None:
			if self.mask is None:
				print "No mask provided, please create new mask";
				return dataset;
			else:
				mask = self.mask;
		
		maskedDataet = dataset * mask
#		if self.alive:
#			self.display(maskedDataet);
		return maskedDataet;

	def display(self, dataset=None):
		if dataset is None:
			if self.dataset is None:
				print "No dataset to display";
				return;
			else:
				dataset = self.dataset;
				
		if self.panel:
			RCPPlotter.imagePlot(self.panel, dataset);
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name,self.name));
			

	def rescan(self, scanNumber):
		"""
		To re-do the data analysis based on the data set generated in the previous scan
		Input: scanNumber: the old scan that created a list of data files
		Output: a new SRS data file that re do the data analysis 
		"""
		self.data.loadSRS(scanNumber);
		self.data.info();
		
		#find the file name
		#load dataset from the file
		#do the analysis and get result
		#save into a new srs file
		
	
	def __getitem__(self, key):
		if self.result == None:
			self.getPosition()
		return self.result[key]

###	Psduco Device Interface method implementations:
	def asynchronousMoveTo(self, exposureTime):
		if self.passive:
			print "The Detector Analyser " + self.name + " only works with existing detector data, no new data will be collected."
			return;

		self.dataset = None;
		self.result = None;
		self.detector.asynchronousMoveTo(exposureTime);
#		self.detector.setCollectionTime(t);
#		self.detector.collectData();
		
	def isBusy(self):
		if self.passive:
			return False;
		else:
			return self.detector.getStatus() == Detector.BUSY;
	
	def getPosition(self):
		self.loadDataset();

		result = [self.detector.getCollectionTime(), self.filename];
		if self.processors != None:
			for processor in self.processors:
				result += list(self.getResult(processor, self.dataset));

		self.setResult(result);

		if self.alive:
			self.display();
		
		return result;


##########################################

#from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor;
#from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
#from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
#from gda.analysis.io import PilatusTiffLoader

#pil1stats = DetectorAnalyserClass("pil1stats", pil1, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
#pil1stats.setAlive(True);

