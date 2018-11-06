from gda.analysis.datastructure import *
from gda.analysis import *
import java.io.FileNotFoundException
# test = ScanFileContainer()
# test.loadPilatusData("/dls/i16/data/Pilatus/test1556.tif")
# test.plot()
# matrix = test.getImage().doubleMatrix()

class PilatusClass(ScannableMotionBase):
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

	def __init__(self,name,pvroot,filepath,filename, display_image=1, process_image=1, logscale=1):
		self.setName(name);
		self.setInputNames(['ExposureTime'])
		self.setExtraNames(['FileNum','max','sum']);
		self.setOutputFormat(['%.2f', '%.0f', '%.0f', '%.0f'])
		self.setLevel(9)
		self.ClientRoot=pvroot
		self.filename=filename
		self.default_filename=filename
		self.filepath=filepath
		self.default_filepath=filepath
		self.display_image=display_image
		self.process_image=process_image
		self.logscale = logscale

		self.CAacquire=CAClient(self.ClientRoot+'Acquire'); self.CAacquire.configure()
		self.CANImages=CAClient(self.ClientRoot+'NImages');	self.CANImages.configure()
		self.CAabort=CAClient(self.ClientRoot+'Abort'); self.CAabort.configure()
		self.CAExposureTime=CAClient(self.ClientRoot+'ExposureTime'); self.CAExposureTime.configure()
		self.CAFilePath=CAClient(self.ClientRoot+'FilePath'); self.CAFilePath.configure()
		self.CAFileName=CAClient(self.ClientRoot+'Filename'); self.CAFileName.configure()
		self.CAFileNumber=CAClient(self.ClientRoot+'FileNumber'); self.CAFileNumber.configure()
		self.CAFileFormat=CAClient(self.ClientRoot+'FileFormat'); self.CAFileFormat.configure()
		self.CAThresholdEnergy=CAClient(self.ClientRoot+'ThresholdEnergy'); self.CAThresholdEnergy.configure()

		self.CANImages.caput(1)
		self.CAFilePath.caput(self.filepath)
		self.CAFileName.caput(self.filename)
		self.fileformat=self.CAFileFormat.caget()

		self.data = ScanFileHolder()
		self.exptime=0
		self.sum=0
		self.maxpix=0
		self.filenum=0
		self.CAacquire.configure()


	def isBusy(self):
		isbusy=float(self.CAacquire.caget())
		return float(isbusy)

	def stop(self):
		self.CAabort.caput(1)

	def getPosition(self):
		self.filenum=float(self.CAFileNumber.caget())-1
		# load file if needed
		if self.process_image or self.display_image:
			file = self.filepath+self.filename+"%04.0f" % self.filenum +self.fileformat[-4:]
			try:
				self.loadPilatusData(file)
			except IOError:
				return [self.exptime, self.filenum, -1, -1]
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
		#return [self.exptime, self.filenum, self.sum, self.maxpix]
		return [self.exptime, self.filenum, self.maxpix, self.sum]

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
			file = self.filepath+self.filename+"%04.0f" % self.filenum +self.fileformat[-4:]
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

	def setFilePath(self,filepath):
		self.filepath=filepath		
		self.CAFilePath.caput(self.filepath)

	def defaultFilePath(self):
		self.filepath=self.default_filepath		
		self.CAFilePath.caput(self.filepath)

	def loadPilatusData(self, path):
		path = path.replace('/i16data/','/dls/i16/') #Hack for the case where the pilatus machine mounts i16storage differently
		try:
			self.data.loadPilatusData(path)
		except java.io.FileNotFoundException, e:
			print "Could not load Pilatus file: %s" % path
			raise IOError(e.getMessage)


class PilatusClassWithRobustLoading(PilatusClass):

	def __init__(self, name,pvroot,filepath,filename, readImageTimeout, display_image=1, process_image=1, logscale=1):
		self.readImageTimeout = readImageTimeout
		self.printNfsTimes = False
		PilatusClass.__init__(self, name, pvroot, filepath, filename, display_image, process_image, logscale)
	
	def loadPilatusData(self, path):
		path = path.replace('/i16data/','/dls/i16/') #Hack for the case where the pilatus machine mounts i16storage differently
		self.keepTryingToLoadPilatusData(path)
		
	def tryToLoadPilatusData(self, path):
		# Returns true if the file could not be loaded
		try:
			os.system("touch %s"%path)
			self.data.loadPilatusData(path)
			return False
		#except java.io.FileNotFoundException, e:
		except:
			return True

	def keepTryingToLoadPilatusData(self, path):
		firstTryTime = None
		if self.tryToLoadPilatusData(path):	# True if problem
			firstTryTime = time.clock()
			sleep(0.1)
			while self.tryToLoadPilatusData(path):
				if time.clock() - firstTryTime > self.readImageTimeout:
					print "Could not load pilatus file %s, within specified timeout of %f s" % (path, self.readImageTimeout)
					raise IOError("Could not load pilatus file %s, within specified timeout of %f s" % (path, self.readImageTimeout))
			sleep(0.1)
		if firstTryTime:
			if self.printNfsTimes:
				print "NOTE: It took %fs for the file %s to cross NFS." % (time.clock()-firstTryTime, path)
	

#oldone# pil100k=PilatusClass('P100k','BL16I-EA-PILAT-01:','/dls/i16/data/2009/mt0/run2/pilatus100k/','p')
pil100k=PilatusClassWithRobustLoading('P100k','BL16I-EA-PILAT-01:','/dls/i16/data/2009/mt769-1/pilatus100k/','p',10)
pil100k.printNfsTimes = True

pil100kvrf=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VRF','BL16I-EA-PILAT-01:VRF','BL16I-EA-PILAT-01:VRF','V','%.3f',help='set VRF (gain) for pilatus\nReturns set value rather than true readback\n-0.05=very high\n-0.15=high\n-0.2=med\n-0.3=low')
pil100kvcmp=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VCMP','BL16I-EA-PILAT-01:VCMP','BL16I-EA-PILAT-01:VCMP','V','%.3f',help='set VCMP (threshold) for pilatus\nReturns set value rather than true readback\n0-1 V')
pil100kgain=SingleEpicsPositionerSetAndGetOnlyClass('P100k_gain','BL16I-EA-PILAT-01:Gain','BL16I-EA-PILAT-01:Gain','','%.3f',help='set gain for pilatus\nReturns set value rather than true readback\n3=very high\n2=high\n1=med\n0=low')
pil100kthresh=SingleEpicsPositionerSetAndGetOnlyClass('P100k_threshold','BL16I-EA-PILAT-01:ThresholdEnergy','BL16I-EA-PILAT-01:ThresholdEnergy','','%.0f',help='set energy threshold for pilatus (eV)\nReturns set value rather than true readback')

#oldone# pil2m=PilatusClass('P2M','BL16I-EA-PILAT-02:','/i16data/data/2009/mt0/run2/pilatus2M/','test', display_image=1, process_image=1, logscale=1)
pil2m=PilatusClassWithRobustLoading('P2M','BL16I-EA-PILAT-02:','/i16data/data/2009/mt0/run2/pilatus2M/','test',10, display_image=1, process_image=1, logscale=1)

#pil2mgain=SingleEpicsPositionerSetAndGetOnlyClass('P2M_gain','BL16I-EA-PILAT-02:Gain','BL16I-EA-PILAT-02:Gain','','%.3f',help='set gain for pilatus\nReturns set value rather than true readback\n3=very high\n2=high\n1=med\n0=low')
#pil2mthresh=SingleEpicsPositionerSetAndGetOnlyClass('P2M_threshold','BL16I-EA-PILAT-02:ThresholdEnergy','BL16I-EA-PILAT-02:ThresholdEnergy','','%.0f',help='set energy threshold for pilatus (eV)\nReturns set value rather than true readback')

pil=pil100k
#pil=pil2m

 


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
