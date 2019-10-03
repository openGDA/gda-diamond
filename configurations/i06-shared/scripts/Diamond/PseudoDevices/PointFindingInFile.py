from java.io import File;

from gda.configuration.properties import LocalProperties;
from gda.device.scannable import ScannableBase
from gda.data import NumTracker
from gda.jython import InterfaceProvider

from org.eclipse.january.dataset import DatasetUtils

import scisoftpy as dnp;

#####################################################################################
#def getScanNumber():
#	nt = NumTracker("tmp")
#	scanNumber = nt.getCurrentFileNumber();
#	del nt;
#	return scanNumber
#
#def	getSrsFileName(scanNumber=None, srsPath=None):
#	if scanNumber is None:
#		sn = getScanNumber()
#	else:
#		sn = scanNumber;
#	if srsPath is None:
#		srsPath = InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir");
#		
#	srsFileName = srsPath + File.separator + str(sn) + ".dat";

#	print "srs file name is: " + srsFileName;
#	return srsFileName;


#####################################################################################
class PointFindingInFileClass(ScannableBase):
#	def __init__(self, name, strUnit, strFormat):
	def __init__(self, name, xAxisName, yAxisName, extraAxisNameList=[], metaAxisNameList=[]):
		self.setName(name);
		self.setInputNames(["scanNumber"]);
		
		self.srsPath=None;
		
		self.xAxis = xAxisName;
		self.yAxis = yAxisName;
		self.extraAxis=extraAxisNameList;
		self.metaAxis=metaAxisNameList;
		
		self.setNewOutputFormat();
		
#		self.dataHolder=ScanFileHolder();
		self.dataHolder=None;
		self.index=long(NumTracker("tmp").getCurrentFileNumber());
		self.yMax=None;
		self.pos=None;
		self.xVal=None;
		self.centroid=None;
		self.extraValues=[];

	def setNewOutputFormat(self):
#		self.setExtraNames(["pos", "xVal", "yMax", "centroid"] + self.extraAxis);
		self.setExtraNames(["index", self.xAxis, self.yAxis, "centroid"] + self.extraAxis + self.metaAxis);
		
		outputFormat=["%6.0f","%10.0f","%20.12f","%20.12f","%20.12f"]
		for i in range(0, len(self.extraAxis + self.metaAxis)):
			outputFormat.append("%20.12f");
		self.setOutputFormat(outputFormat);
		
		#self.setOutputFormat(['%6.2f'])
		#self.setLevel(7);
		
	def setPath(self, srsFilePath):
		self.srsPath=srsFilePath;
		
		
	def setXY(self, xAxisName, yAxisName):
		self.setXYs(xAxisName, yAxisName, []);
		
	def setXYs(self, xAxisName, yAxisName, extraAxisNameList=[], metaAxisNameList=[]):
		self.xAxis=xAxisName;
		self.yAxis=yAxisName;
		self.extraAxis=extraAxisNameList;
		self.metaAxis=metaAxisNameList;
		self.setNewOutputFormat();

	def setMetaYs(self, metaAxisNameList=[]):
		self.metaAxis=metaAxisNameList;
		self.setNewOutputFormat();

	def	getSrsFileName(self, scanNumber=None, srsPath=None):
		if scanNumber is None:
			nt = NumTracker("tmp")
			sn = nt.getCurrentFileNumber();
		else:
			sn = scanNumber;
			
		if srsPath is None:
			srsPath = InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir");
			
		srsFileName = srsPath + File.separator + str(sn) + ".dat";
		
#		print "srs file name is: " + srsFileName;
		return srsFileName;

	def getPosition(self):
		fileName = self.getSrsFileName(self.index, self.srsPath);
		self.dataHolder=dnp.io.load(fileName, formats=['srs']);
		
		self.yMax=self.dataHolder[self.yAxis].max();
		
		newformatpos=self.dataHolder[self.yAxis].maxPos();
		self.pos=newformatpos[0];

		self.xVal=self.dataHolder[self.xAxis][self.pos];
		
#		self.centroid=self.dataHolder.centroid(self.dataHolder.getAxis(self.xAxis), self.dataHolder.getAxis(self.yAxis));
		self.centroid=DatasetUtils.centroid(self.dataHolder[self.yAxis], [ self.dataHolder[self.xAxis] ])[0];

		rtnList=[self.index, int(self.pos), self.xVal, self.yMax, self.centroid]
		self.extraValues=[];

		for axis in self.extraAxis:
			self.extraValues.append( self.dataHolder[axis][int(self.pos)] );
			
		for axis in self.metaAxis:
			if axis in self.dataHolder.metadata.keys():
				self.extraValues.append( self.dataHolder.metadata[axis] );
			else:
				self.extraValues.append( None );
			
		return rtnList+self.extraValues;

	def asynchronousMoveTo(self, new_position):
		self.index = int(new_position);

	def isBusy(self):
		return 0;

	def toString(self):
		self.getPosition();
		ss=self.getName() + ": "+str(self.index)+ ", " + str(int(self.pos)) + ", " + str(self.xVal) + ", " + str(self.yMax) + ", " + str(self.centroid);
		for i in range(0,len(self.extraAxis)):
			ss+=", "+ str(self.extraValues[i]);
		return ss;

#Example:
#scan testMotor1 0 10 1 dummyCounter 0.1 dummyCounter2 0.1
#...
#...
#scan testMotor1 0 10 1 dummyCounter 0.1 dummyCounter2 0.1


#import Diamond.PseudoDevices.PointFindingInFile; reload(Diamond.PseudoDevices.PointFindingInFile)
#from Diamond.PseudoDevices.PointFindingInFile import PointFindingInFileClass

#del pfif
#pfif=PointFindingInFileClass('pfif', 'testMotor1','dummyCounter', ['dummyCounter2'], ['s1ygap', 'iddgap'])

#pfif.setPath("/dls_sw/i07/software/gda_versions/gdaDev/gda_trunk/i07-config/scripts/tests/data")
#scan pfif (14, 15, 16)

#pfif= PointFindingInFileClass('pfif', 'testMotor1','dummyCounter', ['dummyCounter2']);
#pfif= PointFindingInFileClass("pfif", "pgmenergy","ca31sr", []);
#pfe= PointFindingInFileClass("pfe", "pgmenergy","ca31sr", ["iddgap",  "iddtrp"]);


