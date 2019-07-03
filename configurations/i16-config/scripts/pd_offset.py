# modified with optional warnings 6/4/16; previous file saved separately with date

from uk.ac.diamond.daq.persistence.jythonshelf import LocalJythonShelfManager
from gda.device.scannable import PseudoDevice
from org.slf4j import LoggerFactory

import ShelveIO
import installation

# Offset scannables save and load single values to persistant storage.
# Note 
class Offset(PseudoDevice):
	'''
	Offset scannables save and load single values to persistant storage.
	use warningIfChangeGreaterThan keyword to specify the largest allowed change without a warning
	'''
	def __init__(self,name, scannableToOffset=None, warningIfChangeGreaterThan=None):
		self.logger = LoggerFactory.getLogger("Offset:"+name)

		self.setName(name)
		self.setInputNames([name])
		self.warn=warningIfChangeGreaterThan
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
		try:
			oldposition=self.getPosition()
			if not self.warn==None:
				if abs(position-oldposition)>self.warn:
					print "=== xxx === WARNING: YOU HAVE MADE A LARGER-THAN-EXPECTED CHANGE TO %s\n=== xxx === Old value: %g\n=== xxx === New value: %g" % (self.getName(), oldposition, position)
		except:
			print "=== There was a problem checking the previous value of this offset\n=== This is OK if it is a new device"

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
			self.logger.debug("getPosition() returning {}", self.offsetShelf.getValue(self.getName()))
			return self.offsetShelf.getValue(self.getName())
		else:
			# <new shelf>
			self.logger.debug("getPosition() returning {}", self.newshelf.getValue(self.getName(), None))
			return self.newshelf.getValue(self.getName(), None) # None if not is dbase yet

	def isBusy(self):
		return 0


class OffsetDualScannable(PseudoDevice):
	def __init__(self, name, scannablesToOffset = None):
		self.logger = LoggerFactory.getLogger("OffsetDualScannable:"+name)

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
			self.logger.debug("getPosition() returning {}", self.offsetShelf.getValue(self.getName()))
			return self.offsetShelf.getValue(self.getName())
		else:
			# <new shelf>
			self.logger.debug("getPosition() returning {}", self.newshelf.getValue(self.getName(), None))
			return self.newshelf.getValue(self.getName(), None) # None if not is dbase yet

	def isBusy(self):
		return 0
