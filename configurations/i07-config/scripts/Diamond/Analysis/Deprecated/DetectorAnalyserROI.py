from gda.analysis import RCPPlotter;

from uk.ac.diamond.scisoft.analysis.plotserver import GuiBean;
from uk.ac.diamond.scisoft.analysis.plotserver import GuiParameters;
from uk.ac.diamond.scisoft.analysis.plotserver import GuiPlotMode;

from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI, RectangularROIList;

from Diamond.Analysis.DetectorAnalyser import DetectorAnalyserClass;

#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

class DetectorAnalyserWithRectangularROIClass(DetectorAnalyserClass):
	
	def __init__(self, name, detector, processors=[], panelName="Area Detector", iFileLoader=None):

		DetectorAnalyserClass.__init__(self, name, detector, processors, panelName, iFileLoader);
#		super(DetectorAnalyserClass, self).__init__(name, detector, processors, panel_name, iFileLoader);
		self.extraNames = ['file'];
		self.outputFormat = ['%f','%s'];
		
		self.roiList = None;

	def setScannableFormat(self, numberOfROIs):
		self.extraNames = ['file'];
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
		guibean=GuiBean();
		guibean[GuiParameters.ROIDATA]=plotmode;
		RCPPlotter.setGuiBean(self.panel, guibean);
		
	def clearRoi(self):
		roi = RectangularROI();
		roiList = RectangularROIList();

		guibean=GuiBean();
		guibean[GuiParameters.ROIDATA]=roi;
		guibean[GuiParameters.ROIDATALIST] = roiList;
		
		RCPPlotter.setGuiBean(self.panel, guibean);
		
		self.updateRoiList();
		
	def addRoi(self, x=None, y=None, width=None, height=None, angle=0):
		#To get the current GUI situation
		guibean=RCPPlotter.getGuiBean(self.panel);
		#roi=gbean.get(GuiParameters.ROIDATA)
		roi=guibean[GuiParameters.ROIDATA];
		roiList=guibean[GuiParameters.ROIDATALIST];
		
		if None in [x, y, width, height, angle]:#No ROI parameter defined.
			print "No ROI info defined in the command. Use GUI ROI box selection"
			if roi is None: # No ROI selection on the gui
				print "Can not add ROI. Please either give ROI five parameters or draw a box in the GUI";
				return;
		else:
			roi = RectangularROI(x,y, width, height, angle);

		if roiList is None:#No ROI Table on the gui
			roiList = RectangularROIList();

		roiList.add(roi);
		
		#Update the view with new ROI table
		guibean=GuiBean();
		guibean[GuiParameters.ROIDATALIST] = roiList;
		RCPPlotter.setGuiBean(self.panel, guibean);

		self.getRoiTable();
		
	def updateRoiList(self):
		guibean=RCPPlotter.getGuiBean(self.panel);
		roiList=guibean[GuiParameters.ROIDATALIST];

		if isinstance(roiList, RectangularROIList):
			self.roiList = roiList;
			
		if self.roiList is None:
			raise RuntimeError("No ROI Defined Error");

	def getRoiTable(self):
		self.updateRoiList();
		for roi in self.roiList:
			print self.getRoiParameters(roi);


	def getRoiSelectionBox(self):
		#Get current ROI info from the View
		guibean=RCPPlotter.getGuiBean(self.panel);
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
		roiDataset = ds[y:y+h, x:x+w];
		
		return roiDataset;

	def atScanStart(self):
		
		self.updateRoiList();
		self.setScannableFormat(len(self.roiList));
	
	def getPosition(self):
		self.loadDataset();

		#Get the ROI info from GUI
		self.updateRoiList();

		self.setScannableFormat(len(self.roiList));
		
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

#from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor;
#from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
#from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
#from gda.analysis.io import PilatusTiffLoader

#ppr = DetectorAnalyserWithRectangularROIClass("ppr", pil1, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
#ppr.setAlive(True);
#ppr.setPassive(False);
#ppr.addRoi(240, 100, 100, 50);
