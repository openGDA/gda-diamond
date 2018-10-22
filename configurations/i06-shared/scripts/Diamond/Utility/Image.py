
from gda.analysis.io import JPEGLoader, TIFFImageLoader

from gda.analysis import ScanFileHolder

from uk.ac.diamond.scisoft.analysis import SDAPlotter 

#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

GDA_FILELOADERS={
			'TIF':TIFFImageLoader,
			'TIFF':TIFFImageLoader,
			'JPG':JPEGLoader,
			'JPEG':JPEGLoader,
			}

class ImageUtility(object):
	def __init__(self, panelName="Data Vector", iFileLoader=None):
		self.panel = panelName;
		self.iFileLoader = iFileLoader;
		
		self.filename= None;
		self.data = ScanFileHolder();
		self.dataset = None;


	def loadDataFromFile(self, fileName, fileLoader):
		if fileLoader is None:
			import os
			fileLoader = GDA_FILELOADERS[os.path.splitext(fileName)[-1].upper()];

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
		else: 
			print "Please give a full file name"
			return;

		return self.dataset;
			
	def loadFile(self, fileName = None, fileLoader = None):
		return self.loadDataset(fileName, fileLoader);

	def open(self, fileName):
		self.display(fileName);
		
	def display(self, fileName):
		if fileName is None:
			print "Please give a full file name to display";
			return;
		else:
			dataset = self.loadDataset(fileName)
				
		if self.panel:
			SDAPlotter.imagePlot(self.panel, dataset);
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name,self.name));



