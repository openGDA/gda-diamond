from gda.device.scannable import ScannableMotionBase
from gda.device.detector.analyser import EpicsMCAPresets

class Roi:
	def __init__(self, index, label, low, high):
		self.index = index
		self.label = label
		self.low = low
		self.high = high	
	def __str__(self):
		return "%-2d %-8s %-4d %-4d" % (self.index, self.label, self.low, self.high) 

class EpicsMcaHardwareRoiWrapper(ScannableMotionBase):
	
	def __init__(self, name, mca, countType):
		
		assert(countType=='net' or countType=='gross' or countType=='fancy','countType must be net, gross or fancy')
		self.name = name
		self.mca = mca
		self.countType = countType
		self.setInputNames(["livetime"])
		self.configure()
		self.setLevel(9)

	def isBusy(self):
		return self.mca.isBusy()

	def getPosition(self):
		self.configure()
		livetime = self.mca.getPresets().getPresetLiveTime()
		if self.countType=='net':
			return [livetime] + self.__getNetCounts()
		elif self.countType=='gross':
			return [livetime] + self.__getGrossCounts()
#		elif self.countType=='fancy':
#			return [livetime] + self.__getFancyNetCounts()
		else:
			assert(0,'countType must be net or gross')

	def __getGrossCounts(self):
		# Assumes object has been configured
		countArrays = self.mca.getRegionsOfInterestCount() # [index][0:gross, 1:net]
		grosscounts = []		
		for roi in self.rois:
			grosscounts += [ countArrays[roi.index][0] ]
		return grosscounts
	
	def __getNetCounts(self):
		# Assumes the object has been configured
		countArrays = self.mca.getRegionsOfInterestCount() # [index][0:gross, 1:net]		
		netcounts = []		
		for roi in self.rois:
			netcounts += [ countArrays[roi.index][1] ]
		return netcounts

#	def __getFancyNetCounts(self):
#		# Get the gross counts
#		countArrays = self.mca.getRegionsOfInterestCount() # [index][0:gross, 1:net]
#		spectrum = self.mca.readout().tolist()
#		netcounts = []
#		for roi in self.rois:
#			grosscounts = countArrays[roi.index][0]
#			estimatednoise = (roi.high - roi.low)*(spectrum[int(roi.high)]+spectrum[int(roi.low)])/2
#			netcounts += [grosscounts-estimatednoise]
#		return netcounts

	def asynchronousMoveTo(self,livetime):
		self.configure()
		self.mca.setPresets( EpicsMCAPresets(0,float(livetime),0,0,0,0) )
		self.mca.eraseStartAcquisition()

	def configure(self):
		'''Reads the hardware ROI configuration from the live epicsmca, and configures
		the objects extra fields to match.'''
		roilist = self.mca.getRegionsOfInterest()
		# if statement added by zjt21856 on 2008-09-09
		if roilist==None:
			roilist=[]
		extraNames = []
		self.rois = []
		for roi in roilist:
			if roi.getRegionName()!='':
				label = roi.getRegionName()
			else:
				label = 'roi' + str(roi.getRegionIndex())
			extraNames += [label]
			self.rois += [Roi(roi.getRegionIndex(), label, roi.getRegionLow(), roi.getRegionHigh())]
		self.setExtraNames(extraNames)
		self.numRoi = len(extraNames)
		self.setOutputFormat(['%.3f'] + ['%.0f']*self.numRoi)

	def getRoi(self):
		self.configure()
		return self.rois

	def __str__(self):
		self.configure()
		grosscounts = self.__getGrossCounts()
		netcounts = self.__getNetCounts()
		toReturn = ''
		toReturn+= "livetime = " + str(self.mca.getPresets().getPresetLiveTime()) + "s\n"

		toReturn+= "----------------------------------------\n"
		toReturn+= "ch label    low  high gross    net      \n"
		toReturn+= "----------------------------------------\n"
		for roi in self.rois:
			toReturn+= "%-2d %-8s %-4d %-4d %-8d %-8d\n" % (roi.index, roi.label, roi.low, roi.high, grosscounts[roi.index], netcounts[roi.index],)
		toReturn+= "-------------------------------------------------\n"
		toReturn+= "Returns " + self.countType + " count in scans\n"
		return toReturn


