from time import clock
import os
from gda.factory import Finder
from gda.device.scannable import PseudoDevice
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
from time import sleep
#
## These classes can be used for testing the scripts in detectorScanScripts 
#
class DummyMar:
	"""
	Used in testing. When status is switched from 1 back to 0 at end of a scan, a dummy file 
	is produced with the correct name plus the _001 suffix added by the mar software.
	"""
	def __init__(self, name, scanTime):
		self.name = name
		self.scanTime = scanTime
		self.t0 = 0

		self.actualMar = Finder.getInstance().find("Mar345Detector")
	
	def getDirectory(self):
		return self.actualMar.getDirectory()
	
	def setRootName(self, rootName):
		self.actualMar.setRootName(rootName)
	
	def getRootName(self):
		return self.actualMar.getRootName()
		
	def scan(self):
		status = self.getStatus()
		if (status == 0):
			simpleLog("DummyMar: command 'scan' sent")
			self.t0 = clock()
		elif (status == 1):
			simpleLog("DummyMar: 'scan' command not sent as status is busy")
		else:
			raise "DummyMar: invalid status: " + str(status)

	def getStatus(self):
		if ( (clock() - self.t0) > self.scanTime):
			os.system("touch " + self.getDirectory() + "/" + self.getRootName() + "_001.mar3450")
			return 0
		
		return 1
	
		
class SimpleDummyDetector(PseudoDevice):
	"""
	Dummy detector to be passed into scripts for testing
	"""
	def __init__(self):
		self.name = "dummyDetector"
		self.setName(self.name)
		self.exposureTime=0
		self.setInputNames(["Exposure"])
		self.setOutputFormat(["%6.4f", "%s"])
		self.setExtraNames(["File Number"])
		self.runNumber = -1
	def rawGetPosition(self):
		return [self.exposureTime, self.name+"_"+str(self.runNumber)+".img"]
	def rawIsBusy(self):
		return 0
	def rawAsynchronousMoveTo(self,position):
		self.exposureTime = position
		sleep(position)
		self.runNumber+=1

#############################
class SimpleDummyMotor(PseudoDevice):
	"""
	Dummy motor to be passed into scripts for testing
	"""
	def __init__(self):
		self.setName("dummyMotor")
		self.currentposition=0
	def isBusy(self):
		return 0
	def asynchronousMoveTo(self,newPosition):
		self.currentposition = newPosition
	def getPosition(self):
		return self.currentposition
	
