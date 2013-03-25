from time import sleep
from gda.device.scannable import PseudoDevice

class DummyMotor(PseudoDevice):
	
	def __init__(self):
		self.setName("dummyMotor")
		self.setInputNames(["Motor Position"])
		self.setOutputFormat(["%6.4f"])
		self.currentposition=0
	def isBusy(self):
		return 0
	def asynchronousMoveTo(self,newPosition):
		self.currentposition = newPosition
	def getPosition(self):
		return self.currentposition

class DummyPilatusWrapper(PseudoDevice):
	
	def __init__(self, detector=None, exposureTime=0, axis=None, step=None, sync=False, fileName="dummyPilatus", exposureNo=0, noOfExpPerPos=1):
		self.name = "dummyPilatus"
		self.setName(self.name)
		self.setInputNames(["Exposure Time"])
		self.setOutputFormat(["%6.4f", "%s"])
		self.setExtraNames(["File Name"])
		self.scanNumber = 0
		self.exposureTime = 0
		self.exposureNo = exposureNo
		self.noOfExpPerPos = noOfExpPerPos
		self.fullFileName = ""
		self.dir = "/dls/i15/data/2009/0-0/"
		
	def rawGetPosition(self):
		return [self.exposureTime, self.files]
	
	def rawIsBusy(self):
		return 0
	
	def rawAsynchronousMoveTo(self, position):
		
		self.files = []
		
		
		for exp in range(self.noOfExpPerPos):
			self.exposureNo+=1
			self.exposureTime = position
			sleep(position)
			self.fullFileName = self.dir + self.name+"_"+str(self.exposureNo)+".tif"
			open(self.fullFileName, 'w')
			self.files.append(self.fullFileName)
			
		
class DummyMarWrapper(PseudoDevice):
	def __init__(self, detector=None, exposureTime=0, axis=None, step=None, sync=False, fileName="dummyMar", exposureNo=0, noOfExpPerPos=1):
		self.name = fileName
		self.setName(self.name)
		self.setInputNames(["Exposure Time"])
		self.setOutputFormat(["%6.4f", "%s"])
		self.setExtraNames(["File Name"])
		self.exposureNo = exposureNo
		self.exposureTime = exposureTime
		self.noOfExpPerPos = noOfExpPerPos
		self.fullFileName = ""
		self.files = []
		
	def rawGetPosition(self):
		return [self.exposureTime, self.files]
	
	def rawIsBusy(self):
		return 0
	
	def rawAsynchronousMoveTo(self,position):
		
		self.files = []
		self.exposureNo+=1
		
		for exp in range(self.noOfExpPerPos):
			self.exposureTime = position
			sleep(position)
			self.fullFileName = "/dls/i15/data/2009/0-0/"+self.name+"_"+str(self.exposureNo)+"_"+str(exp+1)+".mar3450"
			self.files.append(self.fullFileName)
			open(self.fullFileName, 'w')


class DummyAtlasWrapper(DummyRubyWrapper):
	def __init__(self, detector=None, exposureTime=0, axis=None, step=None, sync=False, fileName="dummyMar", exposureNo=0, noOfExpPerPos=1):
		DummyRubyWrapper.__init__(self, detector, exposureTime, axis, step, sync, fileName, exposureNo, noOfExpPerPos)

	
class DummyRubyWrapper(PseudoDevice):
	def __init__(self, detector=None, exposureTime=0, axis=None, step=None, sync=False, fileName="dummyMar", exposureNo=0, noOfExpPerPos=1):
		self.name = fileName
		self.setName(self.name)
		self.setInputNames(["Exposure Time"])
		self.setOutputFormat(["%6.4f", "%s"])
		self.setExtraNames(["File Name"])
		self.exposureNo = exposureNo
		self.scanNo = 0
		self.exposureTime = exposureTime
		self.noOfExpPerPos = noOfExpPerPos
		self.fullFileName = ""
		self.files = []
		
	def rawGetPosition(self):
		return [self.exposureTime, self.files]
	
	def rawIsBusy(self):
		return 0
	
	def rawAsynchronousMoveTo(self,position):
		
		self.files = []
		self.scanNo+=1
		
		for exp in range(self.noOfExpPerPos):
			self.exposureTime = position
			sleep(position)
			self.fullFileName = "/dls/i15/data/2009/0-0/"+self.name+"_"+str(self.scanNo)+"_"+str(exp+1)+".mar3450"
			self.files.append(self.fullFileName)
			open(self.fullFileName, 'w')