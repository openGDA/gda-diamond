from gda.device.scannable import PseudoDevice
from gdascripts.pd.time_pds import tictoc
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from os import popen
import gda

class UlriksSyncScan(PseudoDevice):
	'''Simply wraps a monitor so it apperas as a regular scannable, and is hence
	moved in scans.'''
	
	def __init__(self):
		self.directory = InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir")
		self.name = 'ionsync'
		self.setInputNames(['time'])
		self.setExtraNames(['pointno'])
		self.setOutputFormat(['%.2f','%f'])
		self.setLevel(9)
		
		self.timer=tictoc()
		self.waitfortime=0
		self.currenttime=0
		
		self.fileprefix = 'ionsync_scan'
		self.pointnumber=-1	
		self.scannumber=-1
		self.scanno=NumTracker("tmp")
		self.inscan = False
		
	def atScanStart(self):
		self.pointnumber=0
		self.scannumber = self.scanno.getCurrentFileNumber() + 1
		self.inscan = True
		

	def isBusy(self):
		if self.timer()<self.waitfortime:
			return 1
		else:
			return 0

	def asynchronousMoveTo(self,waittime):
		if self.inscan == False:
			raise Exception("ionsync must be operated in a scan")
		waittime = 11
		self.currenttime=self.timer()
		self.waitfortime=self.currenttime+waittime
		self.pointnumber = self.pointnumber + 1
		print self.directory + "/" + self.fileprefix + str(self.scannumber) + "_" + str(self.pointnumber) + "-1.csv" 

		popen("export EPICS_CA_MAX_ARRAY_BYTES=10000000; /dls_sw/tools/bin/python2.4 /dls_sw/b16/scripts/syncscan.py " + self.directory + "/" + self.fileprefix + str(self.scannumber) + "_" + str(self.pointnumber) + " 1")

	def getPosition(self):
		return (10,self.pointnumber)
	
	def atScanEnd(self):
		self.inscan = False