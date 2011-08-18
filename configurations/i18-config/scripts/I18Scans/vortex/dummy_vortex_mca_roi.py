from java.lang import *
from jarray import *
from time import sleep
import random
		
#
# Modified Vortex MCA
# MCA is a slave as it requires external hardware trigger to collect data
#
class SlaveVortexMca:
	def __init__(self):
		name='vortex_roi'
		xmap = "BL18I-EA-DET-04:XMAP0"
		mca = xmap + ":MCA"
		self.mcaRecords = [xmap+":0:MCA", xmap+":1:MCA", xmap+":2:MCA", xmap+":3:MCA"]
		# individual ROI sums
		self.roi_sum=[]
		self.no_of_roi_per_mca=3
		for roi in range(self.no_of_roi_per_mca):
			for record in self.mcaRecords:
				self.roi_sum.append(record+".R"+str(roi))
				
		# Acquire status PROC PV
		self.xmap_statPROC=CAClient(xmap+":MCA:STAT.PROC")
		# Read PROC PV
		self.xmap_readPROC=CAClient(xmap+":MCA:READ.PROC")
		# Scan Stats PV
		self.xmap_statSCAN=CAClient(xmap+":MCA:STAT.SCAN")
		# Stop PV
		self.xmap_stop=CAClient(xmap+":MCA:STOP")
		# Erase Start PV
		self.xmap_eraseStart=CAClient(xmap+":MCA:ERST")
		
	#
	# get ROI sums
	#
	def getROISums(self):
		sumroi=[0.0]*self.no_of_roi_per_mca
		roi_index=0
		roi_count=len(self.mcaRecords)
		
		for roi in range(self.no_of_roi_per_mca):
			roiCounts = self.getROICounts(roi)
			for roic in roiCounts:
			   	sumroi[roi_index]=sumroi[roi_index]+roic
			roi_index=roi_index+1
		return sumroi

	#
	# get ROI sums
	#
	def getROICounts(self, roiindex="*"):
		roicounts=[]
		loopCount = self.mcaRecords
		if (roiindex== "*") :
			loopCount = self.roi_sum
			
		for roi in loopCount:
			roicounts.append(float(random.randint(0, 100000)))
		return roicounts
		
	def getPosition(self):
		return self.getROICounts()

	def updateStatus(self):
		pass

	# Stop and Erase and start
	def stopEraseAndStart(self):
		# stop
		pass

	# Stop and Erase and start
	def stop(self):
		pass

	def collectMCA(self,collectionTime=1000.0):
		self.stop()
		self.stopEraseAndStart()
		#self.das.sendCommand("tfg init")
		#command = "tfg setup-groups cycles 1 \n1 0.0 %f 0 3 0 0 \n-1 0 0 0 0 0 0 " %(collectionTime/1000.0)
		#self.das.sendCommand(command)
		#self.das.sendCommand("tfg start")
		#self.das.sendCommand("tfg wait timebar")
		time.sleep(collectionTime/1000.0)
		self.stop()		
		
	def getData(self):
		data=[]
		for d in self.mcaRecords:
			dtemp = []
			for i in range(4095):
				dtemp.append(random.randint(0,10000))
			data.append(dtemp)
		return data
vortex_mca=SlaveVortexMca()
