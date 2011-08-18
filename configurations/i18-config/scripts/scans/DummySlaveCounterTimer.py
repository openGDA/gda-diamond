from jarray import *
from time import sleep

#
#
# Represents a Tfg and EpicsMCA acting as a CounterTimer combination. Since the
# Tfg will generally also be part of a TfgScaler combination there is a slave
# mode. In this mode methods which set things on the Tfg do nothing.
#
# 
class DummySlaveCounterTimer:

	def __init__(self):
		self.max_frames=256
		self.NUMBER_OF_ROIS = 1		
		self.nchannels = 3
		self.collectionTime = 1.0
		self.busy =0

	#
	# Normal set collection time
	#
	def setCollectionTime(self,collectionTime):
		self.collectionTime = collectionTime

	#
	# normal collect using roi
	# 
	def collectData(self):
		self.busy =1
		values=[]
		print self.collectionTime
		sleep(self.collectionTime/1000.0)
		#values[0] = 1000.0
		#values[1] = 2000.0
		#values[2] = 3000.0
		self.busy =0
		return [1000,2000,3000]	

	#
	# Clear and prepare adc
	#
	def clearAndPrepare(self):
		# Do nothing for Dummy.
		return
				
	def isBusy(self):
		return self.busy
		
