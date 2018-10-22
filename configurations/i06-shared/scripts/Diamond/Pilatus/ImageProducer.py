import zipfile;
import re;
import os;
import cPickle as pickle;

import Diamond.Pilatus.PilatusInfo;
from PilatusInfo import PilatusInfo;
#from Diamond.Pilatus import PilatusInfo;

class ImageProducerClass(object):

	def __init__(self, type):
		modulePath = os.path.dirname(Diamond.Pilatus.PilatusInfo.__file__);
		if type == PilatusInfo.PILATUS_MODEL_100K:
			self.zfilename  = modulePath + "/images100K.zip";
			
		elif type == Pilatus.PILATUS_MODEL_2M:
			self.zfilename = modulePath + "images2M.zip";
		else:
			print "Unknown Pilatus type, use default Pilatus 100K";
			self.zfilename  = modulePath + "images100K.zip";
			
		# open the zipped file
		self.zfile = zipfile.ZipFile( self.zfilename, "r" );
		self.infolist=self.zfile.infolist();

		self.pointer = 0;

		self.pickleFileName='/tmp/simPilatusFileNumber.txt';
		self.fileNumber = 0;

		self.filePath = '/tmp/';
		self.filePrefix = 'psim_';
		self.fileNumber = 0;
	
	def setFilePath(self, newFilePath):
		"""Set file path"""
		self.filePath = newFilePath
		self.getFileNumber();
		print "Image file path set to " + newFilePath;
		
	def getFilePath(self):
		return self.filePath;
	
	def setFilePrefix(self, filePrefix):
		"""Set filename - not the path"""
		self.filePrefix = filePrefix

	def getNextImage(self, newFileName=None):
		while True:
			fullname=self.infolist[self.pointer].filename;
			if fullname.endswith('.tif'): #Now a valid tif file, maybe a folder name
				break;
			self.adjustPointer();

		data = self.zfile.read(fullname);
		self.adjustPointer();

		fname=fullname.split('/')[-1];

		# save the decompressed data to a new file
		if newFileName == None: # No file name is given, create one based on file number
			self.updateFileNumber();
			#filename = 'test_' + str(self.updateFileNumber());
			filename = self.filePath + self.filePrefix + "%04.0f" % (self.fileNumber) + '.tif';
		elif newFileName == newFileName.split('/')[-1] : # only a file name is given without the path, use the system file path
			filename = self.filePath + newFileName;
		else:#A full file name with path is given, just use it
			filename = newFileName;
		
		fout = open(filename, "w")
		fout.write(data)
		fout.close()
		return filename;

	def adjustPointer(self):
		self.pointer+=1;
		if self.pointer >= len(self.infolist):
			self.pointer = 0;

	def printList(self):
		# retrieve information about the zip file
		self.zfile.printdir();
		print '-'*40;
		
	def updateFileNumber(self):
		"""Restore the pickled file number for persistence"""
		self.fileNumber = self.getFileNumber();
		self.fileNumber += 1;
		self.saveFileNumber();
		return self.fileNumber;
			
	def getFileNumber(self):
		"""Restore the pickled file number for persistence"""
		try:
			inStream = file(self.pickleFileName, 'rb');
			self.fileNumber = pickle.load(inStream);
			inStream.close();
		except IOError:
			print "No previous pickled file numbers. Create new one";
			self.fileNumber = 0;
		return self.fileNumber;

	def saveFileNumber(self):
		"""Save the file number for persistence"""
		outStream = file(self.pickleFileName, 'wb');
		try:
			#Pickle the file number and dump to a file stream
			pickle.dump(self.fileNumber, outStream);
			outStream.close();
		except IOError:
			print "Can not preserve file numbers.";


#a=ImageProducerClass();

#a.printList();
#for i in range(5):
#	print a.getNextImage();
