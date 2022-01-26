from gda.analysis.datastructure import *
from gda.analysis import *
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from time import sleep
from java.lang import String

class Pilatus(ScannableMotionBase):
	'''Pilatus PD
	obj=pd_pilatus.Pilatus(name,pvroot,filepath,filename)
	e.g. pilatus=pd_pilatus.Pilatus('P100k','BL15I-EA-PILAT-01:','/dls/i15/data/2008/ee0/005','p')
	self.display_data=0 removes data plotting and data summary for faster aquisition
		For Pilatus make sure to have:
		 0)  make sure camserver and TVX are not running on the pilatus PC
		 1)  ssh -X 15detector@i15-pilatus1 (pw:Villigen)
		 2)  cd p2_det
		 3)  ./camserver ~/p2_det
		 4)  In the gda type 'reset_namespace'
		To restart the whole malarchy:
		 a)  Kill the IOC: Close the window created in step 4 (titled 'Terminal')
		 b)  Stop camserver: Go to the terminal used for steps 1 to 3 and press 'control' and 'c' together
		 c)  Start it all up: Uses steps 3 to 6 above
	'''

	def __init__(self,name,pvroot,filepath,filename, display_image=1, process_image=1, logscale=0):
		"""Constructor for Pilatus"""

		self.setName(name);
		self.setInputNames(['ExposureTime'])
		self.setExtraNames(['FileNum','sum','max']);
		self.setOutputFormat(['%.2f', '%.0f', '%.0f', '%.0f'])
		self.setLevel(9)
		self.ClientRoot=pvroot

		self.display_image=display_image
		self.process_image=process_image
		self.logscale = logscale
		self.hotpixels=[]

		self.CAacquire=CAClient(self.ClientRoot+'Acquire'); self.CAacquire.configure()
		self.CANImages=CAClient(self.ClientRoot+'NImages');	self.CANImages.configure()
		self.CAabort=CAClient(self.ClientRoot+'Abort'); self.CAabort.configure()
		self.CAExposureTime=CAClient(self.ClientRoot+'ExposureTime'); self.CAExposureTime.configure()
		self.CAFilePath=CAClient(self.ClientRoot+'FilePath'); self.CAFilePath.configure()
		self.CAFileName=CAClient(self.ClientRoot+'Filename'); self.CAFileName.configure()
		self.CAFileNumber=CAClient(self.ClientRoot+'FileNumber'); self.CAFileNumber.configure()
		self.CAFileFormat=CAClient(self.ClientRoot+'FileFormat'); self.CAFileFormat.configure()
		self.CAFullFileName=CAClient(self.ClientRoot+'FullFilename'); self.CAFullFileName.configure()
		
		self.CANImages.caput(1)
		self.CAFilePath.caput(filepath)
		self.CAFileName.caput(filename)

		self.data = ScanFileHolder()
		self.sum=0
		self.maxpix=0
		self.CAacquire.configure()
		
		print "Pilatus setup complete"

	def setFilePath(self, newFilePath):
		"""Set the file path for the image files"""
		self.CAFilePath.caput(newFilePath)
		print "File path set to " + newFilePath

	def getFilePath(self):
		return self.CAFilePath.caget()
		
	def isBusy(self):
		isbusy=float(self.CAacquire.caget())
		return float(isbusy)

	def stop(self):
		self.CAabort.caput(1)

	def getPosition(self):
		"""Returns [exposure time, filenumber, nsum, maxpix]"""
		# load file if needed
		file = self.getFullFilename()
		print "Getting file: " + file
		if self.process_image or self.display_image:			
			self.data.loadPilatusData(file)
			self.image=self.data.getImage()

		# process
		if self.process_image:
			maxpix=self.image.max()
			nsum=sum(self.image.doubleArray())
		else:
			nsum = -1
			maxpix = -1			

		# display
		if self.display_image:
			self.__plot()
			
		# return
		
		return [self.CAExposureTime.caget(), self.CAFileNumber.caget(), nsum, maxpix]

	def getFullFilename(self):
		"""Returns file path of the last created image"""
		data = self.CAFullFileName.cagetArray()
		intArray = []
		for d in data:
			val = int(d)
			if val == 0:
				break
			intArray.append(val)
		s = String(intArray)
		return self.CAFilePath.caget() + `s`
	
	def getCurrentFullFilename(self):
		"""Returns file path of the next image to be created"""
		return self.getFilePath() + self.CAFileName.caget() + "%04.0f" % self.getFileNumber() + self.CAFileFormat.caget()[-4:]
		
	def setFilename(self, fileName):
		"""Set filename - not the path"""
		self.CAFileName.caput(fileName)

	def setFileNumber(self, fileNumber):
		"""Set filenumber"""
		self.CAFileNumber.caput(fileNumber)

	def getFileNumber(self):
		"""Get filenumber"""
		return self.CAFileNumber.caget()

	def asynchronousMoveTo(self,newpos):
		"""Performs exposure of given time"""
		if newpos != self.CAExposureTime.caget():	#send command to change exposure time if required
			self.CAExposureTime.caput(newpos)
			sleep(1)
		self.CAacquire.caput(1)

	def expose(self,exposureTime):
		"""Calls asynchronousMoveTo to perform exposure of given time"""
		self.asynchronousMoveTo(exposureTime)

	def atScanStart(self):
		print "Pilatus file name:"+self.CAFileName.caget()
		print "Pilatus file path:"+self.CAFilePath.caget()

	def display(self,file=None):
		if file==None:
			file = self.getFullFilename()
		print file
		self.data.loadPilatusData(file)
		self.image = self.data.getImage()
		self.__plot()

	def __plot(self):
		"""Plots the image assuming an image has been loaded into self.image .
		SIDE EFFECT WARNING: May alter image."""

		for (x,y) in self.hotpixels:
			self.image.set(0,(x,y))

		if self.logscale:
			Plotter.plotImage("Pilatus Display", self.image.lognorm())
		else:
			Plotter.plotImage("Pilatus Display",self.image)
			
		print "Pilatus image displayed"


import os
class DummyPilatus(ScannableMotionBase):
	'''Pilatus PD
	obj=pd_pilatus.Pilatus(name,pvroot,filepath,filename)
	e.g. pilatus=pd_pilatus.Pilatus('P100k','BL15I-EA-PILAT-01:','/dls/i15/data/2008/ee0/005','p')
	self.display_data=0 removes data plotting and data summary for faster aquisition
	'''

	def __init__(self,name,pvroot,filepath,filename, display_image=1, process_image=1, logscale=0):
		self.setName(name);
		self.setInputNames(['ExposureTime'])
		self.setExtraNames(['FileNum','sum','max']);
		self.setOutputFormat(['%.2f', '%.0f', '%.0f', '%.0f'])
		self.setLevel(9)
		self.ClientRoot=pvroot

		self.display_image=display_image
		self.process_image=process_image
		self.logscale = logscale
		self.hotpixels=[]
		self.filepath = filepath
		self.filename = filename
		self.filenum = 5
		self.fileformat = "%s%s%4.4d.tif"
		self.exposureTime = 0

		self.data = ScanFileHolder()
		self.sum=0
		self.maxpix=0
		print "Pilatus dummy setup complete"

	def setFilePath(self, newFilePath):
		"""Set file path"""
		self.filepath = newFilePath
		print "File path set to " + newFilePath
	
	def  getFilePath(self):
		return self.filepath

	def setFileNumber(self, fileNumber):
		"""Set filenumber"""
		self.filenum = fileNumber

	def getFileNumber(self):
		"""Get filenumber"""
		return self.filenum
	
	def isBusy(self):
		return False

	def stop(self):
		return

	def getPosition(self):
		return [ self.exposureTime, self.fileNumber, 1, 1]

	def getFullFilename(self):
		"""Returns file path of the LAST CREATED image"""
		return self.filepath + self.filename + "%04.0f" % (self.filenum - 1) + self.fileformat[-4:]
	
	def getCurrentFullFilename(self):
		"""Returns file path of the next image to be created"""
		return self.filepath + self.filename + "%04.0f" % self.filenum + self.fileformat[-4:]
		
	def setFilename(self, fileName):
		"""Set filename - not the path"""
		self.filename = fileName

	def asynchronousMoveTo(self,newpos):
		"""Performs dummy exposure of given time"""
		if newpos != self.exposureTime:
			self.exposureTime = newpos
			sleep(1)
		print "Dummy expose for " + str(self.exposureTime) + " secs"
		
		# Create a dummy file and increase file number
		currentFullFilename = self.filepath + self.filename + "%04.0f" % self.filenum + self.fileformat[-4:]
		os.system("touch " + currentFullFilename)
		self.filenum = self.filenum + 1
		
	def expose(self,exposureTime):
		"""Calls asynchronousMoveTo to performs dummy exposure of given time"""
		self.asynchronousMoveTo(exposureTime)

	def atScanStart(self):
		print "Pilatus file name:"+self.filename
		print "Pilatus file path:"+self.filepath

	def display(self,file=None):
		if file==None:
			file = self.getFullFilename()
		print file
		self.data.loadPilatusData(file)
		self.image = self.data.getImage()
		self.__plot()

	def __plot(self):
		"""Plots the image assuming an image has been loaded into self.image .
		SIDE EFFECT WARNING: May alter image."""

		for (x,y) in self.hotpixels:
			self.image.set(0,(x,y))

		if self.logscale:
			Plotter.plotImage("Pilatus Display", self.image.lognorm())
		else:
			Plotter.plotImage("Pilatus Display",self.image)			
