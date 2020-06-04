from gda.device.scannable import ScannableMotionBase

class McsWrapper(ScannableMotionBase):
	"""
	Designed to work closely within cvscan. All required EMCS methods are
	passed trhough to the raw EMCS. After a collection has been made and
	the EMCS stopped, calling prepareResults() will ready this scannable
	to be scanned (in a dummy way) to return the results.
	
	
	Calling prepareResults() will retrieve data from the EMCS, and put a pointer
	to the first bin. Each succesive call to getPosition will return a line
	counts for the configured channels.
	
	"""

	def __init__(self, name, mcs, channelList, nameList=None):
		'''channelList starts at 1, but the first channel is always added
		anyway as this is the time'''
		if 1 in channelList:
			raise Exception("Do not select channel 1. This is reserved for reading back the bin time.")
		self.name = name
		self.mcs = mcs
		self.channelList = channelList
		if nameList==None:
			nameList=[]
			for i in range(len(channelList)):
				nameList += ["ch" + str(channelList[i])]
		self.setExtraNames(['tbin'] + nameList)
		self.setInputNames([])
		self.setOutputFormat(['%.6f'] + ['%d']*len(channelList))
		self.setLevel(9)

	def isBusy(self):
		return False

	def getPosition(self):
		bin = self.results[self.aboutToReturnBin]
		self.aboutToReturnBin += 1
		return bin

	def asynchronousMoveTo(self,countTime):
		raise Exception("Not a real moveable scannable: designed for use only within cvscan fake-scans")

###

	def prepareResults(self, nbins):
		self.results=[]
		self.results.append(map(lambda x: x/50e6,self.mcs.getData(0)[0:nbins])) # get the ch1 time counts
		for channel in self.channelList:
			self.results.append(self.mcs.getData(channel-1)[0:nbins])
		# now transpose to get nbins rows of channel counts
		self.results=apply(zip,self.results)
		self.aboutToReturnBin = 0

###
	def prepareForCollection(self):
		return self.mcs.prepareForCollection()
	
	def collectData(self):
		return self.mcs.collectData()
	
	def stop(self):
		return self.mcs.stop()
