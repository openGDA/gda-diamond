from gda.epics import CAClient 
from gda.device.scannable import ScannableMotionBase
from misc_functions import caput, caget
from time import sleep


class Mca(ScannableMotionBase):
	def __init__(self,name,pvstring):
		self.setName(name)
		self.pvstring=pvstring
		self.setInputNames(['MCActs'])
		
		self.channels = int(self.getProperty( '.NUSE' ))
		self.setOutputFormat( ['%.0f'] * self.channels )
		self.setExtraNames(['MCActs'] * (self.channels-1) )
		
		self.xxx = CAClient(pvstring+".VAL")
		self.xxx.configure()
		self.setLevel(9)
		
	def __del__(self):
		self.xxx.clearup()

	def setProperty(self,name,value):
		caput(self.pvstring+name,value)
		
	def getProperty(self,name):
		return caget(self.pvstring+name)
					
	def setDefaults(self):
		"""Set the MCA property to defaults values"""  
		self.setProperty('.NUSE',2048)
		self.setProperty('.PLTM',0)
		self.setProperty('.PRTM',0)
		self.setProperty('.PCTL',1)
		self.setProperty('.PCTH',0)
		self.setProperty('.PCT',0)
		self.setProperty('.HIGH',40)
		self.setProperty('.HIHI',70)
		self.setProperty('.MODE',0)
		self.setProperty('.CHAS',0)
		self.setProperty('.DWEL',0)
		self.setProperty('.PSCL',1)
		self.setProperty('Read.SCAN',1)
		self.setProperty('Status.SCAN',.1)
		self.setProperty('EnableWait',.1)

	def setROI(self,index,low,high):
		pass

	def start(self):
		"""Start the MCA data acquisiton"""
		self.setProperty('.STRT', 1)
		self.needsRead=1

	def ctime(self,ctime=None):
		"""Define the preset Live Time"""
		if ctime==None:
			return self.getProperty('.PLTM')
		self.setProperty('.PLTM', ctime)
		return self.getProperty('.PLTM')

	def stop(self):
		"""Stop The acquisition"""
		self.setProperty('.STOP', 1)

	def erase(self):
		"""Erase the spectra"""
		self.setProperty('.ERAS', 1)
		self.needsRead=1

	def read(self):
		"""Start data transfer from AIM"""
		self.setProperty('.READ', 1)
		self.needsRead=0

	def wait(self):
		"""Wait until transfer from AIM is done. This process is the bottleneck!"""
		while self.getProperty('.RDNG')=='1' or self.getProperty('.READ')=='1' :
			sleep(0.1)
			
	def getData(self):
		"""Transfer the data from EPICS to GDA"""
		return self.xxx.cagetArray()

	def atScanStart(self):
		"""Method used at the beginning of the scan, it stops and clears the MCA"""
		self.stop()
		self.erase()
#		self.start()
		self.channels = int(self.getProperty( '.NUSE' ))
		self.setOutputFormat( ['%.0f'] * self.channels )
		self.setExtraNames(['Counts'] * (self.channels-1) )
		
	def asynchronousMoveTo(self,newpos):
#		print "async move to ", newpos
		self.stop()
		self.erase()
		self.setProperty('.PRTM', newpos )
		self.start()
		while self.getProperty('.ACQG')=='0' :
			self.start()

	def isBusy(self):
		if  self.getProperty('.ACQG')=='1':
			self.needsRead=1
			return 1
		else:
			return 0
		
	def getPosition(self):
#		print self.getProperty('.ELTM')
		self.stop()
		if self.needsRead==1:
			self.read()
		self.wait()
		self.intdata=map(int,self.getData() )
	#	self.erase()
	#	self.start()
	
		return self.intdata
			

