import os;

from java.lang import IllegalArgumentException;
from java.util import ArrayList;

#from gda.device.scannable import ScannableMotionBase;
#from gda.device.detector import DetectorBase
#from gda.device import Detector;
from gda.device.detector import DetectorBase
from gda.device.detector import NXDetectorDataWithFilepathForSrs
#
from gda.analysis.io import JPEGLoader, TIFFImageLoader, PNGLoader

from org.eclipse.january.dataset import Dataset
from uk.ac.diamond.scisoft.analysis.dataset.function import MakeMask

import scisoftpy as dnp;

from uk.ac.diamond.scisoft.analysis import SDAPlotter
from uk.ac.diamond.scisoft.analysis.plotserver import GuiParameters;
from uk.ac.diamond.scisoft.analysis.plotserver import GuiPlotMode;
#from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI, ROIList;
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI, RectangularROIList;

from Diamond.Utility.ScriptLogger import ScriptLoggerClass;

logger=ScriptLoggerClass();


ImageFileLoaders={
			'TIF' : TIFFImageLoader,
			'TIFF': TIFFImageLoader,
			'JPG' : JPEGLoader,
			'JPEG': JPEGLoader,
			'PNG' : PNGLoader
			}

class AnalyserDetectorClass(DetectorBase):

	def __init__(self, name, detector, processors=[], panelName="Area Detector", iFileLoader=None):
		self.detector = detector;
		self.processors = processors;
		self.panel = panelName;
		self.iFileLoader = iFileLoader;
		
		self.filename= None;
		self.dataholder = None;
		self.dataset = None;
		self.mask = None;
		self.result = None;

		self.alive = False;
		
		self.scannableSetup(name);

	def scannableSetup(self, name):
		self.setName(name);
		self.setInputNames([]);

		extraNames = ['ExposureTime', 'file'];
#		extraNames = ['file'];
#		extraNames = [];
		outputFormat = ['%f','%s'];
		if self.processors != None:
			for processor in self.processors:
				for label in processor.labelList:
					extraNames.append(self.name + '_' + label)
					outputFormat.append( '%f' );

#		self.extraNames = extraNames;
#		self.outputFormat = outputFormat;
		self.setExtraNames(extraNames);
		self.setOutputFormat(outputFormat);

		self.level = self.detector.getLevel()

	def setAlive(self, newAlive=True):
		self.alive = newAlive;
			
	def loadDataFromFile(self, fileName, fileLoader=None):
		if fileLoader is None:
			fileLoader = ImageFileLoaders[os.path.splitext(fileName)[-1].split('.')[-1].upper()];
			
		try:
			self.dataholder=dnp.io.load(fileName);
		except IllegalArgumentException:
			raise ValueError("Oh Dear. How to load this image file?");

		return self.dataholder;

	def detectorReadout(self):
		return self.detector.readout()

	def loadDataset(self, fileName = None, fileLoader = None):
		self.dataset = None;
		if fileLoader == None:
			fileLoader = self.iFileLoader;
		
		if fileName != None:#Get data from file directly
			self.dataholder = self.loadDataFromFile(fileName, fileLoader);
			if self.dataholder is not None:
				self.filename = fileName;
				self.dataset = self.dataholder[0];
		else: #Get data from detector
			if self.detector.createsOwnFiles():
				nxDetectorReturn=self.detectorReadout();
				
				if isinstance(nxDetectorReturn, NXDetectorDataWithFilepathForSrs):
					fn=nxDetectorReturn.getFilepath();
				else:
					fn=str(nxDetectorReturn);
				self.dataholder = self.loadDataFromFile(fn, fileLoader);
				if self.dataholder is not None:
					self.filename = fn;
					self.dataset = self.dataholder[0]._jdataset();  # Pete's recent change has caused this to return ndarray
			else:
				self.filename = None;
				ds = self.detectorReadout();
				if isinstance(ds, Dataset):
					self.dataset = ds;
				elif isinstance(ds, NXDetectorDataWithFilepathForSrs):
					self.filename = ds.getFilepath()
					self.dataholder = self.loadDataFromFile(self.filename, fileLoader);
					self.dataset = self.dataholder[0]._jdataset();  # Pete's recent change has caused this to return ndarray

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
				
		maskArray = dnp.logical_and(dnp.array(dataset)>=low, dnp.array(dataset)<=high);
		self.mask = maskArray._jdataset()
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
#				print "No mask provided, please create new mask";
				return dataset;
			else:
				mask = self.mask;
		
		#maskedDataet = dataset * mask
		maskedDataset = dataset.imultiply(mask)
#		if self.alive:
#			self.display(maskedDataet);
		return maskedDataset

	def display(self, dataset=None):
		if dataset is None:
			if self.dataset is None:
				print "No dataset to display";
				return;
			else:
				dataset = self.dataset;
				
		if self.panel:
			SDAPlotter.imagePlot(self.panel, dataset);
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name,self.name));
	

###	DetectorBase implementations:
	def createsOwnFiles(self):
		return False;

	def getCollectionTime(self):
		return self.detector.getCollectionTime();

	def setCollectionTime(self, newExpos):
		self.detector.setCollectionTime(newExpos);

	def prepareForCollection(self):
#	def atScanStart(self):
		self.detector.prepareForCollection();
	
	def atScanStart(self):
		self.detector.atScanStart()

	def atScanLineStart(self):
		self.detector.atScanLineStart()

	def atScanEnd(self):
		self.detector.atScanEnd()

	def collectData(self):
		self.dataset = None;
		self.result = None;
		self.detector.collectData();

	def readout(self):
		self.loadDataset();

		result = [self.detector.getCollectionTime(), self.filename];
		if self.processors != None:
			for processor in self.processors:
				result += list(self.getResult(processor, self.dataset));

		self.setResult(result);

		if self.alive:
			self.display();
		
		return result;

	def endCollection(self):
		self.detector.endCollection();

	def getStatus(self):
		return self.detector.getStatus();

	def stop(self):
		self.detector.stop();

	def atCommandFailure(self):
		self.detector.atCommandFailure();

	def getDescription(self):
		return "An Detector based analyser";

	def getDetectorID(self):
		return "dumbdumb-1";

	def getDetectorType(self):
		return "AnalyserDetectorClass";


##########################################


class AnalyserWithRectangularROIClass(AnalyserDetectorClass):
	
	def __init__(self, name, detector, processors=[], panelName="Area Detector", iFileLoader=None):

		AnalyserDetectorClass.__init__(self, name, detector, processors, panelName, iFileLoader);

		self.setScannableFormat(0);
		self.roiList = [];

	def setScannableFormat(self, numberOfROIs):
		
		self.setInputNames([]);
		self.extraNames = ['ExposureTime', 'file'];
		self.outputFormat = ['%f','%s'];
		i=0;
		for i in range(numberOfROIs):
			self.addRoiScannableSetup(i+1);
		
	def addRoiScannableSetup(self, index):
		roiName='roi'+str(index);
		exNames = list( self.getExtraNames() );
		oFormat = list( self.getOutputFormat() );
		exNames.extend([roiName+'_X', roiName+'_Y', roiName+'_Width', roiName+'_Height', roiName+'_Angle']);
		oFormat.extend(['%f', '%f', '%f', '%f', '%f']);
		if self.processors is not None:
			for processor in self.processors:
				for label in processor.labelList:
					exNames.append(roiName + '_' + label)
					oFormat.append( '%f' );
		self.extraNames = exNames;
		self.outputFormat = oFormat;

	def setPlotMode(self, plotmode=GuiPlotMode.TWOD):
#		guibean=GuiBean();
		guibean=SDAPlotter.getGuiBean(self.panel);
		guibean[GuiParameters.PLOTMODE]=plotmode;
		SDAPlotter.setGuiBean(self.panel, guibean);

	def clearRois(self):
		guibean=SDAPlotter.getGuiBean(self.panel);

		if GuiParameters.ROIDATALIST in guibean:
			#guibean[GuiParameters.ROIDATALIST]=None;
			guibean.clear()
			
		SDAPlotter.setGuiBean(self.panel, guibean);
		
		self.roiList = [];
		self.updateRoiList();
		
	def addRoi(self, x=None, y=None, width=None, height=None, angle=0):
		#To get the current GUI situation
		guibean=SDAPlotter.getGuiBean(self.panel);
		#roi=gbean.get(GuiParameters.ROIDATA)
		roi=guibean[GuiParameters.ROIDATA];
		roiList=guibean[GuiParameters.ROIDATALIST];
		
		if None in [x, y, width, height, angle]:#No ROI parameter defined.
			print "Not enough ROI info defined in the command. Use GUI ROI box selection"
			if roi is None: # No ROI selection on the gui
				print "Can not add ROI. Please either give ROI five parameters or draw a box in the GUI";
				return;
		else:
			roi = RectangularROI(x,y, width, height, angle);

		if roiList is None:#No ROI Table on the gui
			roiList = RectangularROIList();

		roiList.add(roi);
		
		#Update the view with new ROI table
#		guibean=GuiBean();
		guibean[GuiParameters.ROIDATALIST] = roiList;
		SDAPlotter.setGuiBean(self.panel, guibean);

		self.getRoiTable();
		
	#To change the shape a ROI that marked by index 
	def modifyRoi(self, index, x, y, width, height, angle=0):
		table=self.getRoiTable();#to get the current roi information
		if len(table)==0:#The current roiList is empty, add new one
			self.addRoi(x, y, width, height, angle);
			return;
		
		table[index]=[x, y, width, height, angle]; # to replace the one
		
		self.clearRois() #To remove all old rois
		for ri in table:
			self.addRoi(ri[0],ri[1],ri[2],ri[3],ri[4]);
	
		
	def updateRoiList(self):
		guibean=SDAPlotter.getGuiBean(self.panel);
		
		roiList=guibean[GuiParameters.ROIDATALIST];
		tempRoiList=[];

		if not isinstance(roiList, RectangularROIList):#No rectangular roi list defined.
			return
		else:
			for roi in roiList:
				if isinstance(roi, RectangularROI):
					tempRoiList.append(roi);

		tempRoiList.sort(key = lambda roi: roi.name)
		self.roiList = tempRoiList;

	def getRoiTable(self):
		self.updateRoiList();
		table=[];

		for roi in self.roiList:
			r=self.getRoiParameters(roi)
			table.append( r );
		return table;


	def getRoiSelectionBox(self):
		#Get current ROI info from the View
		guibean=SDAPlotter.getGuiBean(self.panel);
		#roi=gbean.get(GuiParameters.ROIDATA)
		roi=guibean[GuiParameters.ROIDATA];
		if roi is None:
			print None;
		else:
			print self.getRoiParameters(roi);
		return roi;

	def getRoiParameters(self, roi):
		x, y = roi.getIntPoint();
		w, h = roi.getIntLengths();
		angle = roi.getAngleDegrees();

		return [x,y,w,h,angle];

	def getRoiDataset(self, roi, ds=None):
		if ds is None:
			ds = self.dataset;
#			print 'Debug--> use dataset as default dataset'
			
		[x,y,w,h,angle]=self.getRoiParameters(roi);
		roiDataset = dnp.array(ds)[y:y+h, x:x+w];
		
		return roiDataset;

	def collectData(self):
		self.dataset = None;
		self.result = None;
		self.detector.collectData();

	def prepareForCollection(self):
#	def atScanStart(self):
		AnalyserDetectorClass.prepareForCollection(self);
		self.updateRoiList();
		self.setScannableFormat(len(self.roiList));

	def asynchronousMoveTo(self, collectionTime):
		self.setCollectionTime(collectionTime);
		self.prepareForCollection()
		self.collectData();
		
	def readout(self):
		self.loadDataset();

		#Get the ROI info from GUI
#		self.updateRoiList();
#		self.setScannableFormat(len(self.roiList));
		
		result = [self.detector.getCollectionTime(), self.filename];
		for roi in self.roiList:
			[x,y,w,h,angle]=self.getRoiParameters(roi);
			roiDataset = self.getRoiDataset(roi);
			
			result += [x, y, w, h, angle];
			
			if self.processors != None:
				for processor in self.processors:
					result += list(self.getResult(processor, roiDataset));
	
			self.setResult(result);

		if self.alive:
			self.display();
		
		return result;



##########################################
#Usage:
#from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
#from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
#from gda.analysis.io import PilatusTiffLoader

#from Diamond.Analysis.Analyser import AnalyserDetectorClass;
#from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;
#from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor;


#pil1stats = AnalyserDetectorClass("pil1stats", pil1, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
#pil1stats.setAlive(True);

#pil1roi = AnalyserWithRectangularROIClass("pil1roi", pil1, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
#pil1roi.setAlive(True);
#pil1roi.addRoi(240, 100, 100, 50);
