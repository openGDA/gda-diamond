from gdascripts.scannable.epics.PvManager import PvManager
from gda.data import NumTracker

from time import sleep
from gda.device.detector import DetectorBase
from gda.device.Detector import BUSY, IDLE
import os

# test = ScanFileContainer()
# test.loadPilatusData("/dls/i16/data/Pilatus/test1556.tif")
# test.plot()
# matrix = test.getImage().doubleMatrix()


class EpicsAreaDetector(DetectorBase):
	
	def __init__(self, name, pvroot, numtrackerstring, fileformat, shutterTrigger = None):
		self.name = name
		self.inputNames = ['ExposureTime']
		self.extraNames = ['FileNum']
		self.outputFormat = ['%.4f', '%s']
		self.level = 9
		
		self.filepath = None
		self.numTracker = NumTracker(numtrackerstring)
		self.lastSetAcquireTime = 0
		self.formatString = None
		self.shutterTrigger = shutterTrigger

		self.pvs = PvManager(['FilePath','FilePath_RBV', 'AndorFileFormat', 'AcquireTime', 'AcquireTime_RBV', 'ImageMode', 'AndorADCSpeed', 'MinX', 'MinY', 'SizeX', 'SizeY', 'Acquire', 'Temperature', 'Temperature_RBV','TriggerMode', 'DetectorState_RBV', 'NumImages', 'FileName', 'FileNumber', 'FileName_RBV', 'FileNumber_RBV'], pvroot)	
		self.configure(fileformat)

	def configure(self, fileformat):
		self.pvs.configure()
		self.setTriggerMode('Internal')
		self._setImageMode('Single')
		self._setNumImages(1)
		self._setAndorAdcSpeed(2.5) #MHz
		self.setFileFormat(fileformat)

	def setFilepath(self, filepath):
		self.filepath=filepath
		if not os.path.exists(filepath):
			os.makedirs(filepath)

	def setFileFormat(self, formatString):
		self._setAndorFileFormat(formatString)
		self.formatString = formatString.lower()

# DETECTOR INTERFACE
	def createsOwnFiles(self):
		return True

	def setCollectionTime(self, t):
		self._setAcquireTime(t)
	
	def getCollectionTime(self):
		return self._getAcquireTime()
	
	def collectData(self):
		self.numTracker.incrementNumber();
		# Bug fix by RW on 2/4/12
		# must set the FilePath and FileName PVs manually
		# only set the folder name in the filepath PV
		self._setFilePath(self.filepath)# + '/' + self._generateFileName())
		# set the file number PV
		self.pvs['FileNumber'].controller.caputWait(self.pvs['FileNumber'].channel, self.numTracker.getCurrentFileNumber())
		
		if self.shutterTrigger:
			self.shutterTrigger(0)
		self._triggerAcquire()
		sleep(.5)
		if self.shutterTrigger:
			self.shutterTrigger(1)
			self.waitWhileBusy()
			self.shutterTrigger(0)
# commented out by RW 2/4/12	
#	def _generateFileName(self):
#		return str(self.numTracker.getCurrentFileNumber()) + '.' + self.formatString
	
	def getStatus(self):
		if self._isAcquiring():
			return BUSY
		else:
			return IDLE
	
	def readout(self):
		# file prefix
		prefix = self._getFilePrefix()
		# file number
		number = self.pvs['FileNumber_RBV'].caget()
		# file suffix
		suffix = ".tif"
		return self._getFilePath() + str(prefix) + str(number) + suffix

	def _getFilePrefix(self):
		byteArray = self.pvs['FileName_RBV'].cagetArrayByte()
		byteList = byteArray.tolist()
		byteList = byteList[0:byteList.index(0)]
		return ''.join([chr(b) for b in byteList])


# SCANNABLE INTERFACE (currently used by pos but not scan ??)

	def stop(self):
		self._stop()

	def getPosition(self):
		return [self._getAcquireTime(), self.readout()]

	def asynchronousMoveTo(self, t):
		self.setCollectionTime(t)
		self.collectData()

# ANDOR COMMANDS

	def _setAndorAdcSpeed(self, speedMhz):
		self.pvs['AndorADCSpeed'].caput({0.05: 0, 2.5:1}[speedMhz])
		
	def _setAndorFileFormat(self, formatString):
		self.pvs['AndorFileFormat'].caput({'TIFF':0, 'BMP':1, 'SIF':2, 'EDF':3, 'RAW':4, 'TEXT':5 }[formatString.upper()])

# AREA DETECTOR COMMANDS

	# Note: Command appended where name already taken
	def setTriggerMode(self, modestring):
		self.pvs['TriggerMode'].caput({'Internal': 0, 'External':1}[modestring])
		
	def _setImageMode(self, imagestring):
		self.pvs['ImageMode'].caput({'Single':0, 'Multiple':1, 'Continuous':2}[imagestring])
		
	def _setNumImages(self, num):
		self.pvs['NumImages'].caput(num)
		
	def _setAcquireTime(self, t):
		self.pvs['AcquireTime'].caput(t)
#		self.lastSetAcquireTime = t
		
	def _getAcquireTime(self):
		return float(self.pvs['AcquireTime_RBV'].caget())
	
	def _setFilePath(self, path):
		self.pvs['FilePath'].controller.caputWait(self.pvs['FilePath'].channel, [ord(letter) for letter in path])
		
	def _getFilePath(self):
		byteArray = self.pvs['FilePath_RBV'].cagetArrayByte()
		byteList = byteArray.tolist()
		byteList = byteList[0:byteList.index(0)]
		return ''.join([chr(b) for b in byteList])
	
	def setMinX(self, minx):
		self.pvs['MinX'].caput(minx)
		
	def setMinY(self, minx):
		self.pvs['MinY'].caput(minx)

	def setSizeX(self, minx):
		self.pvs['SizeX'].caput(minx)
		
	def setSizeY(self, minx):
		self.pvs['SizeY'].caput(minx)
		
	def setTemperature(self, t):
		self.pvs['Temperature'].caput(t)
		
	def getTemperature(self):
		return float(self.pvs['Temperature_RBV'].caget())
	
	def _triggerAcquire(self):
		self.pvs['Acquire'].caput(1)
		
	def _isAcquiring(self):
		return int(float(self.pvs['Acquire'].caget())) # not tRBV as there is potential for a race condition
	
	def _stop(self):
		self.pvs['Acquire'].caput(0)

