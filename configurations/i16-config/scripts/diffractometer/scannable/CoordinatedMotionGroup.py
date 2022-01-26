from ScannableMotionBaseWithDottedAccess import ScannableMotionBaseWithDottedAccess

class CoordinatedMotionGroup(ScannableMotionBaseWithDottedAccess):

	def __init__(self, name, scnList, fieldNames):
		"""
		"""
		# Check input
		if len(scnList)!=len(fieldNames):
			raise ValueError("length of componentScannables (%d) and inputFieldNames (%d) must match"%
							(len(scnList), len(fieldNames)) )
		
		# Setup scannable
		self.setName(name)
		self.setInputNames(fieldNames)
		outputFormat = []
		for scn in scnList:
			outputFormat.append(scn.getOutputFormat()[0])
		self.setOutputFormat(outputFormat)		
		
		# Coordinated motion stuff
		self.scnList = scnList
		self.scnNames = fieldNames # In order
		self.scnDict = {}
		self.scnEnabledDict = {}
		for (i,scnName) in enumerate(self.scnNames):
			self.scnDict[scnName] = self.scnList[i]
			self.scnEnabledDict[scnName] = True

		# Make the dotted access work
		self.completeInstantiation()

	def asynchronousMoveTo(self, dest):
		self.checkDestination(dest)
		# Move the axes (order is important to avoid collisions)
		for scn, name, scndest in zip(self.scnList, self.scnNames, dest):
			try:
				if scndest != None:
					if self.scnEnabledDict[name]:
						#print "%s.asynchMoveTo(%f)" % (scn.getName(), scndest)
						scn.asynchronousMoveTo(scndest)
					else:
						print "AXIS DISABLED: %s.asynchMoveTo(%f) NOT performed" % (scn.getName(), scndest)
			except Exception, e:
				self.stop()
				raise e

	def isBusy(self):
		'''Returns true if any component scannable's are busy.'''
		for scn in self.scnList:
			if scn.isBusy():
				return 1
		return 0

	def getPosition(self):
		result = []
		for scn in self.scnList:
			pos = scn.getPosition()
			result.append( float(pos) )
		return result

	def stop(self):
		# Stop motors and turn off defer flag
		for scn in self.scnList:
			scn.stop()

	def atScanStart(self):
		s = ''
		for name, enabled in self.scnEnabledDict.items():
			if not enabled:
				s += name + ', '
		if s != '':
			print "WARNING: In %s axes %s are disabled" % (self.getName(), s[:-2])

	def atScanEnd(self):
		self.atScanStart()
		
	def checkDestination(self, dest):
	# Check input length
		if len(dest)!=self.numInputFields:
			raise ValueError("Move not performed: this scannable has %d fields but its asynchrnousMoveTo() method was called with %d"%(self.numInputFields, len(dest)) )
	
		# Check all axes to be moved are inside limits
		for scn, scn_dest in zip(self.scnList, dest):
			if scn_dest != None:
				if scn.checkPositionValid(scn_dest):
					raise RuntimeError, "\nMove not performed because: \n" + scn.checkPositionValid(scn_dest)
	
# Limits, note that the limits are stored in the component motors
	def getLowerGdaLimits(self):
		result=[]
		for scn in self.scnList:
			lim = scn.getLowerGdaLimits()
			if lim is None:
				result.append(None)
			else:
				result.append(lim[0])
		return result
	
	def getUpperGdaLimits(self):
		result=[]
		for scn in self.scnList:
			lim = scn.getUpperGdaLimits()
			if lim is None:
				result.append(None)
			else:
				result.append(lim[0])
		return result
	
	def setLowerGdaLimits(self, value):
		if type(value) in ('list','tuple'):
			value = value[0]
		if len(value)!=self.numInputFields:
			raise ValueError("Limits not changed: this scannable has %d fields but its setLowerGdaLimits() method was called with %d"%(self.numInputFields, len(value)) )
		for i, scn in enumerate(self.scnList):
			scn.setLowerGdaLimits(value[i])
		
	def setUpperGdaLimits(self, value):
		if type(value) in ('list','tuple'):
			value = value[0]
		if len(value)!=self.numInputFields:
			raise ValueError("Limits not changed: this scannable has %d fields but its setUpperGdaLimits() method was called with %d"%(self.numInputFields, len(value)) )
		for i, scn in enumerate(self.scnList):
			scn.setUpperGdaLimits(value[i])
	
	def getComponent(self, name):
		'''Returns the a component scannable'''
		return self.scnList[name]
	
	def enable(self, name):
		self.scnEnabledDict[name] = True
		
	def disable(self, name):
		self.scnEnabledDict[name] = True
