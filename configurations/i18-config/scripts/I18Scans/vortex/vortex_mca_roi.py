from java.lang import *
from jarray import *
from time import sleep
		
#
# Modified Vortex MCA
# MCA is a slave as it requires external hardware trigger to collect data
#
class SlaveVortexMca:
	def __init__(self):
		name='vortex_roi'
		xmap = "BL18I-EA-DET-04:XMAP0"
		mca = xmap + ":MCA"
		mcaRecords = [xmap+":0:MCA", xmap+":1:MCA", xmap+":2:MCA", xmap+":3:MCA"]
		# individual ROI sums
		self.roi_sum=[]
		for record in mcaRecords:
			self.roi_sum.append(CAClient(record+".R0"))
			self.roi_sum[-1].configure()
		# Acquire status PROC PV
		self.xmap_statPROC=CAClient(xmap+":MCA:STAT.PROC")
		self.xmap_statPROC.configure()
		# Read PROC PV
		self.xmap_readPROC=CAClient(xmap+":MCA:READ.PROC")
		self.xmap_readPROC.configure()
		# Scan Stats PV
		self.xmap_statSCAN=CAClient(xmap+":MCA:STAT.SCAN")
		self.xmap_statSCAN.configure()
		# Stop PV
		self.xmap_stop=CAClient(xmap+":MCA:STOP")
		self.xmap_stop.configure()
		# Erase Start PV
		self.xmap_eraseStart=CAClient(xmap+":MCA:ERST")
		self.xmap_eraseStart.configure()
		self.das=finder.find("daserver")

	#
	# get ROI sums
	#
	def getROISums(self):
		sumroi=0
		for roi in self.roi_sum:
			sumroi=sumroi+float(roi.caget())
		return sumroi

	#
	# get ROI sums
	#
	def getROICounts(self):
		roicounts=[]
		for roi in self.roi_sum:
			roicounts.append(float(roi.caget()))
		return roicounts
		
	def getPosition(self):
		return self.getROICounts()

	def updateStatus(self):
		self.xmap_statPROC.caput(1)
		self.xmap_readPROC.caput(1)

	# Stop and Erase and start
	def stopEraseAndStart(self):
		# stop
		self.xmap_stop.caput(1)
		# erase and start
		self.xmap_eraseStart.caput(1)

	# Stop and Erase and start
	def stop(self):
		# stop
		self.xmap_stop.caput(1)

	def collectMCA(self,collectionTime=1000.0):
		self.stop()
		self.stopEraseAndStart()
		self.das.sendCommand("tfg init")
		command = "tfg setup-groups cycles 1 \n1 0.0 %f 0 3 0 0 \n-1 0 0 0 0 0 0 " %(collectionTime/1000.0)
		self.das.sendCommand(command)
		self.das.sendCommand("tfg start")
		self.das.sendCommand("tfg wait timebar")
		self.stop()		
		
	
vortex_mca=SlaveVortexMca()

