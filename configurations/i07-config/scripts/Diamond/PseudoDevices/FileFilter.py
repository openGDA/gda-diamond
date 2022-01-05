from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

from java.io import File;

import os
from time import sleep;

from gda.jython import InterfaceProvider

from gda.data import NumTracker

from gda.analysis.io import SRSLoader

from gda.analysis import ScanFileHolder

import scisoftpy as dnp
from org.eclipse.january.dataset import Dataset

#####################################################################################

class SrsFileFilterClass(object):
	def __init__(self, indexAxisName, low, high):
		
		self.indexAxisName = indexAxisName;
		self.indexAxis = None;
		self.low = low;
		self.high = high;
		
		self.fileName=None;
###		self.dataholder=ScanFileHolder();
		self.dataholder=None;
		self.targetData=ScanFileHolder();
		self.srsHeader=[];
#		srsHeader=[" &---> SRS\n", " SRSRUN=null,SRSDAT=null,SRSTIM=null,\n", " SRSSTN='null',SRSPRJ='null    ',SRSEXP='null    ',\n", " SRSTLE='                                                            ',\n", " SRSCN1='        ',SRSCN2='        ',SRSCN3='        ',\n", " &---> END\n"];
	
	def setFilter(self, indexAxisName, low, high):
		self.indexAxisName = indexAxisName;
		self.indexAxis = None;
		self.low = low;
		self.high = high;
		
	def loadFile(self, fileName=None):
		if fileName is None:
			fileName = self.getSrsFileName();#To get the current scan data file
		self.fileName = fileName;
###		self.dataholder.loadSRS(self.fileName);
		self.dataholder=dnp.io.load(self.fileName, formats=['srs']);
		
###		self.indexAxis = self.dataholder.getAxis(self.indexAxisName);
		self.indexAxis = self.dataholder[self.indexAxisName];
		
		self.getSrsHeader();
		
	def applyFilter(self):	
		indices = self.getIndices(self.indexAxis, self.low, self.high);
		self.trim(indices);
#		self.saveFile("/dls_sw/i07/software/gda_versions/gdaDev/gda-config/i06/users/data/2010/cm1907-1/aaa.dat");
#		self.saveFile();
		
		
	def saveFile(self, fileName=None):
		if fileName is None:
			fileName = self.fileName;
		
		if os.path.exists(fileName):#The output file exist, better to make a backup	
			os.system("cp " + fileName + " " + fileName + ".bak");
#			os.system("mv " + fileName + " " + fileName + ".bak");
			sleep(0.1);

		self.targetData.save(SRSLoader(fileName));
		self.addSrsHeader();

	def saveNewFile(self, fileName=None):
		if fileName is None:
			newSN=self.incScanNumber();
			fileName = self.getSrsFileName(newSN);#To get the new scan data file name
		
		if os.path.exists(fileName):#The output file exist, better to make a backup	
			os.system("cp " + fileName + " " + fileName + ".bak");
#			os.system("mv " + fileName + " " + fileName + ".bak");
			sleep(0.1);

		self.targetData.save(SRSLoader(fileName));
		self.addSrsHeader();
		print "New Scan data file: %s" %fileName;

	def getSrsHeader(self, fileName=None):
		if fileName is None:
			fileName = self.fileName;

		inFile=None;
		self.srsHeader=[];
		try:
			inFile=open(fileName);

			insideHeader=False;
			for line in inFile:
				if line.strip().startswith("&SRS"):#First time to reach the header area
					self.srsHeader.append(line);
					insideHeader=True;
					continue;
				if line.strip().startswith("&END"):
					self.srsHeader.append(line);
					insideHeader=False;
					break;
				if insideHeader:
					self.srsHeader.append(line);
					continue;
		except:
			print "ERROR: Could not get header from file."

		if inFile: inFile.close();

		
	def addSrsHeader(self, fileName=None):
		if fileName is None:
			fileName = self.fileName;
		
		tempFileName = fileName + ".in"
		if os.path.exists(fileName):#The output file exist, rename it	
			os.system("mv -f " + fileName + " " + tempFileName);
			sleep(0.1);

		inFile=None;
		outFile=None;
		try:
			inFile=open(tempFileName);
			outFile=open(fileName, 'w');

			insideHeader=False;
			for line in inFile:
				if line.strip().startswith("&SRS"):#First time to reach the header area
					insideHeader=True;
					for hl in self.srsHeader:
						outFile.write(hl);
					continue;
				if line.strip().startswith("&END"):
					insideHeader=False;
					continue;
				if not insideHeader:
					outFile.write(line);
				
			outFile.flush();
		except:
			print "ERROR: Could not save header into file."

		if inFile: inFile.close();
		if outFile: outFile.close();
		if os.path.exists(tempFileName):#The output file exist, rename it	
			os.system("rm -f " + tempFileName);

#TODO - Is this the reason why zacscan is failing?
#This one actually do nothing due to changes on the scisoft again. --10130916
	def trim(self, indices):
		for (axisName, ds) in self.dataholder.items():
			if isinstance(ds, Dataset) or isinstance(ds, dnp.jython.jycore.ndarray):
				tds=ds.take(indices, 0);
				if isinstance(ds, Dataset):
					logger.logger.debug("FileFilter:trim:%r(%r): Adding %r" % (axisName, ds.getName(), len(indices)))
					self.targetData.setAxis( ds.getName(), tds); # Why ds.getName() not axisName?
				else:
					logger.logger.debug("FileFilter:trim:%r: Adding %r from %r (%r): %r" % (axisName, len(indices), tds.__class__, tds._jdataset().__class__, tds))
					self.targetData.setAxis( axisName, tds._jdataset()); # ndarray has no ds.getName()
					# and setAxis needs the java dataset from inside the ndarray, not the ndarray
			else:
				logger.logger.debug("FileFilter:trim:%r: Is not a Dataset or ndarray: %r (%r)" % (axisName, ds, ds.__class__))

	def trimOld(self, indices):
		for i in range( self.dataholder.getNumberOfAxis() ):
			ds=self.dataholder.getAxis(i);
#			tds=ds.take(indices, None); #works fine on 8.10, but not for 8.18
			self.targetData.setAxis( ds.getName(), tds);
		

	def getIndices(self, ds, low, high):
		indices=[];
		logger.logger.debug("FileFilter:getIndices... ds.size=%r" % ds.size)
#		for i in range( ds.getSize() ):
#			cvalue = ds.getDouble([i]);
#			if  cvalue >= low and cvalue <= high:
#				indices.extend([i]);
		for i in range( ds.size ):
			if  ds[i] >= low and ds[i] <= high:
				indices.extend([i]);
		logger.logger.debug("FileFilter:getIndices: return indices=%r" % len(indices))

		return indices;
				

	def	getSrsFileName(self, scanNumber = None):
		if scanNumber is None:
			sn = self.getScanNumber()
		else:
			sn = scanNumber;
		srsPath = InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir");
		srsFileName = srsPath + File.separator + str(sn) + ".dat";
		
		return srsFileName;

	def getScanNumber(self):
		nt = NumTracker("tmp")
		scanNumber = nt.getCurrentFileNumber();
		del nt;
		return scanNumber
	
	def incScanNumber(self):
		nt = NumTracker("tmp")
		#increase the scan number for one
#		scanNumber = nt.getCurrentFileNumber();
		scanNumber=nt.incrementNumber();
		return scanNumber


#Example:
sff= SrsFileFilterClass("testMotor2", 15, 23);
#sff.setFilter("testMotor2", 15, 23);
#sff.loadFile();
#sff.applyFilter();
#sff.saveFile();
