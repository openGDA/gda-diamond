#from gda.analysis.datastructure import *
#from gda.analysis import *
## test = ScanFileContainer()
## test.loadPilatusData("/dls/i16/data/Pilatus/test1556.tif")
## test.plot()
## matrix = test.getImage().doubleMatrix()
##
#
#
#
## PILATUS UTILITILITIES
#
## to set the FilePath, run the following line from a terminal
## ./ca_string_put.py BL16I-EA-PILAT-01:FilePath /disk2/images/test/
##./ca_string_put.py BL16I-EA-PILAT-01:FilePath /dls/i16/data/Pilatus/
#
#class NumericalEpicsRecordClass(PseudoDevice):
#
#	def __init__(self,name,outputformat):
#		self.setName(name);
#		self.setInputNames([name])
#		self.setOutputFormat([outputformat])
#		self.cli = CAClient(self.name)
#		self.cli.configure()
#
#	def isBusy(self):
#		return 0
#
#	def getPosition(self):
#		#self.cli.configure()
#		return float(self.cli.caget())
#		#self.cli.clearup()
#
#	def asynchronousMoveTo(self,newpos):
#		#self.cli.configure()
#		return self.cli.caput(newpos)
#		#self.cli.clearup()
#
#class StringEpicsRecordClass(PseudoDevice):
#
#	def __init__(self,name):
#		self.setName(name);
#		self.setInputNames([name])
#		self.cli = CAClient(self.name)
#		self.cli.configure()
#
#	def isBusy(self):
#		return 0
#
#	def getPosition(self):
#		#self.cli.configure()
#		return self.cli.caget()
#		#self.cli.clearup()
#
#	def asynchronousMoveTo(self,newval):
#		#self.cli.configure()
#		return self.cli.caput(newval)
#		#self.cli.clearup()
#
#
#
#class PilatusClass(PseudoDevice):
#	'''Create Pilatus PD and utilities
#	Make sure camserver is runnning
#	ssh -X det@i16-pilatus1  (password Pilatus2)
# 	ps aux | grep cam   to see if camserver running
#	to start camserver...
#	cd p2_1mod
#	camonly
#	'''
#
#	def __init__(self,name):
#		self.setName(name);
#		self.setInputNames(['ExposureTime'])
#		self.setExtraNames(['FileNum','sum','max']);
#		self.Units=['s']
#		self.setOutputFormat(['%.2f', '%.0f', '%.0f', '%.0f'])
#		self.setLevel(9)
#		self.ClientRoot = 'BL16I-EA-PILAT-01:'
#		self.CAImageData = CAClient(self.ClientRoot+'ImageData')
#		self.CAacquire=CAClient(self.ClientRoot+'Acquire')
#		self.CANExposures=CAClient(self.ClientRoot+'NExposures')
#		self.CANImages=CAClient(self.ClientRoot+'NImages')
#		self.CAabort=CAClient(self.ClientRoot+'Abort')
#	#	self.CAExposureTime=CAClient(self.ClientRoot+'ExposureTime')
#		self.exposuretime=NumericalEpicsRecordClass(self.ClientRoot+'ExposureTime','%.1f')
#		self.exposureperiod=NumericalEpicsRecordClass(self.ClientRoot+'ExposurePeriod','%.1f')
#		self.nimages=NumericalEpicsRecordClass(self.ClientRoot+'NImages','%.0f')
#		self.CAFilePath=CAClient(self.ClientRoot+'FilePath'); self.CAFilePath.configure()
#		self.CAFilename=CAClient(self.ClientRoot+'Filename'); self.CAFilename.configure()
#		self.filepath=StringEpicsRecordClass(self.ClientRoot+'FilePath')
#		self.filename=StringEpicsRecordClass(self.ClientRoot+'Filename')
#		self.filenumber=NumericalEpicsRecordClass(self.ClientRoot+'FileNumber','%.0f')
#		self.fileformat=StringEpicsRecordClass(self.ClientRoot+'FileFormat')
#		self.CAFileFormat=CAClient(self.ClientRoot+'FileFormat')
#		self.CAFullFilename=CAClient(self.ClientRoot+'FullFilename');self.CAFullFilename.configure()
#		self.ReadTiffTimeout = NumericalEpicsRecordClass(self.ClientRoot+'ReadTiffTimeout','%.1f')
#		#self.data = ScanFileContainer()
#		self.data = ScanFileHolder()
#		#self.CAacquire.configure()
#		self.exptime=0
#		self.CAacquire.configure()
#		self.display_data=1
#
#	def isBusy(self):
##		print 'isbiz start'
#		isbusy=float(self.CAacquire.caget())
##		print float(isbusy)
#		return float(isbusy)
##		print 'isbiz end'
#
#	def acquire(self):
##		print 'acquire start'
#		self.CAFilename.caput('p')
#		sleep(1)#################seems to need this
#		self.CAFilePath.caput('/dls/i16/data/Pilatus/')
#		sleep(1)######################seems to need this one
#		self.CAacquire.caput(1)
##		sleep(self.exptime+1)#because isBusy doesn't always work
##		print 'acquire end'
#
#	def average10(self):
#		self.CANExposures.configure()
#		self.CANExposures.caput(10)
#		self.CANExposures.clearup()
#		self.CANImages.configure()
#		self.CANImages.caput(10)
#		self.CANImages.clearup()
#		self.CAacquire.configure()
#		self.CAacquire.caput(1)
#		self.CAacquire.clearup()
#
#	def abort(self):
#		self.CAabort.configure()
#		self.CAabort.caput(1)
#		self.CAabort.clearup()
#
#	def stop(self):
#		self.abort()
#
#	def getPosition(self):
##		print 'getpos start'
#		if self.display_data==1:
#			self.display()
#		else:
#			sleep(.5)
#		return [self.exposuretime(), self.filenumber()-1,self.sum, self.maxpix]
#		print 'getpos end'
#
#	def asynchronousMoveTo(self,newpos):
##		print 'moveto start'
#		if newpos!=self.exptime:
#			self.exptime=newpos
#			self.nimages(1)
#			self.exposuretime(newpos)
#			self.exposureperiod(newpos+0.1)
#			sleep(1)
#		self.acquire()
##		print 'moveto end'
#
#	def atScanStart(self):
#		print "Pilatus file name:"+self.CAFilename.caget()
#		print "Pilatus file path:"+self.CAFilePath.caget()
#
##	def display(self,file=None):
##		if file==None:
##			file = self.filepath() + self.filename() + "%04.0f" % (self.filenumber()-1) + self.fileformat()[-4:]
##		print file
##		self.data.loadPilatusData(file)
##		self.data.plot()
#
#	def display(self,file=None):
#		if file==None:
#			file = self.filepath() + self.filename() + "%04.0f" % (self.filenumber()-1) + self.fileformat()[-4:]
#		#print file
#		self.data.loadPilatusData(file)
#		self.data.plot()
#		Plotter.plotImage(self.data.getImage().lognorm())
#		self.image=self.data.getImage()
#		self.maxpix=self.image.max()
#		self.sum=sum(self.image.doubleArray())
#
#
##from gda.analysis import *
#
##data = ScanFileHolder()
#
##data.loadPilatusData("/dls/i16/data/Pilatus/p0246.tif")
##data.plot()
#
# #scans through the data so that the different parts can be seen easily.
##for i in range(0,10):
##	print i
##	Plotter.plotImage((data.getImage().norm()*10)-i)
#
##Plotter.plotImage((data.getImage().pow(3).norm()))
##Plotter.plotImage((data.getImage().pow(0.5).norm()))
#
##Plotter.plotImage((data.getImage().lognorm()))
##Plotter.plotImage((data.getImage().lnnorm()))
#
#
#
#
#
#class PilatusSingleExposureClass(PseudoDevice):
#	'''Create Pilatus PD and utilities
#	Make sure camserver is runnning
#	ssh -X det@i16-pilatus1  (password Pilatus2)
# 	ps aux | grep cam   to see if camserver running
#	to start camserver...
#	cd p2_1mod
#	camonly
#	'''
#
#	def __init__(self,name):
#		self.setName(name);
#		self.setInputNames(['ExposureTime'])
#		self.setExtraNames(['FileNum']);
#		#self.Units=['' 's']
#		self.setOutputFormat(['%.2f' '%.0f'])
#		self.setLevel(9)
#		self.ClientRoot = 'BL16I-EA-PILAT-01:'
#		self.CAImageData = CAClient(self.ClientRoot+'ImageData')
#		self.CAacquire=CAClient(self.ClientRoot+'Acquire')
#		self.CANExposures=CAClient(self.ClientRoot+'NExposures')
#		self.CANImages=CAClient(self.ClientRoot+'NImages')
#		self.CAabort=CAClient(self.ClientRoot+'Abort')
#	#	self.CAExposureTime=CAClient(self.ClientRoot+'ExposureTime')
#		self.exposuretime=NumericalEpicsRecordClass(self.ClientRoot+'ExposureTime','%.1f')
#		self.exposureperiod=NumericalEpicsRecordClass(self.ClientRoot+'ExposurePeriod','%.1f')
#		self.nimages=NumericalEpicsRecordClass(self.ClientRoot+'NImages','%.0f')
#		self.CAFilePath=CAClient(self.ClientRoot+'FilePath'); self.CAFilePath.configure()
#		self.CAFilename=CAClient(self.ClientRoot+'Filename'); self.CAFilename.configure()
#		self.filepath=StringEpicsRecordClass(self.ClientRoot+'FilePath')
#		self.filename=StringEpicsRecordClass(self.ClientRoot+'Filename')
#		self.filenumber=NumericalEpicsRecordClass(self.ClientRoot+'FileNumber','%.0f')
#		self.fileformat=StringEpicsRecordClass(self.ClientRoot+'FileFormat')
#		self.CAFileFormat=CAClient(self.ClientRoot+'FileFormat')
#		self.CAFullFilename=CAClient(self.ClientRoot+'FullFilename');self.CAFullFilename.configure()
#		self.ReadTiffTimeout = NumericalEpicsRecordClass(self.ClientRoot+'ReadTiffTimeout','%.1f')
#		self.data = ScanFileContainer()
#		#self.CAacquire.configure()
#		self.CAacquire.configure()
#
#	def isBusy(self):
#		self.CAacquire.configure()
#		isbusy=float(self.CAacquire.caget())
#		self.CAacquire.clearup()
##		print float(isbusy)
#		return float(isbusy)
#
#	def acquire(self):
#		self.CAFilename.caput('p')
#		self.CAFilePath.caput('/dls/i16/data/Pilatus/')
#		self.CAacquire.caput(1)
#		sleep(1)
#	
#	def average10(self):
#		self.CANExposures.configure()
#		self.CANExposures.caput(10)
#		self.CANExposures.clearup()
#		self.CANImages.configure()
#		self.CANImages.caput(10)
#		self.CANImages.clearup()
#		self.CAacquire.configure()
#		self.CAacquire.caput(1)
#		self.CAacquire.clearup()
#
#	def abort(self):
#		self.CAabort.configure()
#		self.CAabort.caput(1)
#		self.CAabort.clearup()
#
#	def stop(self):
#		self.abort()
#
#	def getPosition(self):
#		return [self.exposuretime(), self.filenumber()-1]
#
#	def asynchronousMoveTo(self,newpos):
#		self.nimages(1)
#		self.exposuretime(newpos)
#		self.exposureperiod(newpos+0.1)
#		sleep(1)
#		self.acquire()
#
#	def atScanStart(self):
#		print "Pilatus file name:"+self.CAFilename.caget()
#		print "Pilatus file path:"+self.CAFilePath.caget()
#
#	def display(self,file=None):
#		if file==None:
#			file = self.filepath() + self.filename() + "%04.0f" % (self.filenumber()-1) + self.fileformat()[-4:]
#		print file
#		self.data.loadPilatusData(file)
#		self.data.plot()
#		self.image=self.data.getImage()
#		self.maxpix=self.image.max()
#		self.sum=sum(self.image.doubleArray())
#
#
#
#
##print "Quelquechose"
#pilatus = PilatusClass('Pilatus')
##pil = PilatusSingleExposureClass('Pilatus')
#
##>>>pilatus.data.getImage().max()
##58848.0
##>>>pilatus.data.getImage().min()
##>>>pilatus.data.getImage().get([12,24])
##sum(list(pilatus.data.getImage().doubleArray())[-10:-1])
##sum(list(pilatus.data.getImage().doubleArray()))
