import zipfile;
import re;
import cPickle as pickle

class ImageProducer(object):
	def __init__(self):
		#zfilename = "/home/xr56/Dev/users/data/demoImages/pilatus/images100K.zip";
		self.zfilename = "images2M.zip";
			
		# open the zipped file
		self.zfile = zipfile.ZipFile( self.zfilename, "r" );
		self.infolist=self.zfile.infolist();

		self.pointer = 0;

		self.pickleFileName='/tmp/simPilatusFileNumber.txt';
		self.fileNumber = 0;

		self.filePath = '/tmp/';
		self.filePrefix = 'test_';
		self.fileNumber = 0;
	
	
	def myComp (x,y):
		def getNum(str):
			num = float(re.findall(r'\d+',str)[0]);
			print num;
			return num;
		return cmp(getNum(x),getNum(y));

	def getNextImage(self):
		while True:
			fullname=self.infolist[self.pointer].filename;
			if fullname.endswith('.tif'): #Now a valid tif file, maybe a folder name
				break;
			self.adjustPointer();

		data = self.zfile.read(fullname);
		self.adjustPointer();

		fname=fullname.split('/')[-1];

		# save the decompressed data to a new file

		self.updateFileNumber();
		#filename = 'test_' + str(self.updateFileNumber());
		filename = self.filePath + self.filePrefix + "%04.0f" % (self.fileNumber) + '.tif';
		
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


a=ImageProducer();

#a.printList();
for i in range(5):
	print a.getNextImage();
