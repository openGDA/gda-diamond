from gda.device.scannable import ScannableMotionBase

class McaChannel( ScannableMotionBase ):
	def __init__(self,name,mca):
		self.mca=mca
		self.setName(name)
		self.newpos=0
		self.maxpos=self.mca.getProperty('.NUSE')
		self.setInputNames(['Counts'])
		self.setOutputFormat(["%.0f"])
		self.needsRead = 1
		
	def atScanStart(self):
		self.mca.read()
		self.mca.wait()
		self.data=self.mca.getData()
		self.maxpos=self.mca.getProperty('.NUSE')
		
	def asynchronousMoveTo(self,newpos):
		if newpos < self.maxpos and newpos >=0:
			self.newpos=int(newpos)
		else:
			print "Error: newpos not correct"
			
	def isBusy(self):
		return 0

	def getPosition(self):
		return int(self.data[self.newpos])
