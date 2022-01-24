from java.lang import IllegalArgumentException

from gda.factory import Finder

COLLECT_MODE = ['normal','time-resolved']
IMAGE_MODE = ['Single','Multiple','Continuous']
TRIGGER_MODE = ['Internal', 'Ext. Enable', 'Ext. Trigger', 'Mult. Trigger','Alignment']

class CollectionMode():

	def __init__(self):
		self.modeIndexer = Finder.find("dc_mode_index")
		self.imageMode = Finder.find("dc_imageMode")
		self.triggerMode = Finder.find("dc_triggerMode")
		self.numImages = Finder.find("dc_numImages")
		self.numExposures = Finder.find("dc_numExposures")
		self.acquireTime = Finder.find("dc_acquireTime")
		self.acquirePeriod = Finder.find("dc_acquirePeriod")
		self.start = Finder.find("dc_start")
		self.userHeaderStep = 0.0
		self.numExposuresPerHatrix = 1

	def _configMode(self, modeIndex):
		if modeIndex == 0: # normal
			self.setNumExposuresPerImage(1)
			self.imageModeSingle()
			self.triggerModeExtTrigger()
			return
		if modeIndex == 1: # time-resolved
			self.triggerModeExtEnable()
			return

	def _getModeIndex(self):
		return int(round(self.modeIndexer.getPosition()))

	def _setModeIndex(self,index):
		self.modeIndexer.asynchronousMoveTo(float(index))

	def _setImageModeByIndex(self,index):
		try:
			if index >=0 and index < len(IMAGE_MODE):
				self.imageMode.asynchronousMoveTo(index)
			else:
				raise IllegalArgumentException
		except:
			print "Unable to set image mode (%s)" % str(index)
			self.showImageModes()
		finally:
			print "Image Mode is set to '%s'" % self.getImageMode()

	def _setTriggerModeByIndex(self,index):
		try:
			if index >=0 and index < len(TRIGGER_MODE):
				self.triggerMode.asynchronousMoveTo(index)
				if index != 1:
					self.setNumExposuresPerImage(1)
			else:
				raise IllegalArgumentException
		except:
			print "Unable to set trigger mode (%s)" % str(index)
			self.showTriggerModes()
		finally:
			print "Trigger Mode is set to '%s'" % self.getTriggerMode()

	def getImageMode(self):
		mode = self.imageMode.getPosition().lower()
		for imode in IMAGE_MODE:
			if mode == imode.lower():
				return imode
		return mode
		
	def getAcquirePeriod(self):
		return self.acquirePeriod.getPosition()

	def getAcquireTime(self):
		return self.acquireTime.getPosition()

	def getNumExposuresPerHatrx(self):
		return self.numExposuresPerHatrix

	def getNumExposuresPerImage(self):
		return self.numExposures.getPosition()

	def getNumImages(self):
		return self.numImages.getPosition()

	def getMode(self):
		return COLLECT_MODE[self._getModeIndex()]

	def getTriggerMode(self):
		mode = self.triggerMode.getPosition().lower()
		for tmode in TRIGGER_MODE:
			if mode == tmode.lower():
				return tmode

	def getUserHeaderStep(self):
		return self.userHeaderStep

	def help(self):
		lines = []
		lines.append("Use 'dcmode.method()' for control over Data Collection Mode where method() is one of:")
		lines.append("\tsetMode(mode) for Collection Mode: mode is 'n' for normal, 't' for time-resolved")
		lines.append("\tCollection Mode currently: '%s'\n" % self.getMode())

		lines.append("\timageModeSingle()")
		lines.append("\timageModeMultiple()")
		lines.append("\timageModeContinuous()")
		lines.append("\tImage Mode currently: '%s'\n" % self.getImageMode())

		lines.append("\ttriggerModeInternal()")
		lines.append("\ttriggerModeExtEnable()")
		lines.append("\ttriggerModeExtTrigger()")
		lines.append("\ttriggerModeMultTrigger()")
		lines.append("\ttriggerModeAlignment()")
		lines.append("\tTrigger Mode currently: '%s'\n" % self.getTriggerMode())

		lines.append("\tsetNumExposuresPerImage(number)   \tcurrently %d" % self.getNumExposuresPerImage())
		lines.append("\tsetNumImages(number)      \tcurrently %d" % self.getNumImages())
		lines.append("\tsetAcquireTime(seconds)   \tcurrently %5.3f s" % self.getAcquireTime())
		lines.append("\tsetAcquirePeriod(seconds) \tcurrently %5.3f s" % self.getAcquirePeriod())
		
		lines.append("\tsetUserHeaderStep(degrees) \tcurrently %5.3f s" % self.getUserHeaderStep())

		message = '\n'.join(lines)
		print message

	def imageModeContinuous(self):
		self._setImageModeByIndex(2)
		
	def imageModeMultiple(self):
		self._setImageModeByIndex(1)

	def imageModeSingle(self):
		self._setImageModeByIndex(0)

	def setAcquirePeriod(self, value):
		return self.acquirePeriod.asynchronousMoveTo(value)

	def setAcquireTime(self, value):
		return self.acquireTime.asynchronousMoveTo(value)

	def setCollectionModeNormal(self):
		self.setMode('n')

	def setNumExposuresPerHatrx(self, value):
		self.numExposuresPerHatrix = value

	def setNumExposuresPerImage(self, value):
		if self.getTriggerMode() == TRIGGER_MODE[1]:
			return self.numExposures.asynchronousMoveTo(value)
		else:
			print "Can only set number of Exposures/Image with trigger mode set to 'Ext.Enable'"
			print "Current trigger mode: '%s'" % self.getTriggerMode()
			print "Current number exposures per image: '%s'" % self.getNumExposuresPerImage()

	def setNumImages(self, value):
		return self.numImages.asynchronousMoveTo(value)

	def setmode(self,mode=""):
		self.setMode(mode)

	def setMode(self,mode=""):
		index = -1
		try:
			if len(mode) > 0:
				for i in range(0,2):
					if mode[0:1].lower() == COLLECT_MODE[i][0:1]:
						index = i
						break;
				if index >= 0:
					self._setModeIndex(index)
					self._configMode(index)
				else:
					print "Unable to set invalid collection mode"
			else:
				self.showModes()
		except:
			print "Unable to set collection mode"
		finally:
			print "Data Collection mode is set to '%s'" % self.getMode()
	
	def setUserHeaderStep(self,value):
		self.userHeaderStep = value
		
	def show(self):
		print self.toString()

	def showImageModes(self):
		print "Image Modes:"
		for i,mode in zip(range(0,len(IMAGE_MODE)),IMAGE_MODE):
			print "\t%d: '%s'" % (i,mode)

	def showModes(self):
		print "Collection Modes:"
		for i,mode in zip(range(0,len(COLLECT_MODE)),COLLECT_MODE):
			print "\t%d: '%s'" % (i,mode)

	def showTriggerModes(self):
		print "Trigger Modes:"
		for i,mode in zip(range(0,len(TRIGGER_MODE)),TRIGGER_MODE):
			print "\t%d: '%s'" % (i,mode)

	def triggerModeInternal(self):
		self._setTriggerModeByIndex(0)

	def triggerModeExtEnable(self):
		self._setTriggerModeByIndex(1)

	def triggerModeExtTrigger(self):
		self._setTriggerModeByIndex(2)

	def triggerModeMultTrigger(self):
		self._setTriggerModeByIndex(3)

	def triggerModeAlignment(self):
		self._setTriggerModeByIndex(4)

	def toString(self):
		lines = []
		lines.append("'dcmode' for control over Data Collection Mode:")
		lines.append("\tCollection Mode: %s" % self.getMode())
		lines.append("\tImage Mode: %s" % self.getImageMode())
		lines.append("\tTrigger Mode: %s" % self.getTriggerMode())
		lines.append("\t# Exposures/Image: %d" % self.getNumExposuresPerImage())
		lines.append("\t# Images: %d" % self.getNumImages())
		lines.append("\tAcquire Time (s) (Exposure): %5.3f s" % self.getAcquireTime())
		lines.append("\tAcquire Period (s): %5.3f s" % self.getAcquirePeriod())
		if self.getMode() == COLLECT_MODE[1]:
			lines.append("\tUser Header Step (deg): %5.3f s" % self.getUserHeaderStep())
		return '\n'.join(lines)

	def __call__(self):
		print self.toString()

