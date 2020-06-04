from gda.device.scannable import ScannableMotionBase
from time import sleep
from gda.analysis.io import TIFFImageLoader
from gda.analysis import Plotter

class AndorCCDClass(ScannableMotionBase):
	'''Andor CCD
	'''

	def __init__(self,name,pvroot,filepath,filenum_pd, display_image=1, process_image=1, logscale=1):
		self.setName(name);
		self.setInputNames(['ExposureTime'])
		self.setExtraNames(['FileNum','max','sum']);
		self.setOutputFormat(['%.2f', '%.0f', '%.0f', '%.0f'])
		self.setLevel(9)
		self.ClientRoot=pvroot
		#self.filename=filename
		#self.default_filename=filename
		self.filepath=filepath
		self.default_filepath=filepath
		self.display_image=display_image
		self.process_image=process_image
		self.logscale = logscale

		self.CAacquire=CAClient(self.ClientRoot+'Acquire'); self.CAacquire.configure()
		self.CAAcquire_RBV=CAClient(self.ClientRoot+'Acquire_RBV'); self.CAAcquire_RBV.configure()
		#self.CANImages=CAClient(self.ClientRoot+'NImages');	self.CANImages.configure()
		#self.CAabort=CAClient(self.ClientRoot+'Abort'); self.CAabort.configure()
		#self.CAExposureTime=CAClient(self.ClientRoot+'ExposureTime'); self.CAExposureTime.configure()
		self.CAExposureTime=CAClient(self.ClientRoot+'AcquireTime'); self.CAExposureTime.configure()
		self.CAFilePath=CAClient(self.ClientRoot+'FilePath'); self.CAFilePath.configure()
		self.CAFilePath_RBV=CAClient(self.ClientRoot+'FilePath_RBV'); self.CAFilePath_RBV.configure()
		#self.CAFileName=CAClient(self.ClientRoot+'Filename'); self.CAFileName.configure()
		#self.CAFileNumber=CAClient(self.ClientRoot+'FileNumber'); self.CAFileNumber.configure()
		#self.CAFileFormat=CAClient(self.ClientRoot+'FileFormat'); self.CAFileFormat.configure()
		#self.CAThresholdEnergy=CAClient(self.ClientRoot+'ThresholdEnergy'); self.CAThresholdEnergy.configure()

		#self.CANImages.caput(1)
		self.CAFilePath.caput(self.filepath)
		#self.CAFileName.caput(self.filename)
		#self.fileformat=self.CAFileFormat.caget()

		#self.data = ScanFileHolder()
		self.exptime=0
		self.sum=0
		self.maxpix=0
		#self.filenum=0
		#self.CAacquire.configure()

		#self.roix1 = None
		#self.roiy1  = None
		#self.roix2 = None
		#self.roiy2  = None

		self.filenum_pd=filenum_pd
		self.filename='';

	def isBusy(self):
		isbusy=float(self.CAAcquire_RBV.caget())
		return float(isbusy)

	def getPosition(self):
		if self.display_image:
			for tries in range(10):
				try:	
					img = TIFFImageLoader(self.filename) # e.g. /dls_sw/i16/andortest1.tiff
#					img = AndorAsciiLoader(self.filename,1024,1024,1)
					hol = img.loadFile()
					data = hol.data
					mydata = data.elementAt(0)
					break 
				except e:
					print e
					print '=== Failed to read back image file '+self.filename+' - trying again'
					sleep(2)


			if self.logscale:
				Plotter.plotImage("Data Vector", mydata.lognorm())
			else:
				Plotter.plotImage("Data Vector", mydata)

			self.maxpix=mydata.max()
			self.sum=mydata.sum()#(self.image.doubleArray())
		else:
			self.sum = -1
			self.maxpix = -1
	
		return [self.exptime, self.filenum_pd(), self.maxpix, self.sum]

	def setNextFileName(self):
		self.filenum_pd(self.filenum_pd()+1);	#increment file number
#		self.filename=self.filepath+str(int(self.filenum_pd()))+'.txt'
		self.filename=self.filepath+str(int(self.filenum_pd()))+'.tif'
		self.filename_bytes=[]
		for letter in self.filename:
			self.filename_bytes.append(ord(letter))
		self.CAFilePath.controller.caputWait(self.CAFilePath.channel,self.filename_bytes)

	def asynchronousMoveTo(self,newpos):
		self.setNextFileName()
		if newpos!=self.exptime:	#send command to change exposure time if required
			self.exptime=newpos
			self.CAExposureTime.caput(self.exptime)
			sleep(1)
		x1(0)
		self.CAacquire.caput(1)
		sleep(0.5)
		x1(1)
		x1(0)
		#sleep(.5)

	def atStart(self):
		#print "Pilatus file name:"+self.CAFileName.caget()
		print "Pilatus file path:"+self.CAFilePath.caget()
		
import os
from org.eclipse.january.dataset import DatasetFactory, Dataset
from gda.analysis.io import LoadDataHolder
import array

class AndorAsciiLoader:
	''' Reads the temporary ascii file format being created by the Andor detector
	'''
	
	def __init__(self,filename,width,height,skipLines):
		self.filename = filename
		self.width = width
		self.height = height
		self.skipLines = skipLines
		
	def loadFile(self):
		''' Loads the file and returns its contents as a gda.analysis.io.LoadDataHolder object
		'''
		if not os.path.exists(self.filename):
                    raise IOError("File does not exist: " + self.filename)
		
		f= open(self.filename)
		rawData = array.array('d')
		lineNumber = 0
		for line in f:
			if lineNumber >= self.skipLines:
				rawData.append(float(line))
			lineNumber += 1
		
		data = DatasetFactory.createFromObject(self.rawData, self.height, self.width)
		
		output = LoadDataHolder();
		output.addDataSet(self.filename, data);
		return output;
			

#andor=AndorCCDClass('AndorCCD','BL16I-EA-ANDOR-01:','/dls_sw/i16/epics/andor/andor',andor_file_number,display_image=1, process_image=1, logscale=0)
andor=AndorCCDClass('AndorCCD','BL16I-EA-ANDOR-01:','/dls/i16/data/andorTest/',andor_file_number,display_image=1, process_image=1, logscale=0)

