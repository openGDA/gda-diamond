from gda.device.scannable import ScannableMotionBase
from java.lang import String

class ScannableMotionBaseWithDottedAccess(ScannableMotionBase):
	'''This extended version of ScannableMotionBase contains a completeInstantiation() method
	which adds a dictionary of MotionScannableParts to an instance. Each part allows one of the
	instances fields to be interacted with like it itself is a scannable. Fields are dynamically 
	added to the instance linking to these parts allowing dotted access from Jython.  They may
	also be accessed using Jython container access methods (via the __getitem__() method).
	To acess them from Jave use the getComponent(name) method.
	
	When moving a part (via either a pos or scan command), the part calls the parent to perform
	the actual task.  The parts asynchronousMoveto command will call the parent with a list
	of None values except for the field it represents which will be passed the desired position
	value.
	
	The asynchronousMoveTo method in class that inherats from this base class then must handle
	these Nones.  In some cases the method may actually be able to move the underlying system
	assoiciated with one field individually from others. If this is not possible the best behaviour
	may be to simply not support this beahviour and exception or alternatively to substitute the
	None values with actual current position of parent's scannables associated fields.
	
	ScannableMotionBaseWithMemory() inherats from this calss and provides a solution useful
	for some scenarious: it keeps track of the last position moved to, and replaces the Nones
	in an asynchronousMoveTo request with these values. There are a number of dangers associated
	with this which are addressed in that class's documentation, but it provides a way to move
	one axis within a group of non-orthogonal axis while keeping the others still.
	'''
	


	def completeInstantiation(self):
		'''This method should be called at the end of all user defined consructors'''
		# self.validate()
		self.numInputFields = len(self.getInputNames())
		self.__addScannableParts()

	def __addScannableParts(self):
		'''Creates an array of MotionScannableParts each of which allows acces to the scannable's
		fields. See this class's documentation for more info.'''
		self.childrenDict = {}
		nameList = self.getInputNames()
		for i, name in enumerate(nameList):
			self.childrenDict[name] = self.MotionScannablePart(name, i, self)
		
		self.__dict__.update(self.childrenDict)

	def asynchronousMoveTo(self):
		'''Must take an array including Nones which will not be moved.'''
		raise Exception("Overide")

	def getPosition(self):
		raise Exception("Overide")
	
	def isBusy(self):
		raise Exception("Overide")
	
	def toString(self):
		result = ""
		for name in self.getInputNames():
			result += self.childrenDict[name].toString() + "\n"
		return result
		
#	def __getattr__(self, key):
#		'''Provides dotted access from Jython'''
#		if self.childrenDict.has_key(key):
#			return self.childrenDict[key]
#		else:
#			raise AttributeError, key	
		
	def __getitem__(self, key):
		'''Provides container like access from Jython'''
		return self.childrenDict[key]
	
	def getPart(self, name):
		'''Returns the a compnent scannable'''
		return self.childrenDict[name]
	
	def __fillPosition(self, position):
		'''If position contains any null or None values, these are replaced with the
		corresponding fields from the scannables current position and then returned.'''
		# Just return position if it does not need padding
		if None not in position:
			return position	
		currentPosition = self.getPosition()[:self.numInputFields]
		for i in range(self.numInputFields):
			if position[i] == None:
				position[i] = currentPosition[i]
				
	# (internal class!)
	class MotionScannablePart(ScannableMotionBase):
		'''A scannable to be placed in the parent's childrenDict that allows access to the
		parent's individual fields.'''
	
		def __init__(self, scannableName, index, parentScannable):
			self.setName(scannableName)
			self.setInputNames([scannableName])
			self.setOutputFormat([parentScannable.getOutputFormat()[index]])
			self.index = index
			self.parentScannable = parentScannable
			
		def isBusy(self):
			return self.parentScannable.isBusy()

		def asynchronousMoveTo(self,new_position):
#			if self.parentScannable.isBusy():
#				raise Exception, self.parentScannable.getName() + "." + self.getName() + " cannot be moved because " + self.parentScannable.getName() + " is already moving"
			toMoveTo=[None] * len(self.parentScannable.getInputNames())
			toMoveTo[self.index] = new_position
			self.parentScannable.asynchronousMoveTo(toMoveTo)

		def simulateMoveTo(self, new_position):
			toMoveTo=[None] * len(self.parentScannable.getInputNames())
			toMoveTo[self.index] = new_position
			return self.parentScannable.simulateMoveTo(toMoveTo)
		
		def getPosition(self):
			return self.parentScannable.getPosition()[self.index]
	
#		def toString(self):
#			name = self.getInputNames()[0]
#			return self.parentScannable.getName() + "." + name + " : " + str(self.getPosition())
	
		def getLowerGdaLimits(self):
			limList=self.parentScannable.getLowerGdaLimits()
			if limList==None:
				return None
			else:
				return [ limList[self.index] ]
		
		def getUpperGdaLimits(self):
			limList=self.parentScannable.getUpperGdaLimits()
			if limList==None:
				return None
			else:
				return [ limList[self.index] ]
		
		def setLowerGdaLimits(self, value):
			if type(value) in ('list','tuple'):
				value = value[0]
			lim = self.parentScannable.getLowerGdaLimits()
			if lim == None:
				lim = [None]*self.parentScannable.numInputFields
			lim = list(lim)
			lim[self.index] = value
			self.parentScannable.setLowerGdaLimits(lim)
			
		def setUpperGdaLimits(self, value):
			if type(value) in ('list','tuple'):
				value = value[0]
			lim = self.parentScannable.getUpperGdaLimits()
			if lim == None:
				lim = [None]*self.parentScannable.numInputFields
			lim = list(lim)				
			lim[self.index] = value
			self.parentScannable.setUpperGdaLimits(lim)			
		
		def toString(self):
			format = "%-6s : "  + self.getOutputFormat()[0]
			output = format % (self.getName(), self.getPosition())
			lowerLimSet = False
			upperLimSet = False
			if self.getLowerGdaLimits() != None:
				if self.getLowerGdaLimits()[0] != None:
					lowerLimSet = True
			if self.getUpperGdaLimits() != None:
					if self.getUpperGdaLimits()[0] != None:
						upperLimSet = True
			if (lowerLimSet | upperLimSet):
				output += " gda("
				if lowerLimSet:
					output += str(self.getLowerGdaLimits()[0])
				else:
					output += " "
				output += " : "
				if upperLimSet:
					output += str(self.getUpperGdaLimits()[0])
				else:
					output += " "
				output += ")"
			
			return output