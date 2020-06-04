
from time import sleep;
#import math;
import jarray;

from gda.device.detector import DetectorBase;
from gda.device.Detector import BUSY, IDLE;
from gda.epics import CAClient;


class StructMcaGdaClass(DetectorBase):
	"""
	Designed to work closely within cvscan. All required EMCS methods are
	passed trhough to the raw EMCS. After a collection has been made and
	the EMCS stopped, calling prepareResults() will ready this scannable
	to be scanned (in a dummy way) to return the results.
	
	
	Calling prepareResults() will retrieve data from the EMCS, and put a pointer
	to the first bin. Each succesive call to getPosition will return a line
	counts for the configured channels.
	
	"""

	def __init__(self, name, mca):
		'''channelList starts at 1, but the first channel is always added
		anyway as this is the time'''
		if 1 in channelList:
			raise Exception("Do not select channel 1. This is reserved for reading back the bin time.")
		self.name = name
		self.mca = mcs
		self.channelList = channelList
		if nameList==None:
			nameList=[]
			for i in range(len(channelList)):
				nameList += ["ch" + str(channelList[i])]
		self.setExtraNames(['tbin'] + nameList)
		self.setInputNames([])
		self.setOutputFormat(['%.6f'] + ['%d']*len(channelList))
		self.setLevel(7);

	def isBusy(self):
		return False

	def getPosition(self):
		bin = self.results[self.aboutToReturnBin]
		self.aboutToReturnBin += 1
		return bin

###

	def prepareResults(self, nbins):
		self.results=[]
		self.results.append(map(lambda x: x/50e6,self.mca.getData(0)[0:nbins])) # get the ch1 time counts
		for channel in self.channelList:
			self.results.append(self.mca.getData(channel-1)[0:nbins])
		# now transpose to get nbins rows of channel counts
		self.results=apply(zip,self.results)
		self.aboutToReturnBin = 0

###
###=========================
# DetectorBase Implementation
	def prepareForCollection(self):
		return self.mca.prepareForCollection()

	def collectData(self):
		return self.mca.collectData()
	
	def stop(self):
		return self.mca.stop()

	def asynchronousMoveTo(self,newExpos):
		self.mca.setCollectionTime(newExpos)
		self.mca.collectData();

	def getCollectionTime(self):
		return self.mca.getCollectionTime();

	def setCollectionTime(self, newExpos):
		self.mca.setCollectionTime(newExpos);

	def readout(self):
		return self.scaler.readout();

	def getStatus(self):
		return self.scaler.getStatus();
	
	def createsOwnFiles(self):
		return False;
	
	def toString(self):
		return self.getName() + ": Integration= " + str(self.getCollectionTime()) + ", Count=" + str(self.getPosition());
	



#mca=StructMcaGdaClass('mca', mcs, [2,3,4],['ch2','ch3','ch4'])
# To use:
# cvscan kth start stop step mcsw time_per_bin

#pvRootScaler   = "BL07I-EA-ADC-01";

#ionsc = AdcScalerClass('ionsc', pvRootScaler);
#ionsc1 = AdcScalerChannelClass('ionsc1', pvRootScaler, channel=0);
#ionsc1.setUsedByDefault(False);


# BL07I-EA-DET-01:SCALER.CNT     Done 
#BL07I-EA-DET-01:SCALER.S1      9.61967e+06 
#BL07I-EA-DET-01:SCALER.TP      4 
#BL07I-EA-DET-01:SCALER.CONT    AutoCount 

eh1mca = StructMcaGdaClass("eh1mca", mca1);
eh1mca1 = StructMcaGdaChannelClass("eh1mca1", mca1, 0);
eh1mca2 = StructMcaGdaChannelClass("eh1mca2", mca1, 1);

