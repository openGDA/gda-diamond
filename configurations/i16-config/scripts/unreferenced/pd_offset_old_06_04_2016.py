from uk.ac.diamond.daq.persistence.jythonshelf import LocalJythonShelfManager
from gda.device.scannable import ScannableMotionBase

import ShelveIO
import installation

# Offset scannables save and load single values to persistant storage.
# Note 
class Offset(ScannableMotionBase):
	'''Offset scannables save and load single values to persistant storage.
	
	'''
	def __init__(self,name, scannableToOffset=None):
		self.setName(name)
		self.setInputNames([name])
		# <old shelf>
		self.offsetShelf=ShelveIO.ShelveIO()
		self.offsetShelf.path=ShelveIO.ShelvePath+'offset'
		self.offsetShelf.setSettingsFileName('offset')
		# <new shelf>
		self.newshelf=LocalJythonShelfManager.open("offsets")
		self.label=0

		self.scannableToOffset = scannableToOffset
		if self.scannableToOffset:
			self.applyCurrentOffsetToScannable()
		
	def applyCurrentOffsetToScannable(self):
		if self.scannableToOffset == None:
			raise Exception(self.name + ": Error applying current offset: No scannable-to-offset has been configured")
		toset = self.getPosition()
		self.scannableToOffset.setOffset(float(toset) if toset else None)

	def asynchronousMoveTo(self,position):
		self.label=1
		# <old shelf >
#		try:
		self.offsetShelf.ChangeValue(str(self.getName()),position)
#		except:
#			print "Caught exception saving '%s' offset='%s' to old shelf (this is only a backup system)" % (self.getName(), position)
		# < new shelf >
		self.newshelf[self.getName()]=position
		if self.scannableToOffset:
			print `self.scannableToOffset` + " -->"
			self.applyCurrentOffsetToScannable()
			print `self.scannableToOffset`
		

	def getPosition(self):
		if installation.loadOldShelf():
			# <old shelf >
			return self.offsetShelf.getValue(self.getName())
		else:
			# <new shelf>
			return self.newshelf.getValue(self.getName(), None) # None if not is dbase yet

	def isBusy(self):
		return 0


class OffsetDualScannable(ScannableMotionBase):
	def __init__(self, name, scannablesToOffset = None):
		self.name = name
		self.inputNames = [name]
		# <old shelf>
		self.offsetShelf=ShelveIO.ShelveIO()
		self.offsetShelf.path=ShelveIO.ShelvePath+'offset'
		self.offsetShelf.setSettingsFileName('offset')
		# <new shelf>
		self.newshelf=LocalJythonShelfManager.open("offsets")
		self.label=0

		self.scannables = scannablesToOffset
		if len(self.scannables) > 0:
			self.applyOffsets()

	def applyOffsets(self):
		offset = self.getPosition()
		for scannable in self.scannables:
			scannable.setOffset(float(offset) if offset else None)

	def asynchronousMoveTo(self,position):
		self.label=1
		# <old shelf >
#		try:
		self.offsetShelf.ChangeValue(str(self.getName()),position)
#		except:
#			print "Caught exception saving '%s' offset='%s' to old shelf (this is only a backup system)" % (self.getName(), position)
		# < new shelf >
		self.newshelf[self.getName()]=position
		if self.scannables:
			print `self.scannables` + " -->"
			self.applyOffsets()
			print `self.scannables`

	def getPosition(self):
		if installation.loadOldShelf():
			# <old shelf >
			return self.offsetShelf.getValue(self.getName())
		else:
			# <new shelf>
			return self.newshelf.getValue(self.getName(), None) # None if not is dbase yet

	def isBusy(self):
		return 0
