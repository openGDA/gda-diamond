from gda.analysis.datastructure import *
from gda.analysis import *
from gda.device.scannable import PseudoDevice
from gda.configuration.properties import LocalProperties
from popen2 import popen2
from imaplib import path
import os
import java.io.FileNotFoundException

# test = ScanFileContainer()
# test.loadPilatusData("/dls/i16/data/Pilatus/test1556.tif")
# test.plot()
# matrix = test.getImage().doubleMatrix()

class PilatusClass(PseudoDevice):
	'''Pilatus PD
	obj=PilatusClass(name,pvroot,filepath,filename)
	e.g. pilatus=PilatusClass('P100k','BL16I-EA-PILAT-01:','/dls/i16/data/Pilatus/','p')
	pilatus.getThesholdEnergy to print threshhold
	Make sure camserver is runnning
	ssh -X det@i16-pilatus1  (password Pilatus2)
 	ps aux | grep cam   to see if camserver running
	to start camserver...
	cd p2_1mod
	camonly
	self.display_data=0 removes data plotting and data summary for faster aquisition
	self.setFileName(name) sets data file name e.g. 'p'
	self.setFilePath(name) sets data file path e.g. '/dls/i16/data/Pilatus/'
	self.defaultFileName()/ self.defaultFilePath()sets data file name/path back to the name given when the device was created
	'''

	def __init__(self,name,pvroot, pilatusType, filename, manualFilepath = None, display_image=1, process_image=1, logscale=1):
		# Scannable stuff
		self.setName(name);
		self.setInputNames(['ExposureTime'])
		self.setExtraNames(['FileNum','sum','max']);
		self.setOutputFormat(['%.2f', '%.0f', '%.0f', '%.0f'])
		self.setLevel(9)
	
		# File path/name/format stuff		
		if not subFolderName in ('pilatus100k' ,'pilatus2M'):
			raise IOError("The subfolder name specified must be either 'pilatus100k' or 'pilatus2M'")
		self.pilatusType = pilatusType
		self.manualFilepath = manualFilepath
		self.filename=filename
		self.default_filename=filename		
		self.filepath = None # Set once pilatus configured
		self.fileformat = None # determined later from pilatus

		# Display/process stuff		
		self.display_image=display_image
		self.process_image=process_image
		self.logscale = logscale	
		self.readImageTimeout = 20 # in seconds
		self.data = ScanFileHolder()	

		# State
		self.exptime=0
		self.sum=0
		self.maxpix=0

		# Epics stuff
		self.ClientRoot=pvroot

		# Configure
		self.configure()


	def configure(self):
		# Connect Epics
		self.__createCAClients()
		self.CANImages.caput(1) # do something? (RobW)
		
		# Filepath
		if self.manualFilepath:
			self.setFilePath(self.manualFilepath)
		else:
			self.configureToWriteInVisitFolder(self.pilatusType)
		
		# Filename/format
		self.setFileName(self.filename)
		self.fileformat=self.CAFileFormat.caget()

		# Not needed unless some strange hack (RobW):
		self.CAacquire.configure() 

	def __createCAClients(self):
		self.CAacquire=CAClient(self.ClientRoot+'Acquire'); self.CAacquire.configure()
		self.CANImages=CAClient(self.ClientRoot+'NImages');	self.CANImages.configure()
		self.CAabort=CAClient(self.ClientRoot+'Abort'); self.CAabort.configure()
		self.CAExposureTime=CAClient(self.ClientRoot+'ExposureTime'); self.CAExposureTime.configure()
		self.CAFilePath=CAClient(self.ClientRoot+'FilePath'); self.CAFilePath.configure()
		self.CAFileName=CAClient(self.ClientRoot+'Filename'); self.CAFileName.configure()
		self.CAFileNumber=CAClient(self.ClientRoot+'FileNumber'); self.CAFileNumber.configure()
		self.CAFileFormat=CAClient(self.ClientRoot+'FileFormat'); self.CAFileFormat.configure()
		self.CAThresholdEnergy=CAClient(self.ClientRoot+'ThresholdEnergy'); self.CAThresholdEnergy.configure()

	def isBusy(self):
		isbusy=float(self.CAacquire.caget())
		return float(isbusy)

	def stop(self):
		self.CAabort.caput(1)

	def getPosition(self):
		filenum=float(self.CAFileNumber.caget())-1
		return self.processAndDisplay(filenum)

	def processAndDisplay(self, filePathOrNumber = None):	
		filenum=float(self.CAFileNumber.caget())-1
		# load file if needed
		if self.process_image or self.display_image:
			# default to current file number
			if filePathOrNumber == None:
				filePathOrNumber = float(self.CAFileNumber.caget())-1
			if type(filePathOrNumber) in (int, float):
				filenum = filePathOrNumber	
				file = self.filepath+self.filename+"%04.0f" % filenum +self.fileformat[-4:]
				file = '/dls/i16'+file.split('/i16data')[1]
			elif type(filePathOrNumber) is str:
				file = filePathOrNumber
				filenum = -1
			else:
				raise IOException("input must be None, an integer or a path (string).")
			self.loadedFile = None
			self.keepTryingToLoadPilatusData(file)
			self.loadedFile = file
		# process
		if self.process_image:
			self.image=self.data.getImage()
			self.maxpix=self.image.max()
			self.sum=sum(self.image.doubleArray())
		else:
			self.sum = -1
			self.maxpix = -1			
		# display
		if self.display_image:
			if self.logscale:
				Plotter.plotImage("Data Vector", self.data.getImage().lognorm())
			else:
				Plotter.plotImage("Data Vector", self.data.getImage().norm())
		# return
		return [self.exptime, filenum, self.sum, self.maxpix]

	def loadPilatusData(self, file):
		# Returns true if the file could not be loaded
		try:
			os.system("touch %s"%file)
			self.data.loadPilatusData(file)
			return False
		#except java.io.FileNotFoundException, e:
		except:
			return True

	def keepTryingToLoadPilatusData(self, file):
		firstTryTime = None
		if self.loadPilatusData(file):
			firstTryTime = time.clock()
			sleep(0.1)
			while self.loadPilatusData(file):
				if time.clock() - firstTryTime > self.readImageTimeout:
					print "Could not load pilatus file %s, within specified timeout of %f s" % (file, self.readImageTimeout)
					raise IOError("Could not load pilatus file %s, within specified timeout of %f s" % (file, self.readImageTimeout))
			sleep(0.1)
		if firstTryTime:
			print "NOTE: It took %fs for the file %s to get across NFS." % (time.clock()-firstTryTime, file)
			



	def asynchronousMoveTo(self,newpos):
		if newpos!=self.exptime:	#send command to change exposure time if required
			self.exptime=newpos
			self.CAExposureTime.caput(self.exptime)
			sleep(1)

		self.CAacquire.caput(1)
	
	def getThresholdEnergy(self):
		print "Threshold: "+str(self.CAThresholdEnergy.caget())+" eV"

	def atStart(self):
		print "Pilatus file name:"+self.CAFileName.caget()
		print "Pilatus file path:"+self.CAFilePath.caget()

	def display(self,file=None):
		if file==None:
			filenum=float(self.CAFileNumber.caget())-1
			file = self.filepath+self.filename+"%04.0f" % filenum +self.fileformat[-4:]
		print file
		self.data.loadPilatusData(file)
		if self.logscale:
			Plotter.plotImage("Data Vector",self.data.getImage().lognorm())
		else:
			Plotter.plotImage("Data Vector",self.data.getImage().norm())

	def setFileName(self,filename):
		self.filename=filename		
		self.CAFileName.caput(self.filename)

	def defaultFileName(self):
		self.filename=self.default_filename		
		self.CAFileName.caput(self.filename)

	def setManualFilePath(self, path):
		self.manualFilepath = path
		self.configure()

	def setFilePath(self,filepath):
		self.filepath=filepath		
		self.CAFilePath.caput(self.filepath)
		sleep(1)


	def configureToWriteInVisitFolder(self,subFolderName):	
		if not subFolderName in ('pilatus100k' ,'pilatus2M'):
			raise IOError("The subfolder name specified must be either 'pilatus100k' or 'pilatus2M'")
		thedatadir = LocalProperties.getPath("gda.data.scan.datawriter.datadir",None)
		print "Current datadir = ", thedatadir
		print "  ( Change using datadir(path) if needed )"

		pilatusdir = thedatadir + "/" + subFolderName + "/"
		if os.path.exists(pilatusdir):
			print "The directory ", pilatusdir, " exists already."
		else:
			print "WARNING: This directory ", pilatusdir, "does NOT exist. Creating and setting facls..."
			if os.system("mkdir %s" % pilatusdir):
				raise IOError("Could not create folder ", pilatusdir, " (as user gda)")
			print "   ...directory created."

		remotepilatusdir = "/i16data/" + pilatusdir.split("/dls/i16/")[1] 		
		
		print "Configuring pilatus to write to this filepath..."
		self.setFilePath(remotepilatusdir)


pil2m=PilatusClass('P2M','BL16I-EA-PILAT-02:',datadir()+'/pilatus2M/','test',display_image=0, process_image=0, logscale=1) 
pil2m.process_image=1
pil2m.display_image=1
#pil2m.processAndDisplay()
sleep(1)
pil2m.configureToWriteInVisitFolder('pilatus2M')


#pil100k=PilatusClass('P100k','BL16I-EA-PILAT-01:','/dls/i16/data/2009/mt0/run1/pilatus100k/','p')
#pil100kvrf=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VRF','BL16I-EA-PILAT-01:VRF','BL16I-EA-PILAT-01:VRF','V','%.3f',help='set VRF (gain) for pilatus\nReturns set value rather than true readback\n-0.05=very high\n-0.15=high\n-0.2=med\n-0.3=low')
#pil100kvcmp=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VCMP','BL16I-EA-PILAT-01:VCMP','BL16I-EA-PILAT-01:VCMP','V','%.3f',help='set VCMP (threshold) for pilatus\nReturns set value rather than true readback\n0-1 V')
#pil100kgain=SingleEpicsPositionerSetAndGetOnlyClass('P100k_gain','BL16I-EA-PILAT-01:Gain','BL16I-EA-PILAT-01:Gain','','%.3f',help='set gain for pilatus\nReturns set value rather than true readback\n3=very high\n2=high\n1=med\n0=low')
#pil100kthresh=SingleEpicsPositionerSetAndGetOnlyClass('P100k_threshold','BL16I-EA-PILAT-01:ThresholdEnergy','BL16I-EA-PILAT-01:ThresholdEnergy','','%.0f',help='set energy threshold for pilatus (eV)\nReturns set value rather than true readback')
#
##pil2m=PilatusClass('P2M','BL16I-EA-PILAT-02:','/i16data/data/2008/mt0/pilatus2/','test',display_image=0, process_image=0, logscale=1)
#pil2m=PilatusClass('P2M','BL16I-EA-PILAT-02:','/i16data/data/2009/mt0/run1/pilatus2m/','test',display_image=0, process_image=0, logscale=1)
#
#pil2mgain=SingleEpicsPositionerSetAndGetOnlyClass('P2M_gain','BL16I-EA-PILAT-02:Gain','BL16I-EA-PILAT-02:Gain','','%.3f',help='set gain for pilatus\nReturns set value rather than true readback\n3=very high\n2=high\n1=med\n0=low')
#pil2mthresh=SingleEpicsPositionerSetAndGetOnlyClass('P2M_threshold','BL16I-EA-PILAT-02:ThresholdEnergy','BL16I-EA-PILAT-02:ThresholdEnergy','','%.0f',help='set energy threshold for pilatus (eV)\nReturns set value rather than true readback')
#
#pil=pil100k
##pil=pil2m

 


#pil.display_data=0




#from gda.analysis import *

#data = ScanFileHolder()

#data.loadPilatusData("/dls/i16/data/Pilatus/p0246.tif")
#data.plot()

#scans through the data so that the different parts can be seen easily.
#for i in range(0,10):
#	print i
#	Plotter.plotImage((data.getImage().norm()*10)-i)

#Plotter.plotImage((data.getImage().pow(3).norm()))
#Plotter.plotImage((data.getImage().pow(0.5).norm()))

#Plotter.plotImage((data.getImage().lognorm()))
#Plotter.plotImage((data.getImage().lnnorm()))



#print "Quelquechose"
#pilatus = PilatusClass('Pilatus')
#pil = PilatusSingleExposureClass('Pilatus')

#>>>pilatus.data.getImage().max()
#58848.0
#>>>pilatus.data.getImage().min()
#>>>pilatus.data.getImage().get([12,24])
#sum(list(pilatus.data.getImage().doubleArray())[-10:-1])
#sum(list(pilatus.data.getImage().doubleArray()))
